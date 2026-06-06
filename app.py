"""
CineMatch – AI-Powered Movie Recommendation System
Flask web application serving content-based movie recommendations.
"""

import os
import sys
import logging

from flask import Flask, render_template, request, jsonify

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Ensure project root is on sys.path ────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cinematch-secret-key-2024")

# ── Initialise recommendation engine ─────────────────────────────────────────
from model.recommender import MovieRecommender  # noqa: E402

recommender = MovieRecommender()
recommender.initialize()

# ── Optional MongoDB handler ─────────────────────────────────────────────────
mongo = None
try:
    from database.mongo_handler import MongoHandler  # noqa: E402
    mongo = MongoHandler()
    if mongo.connected:
        logger.info("MongoDB connected – logging recommendations to database.")
        # Optionally seed movies into MongoDB
        movies_for_db = recommender.df.to_dict("records") if recommender.df is not None else []
        if movies_for_db:
            mongo.insert_movies(movies_for_db)
    else:
        logger.info("MongoDB not available – running without database.")
        mongo = None
except Exception as exc:
    logger.info("MongoDB disabled (%s) – running without database.", exc)
    mongo = None


# ══════════════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Home page – movie search with featured movies grid."""
    featured = recommender.get_random_movies(n=12)
    return render_template("index.html", featured_movies=featured)


@app.route("/recommend", methods=["POST", "GET"])
def recommend():
    """Show recommendations for the selected movie."""
    movie_title = (
        request.form.get("movie_title", "").strip()
        or request.args.get("movie_title", "").strip()
    )

    if not movie_title:
        return render_template("recommendations.html", movie=None, recommendations=[])

    movie = recommender.get_movie_details(movie_title)
    recommendations = recommender.get_recommendations(movie_title, n=10)

    # Log to MongoDB (if available)
    if mongo and movie:
        try:
            mongo.log_recommendation(
                source_movie=movie_title,
                recommendations=recommendations,
                user_ip=request.remote_addr,
            )
        except Exception as exc:
            logger.warning("Failed to log recommendation to MongoDB: %s", exc)

    return render_template(
        "recommendations.html",
        movie=movie,
        recommendations=recommendations,
    )


@app.route("/api/movies", methods=["GET"])
def api_movies():
    """JSON API – returns list of all movie titles (for autocomplete)."""
    return jsonify({"movies": recommender.get_all_movies()})


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    logger.info("Starting CineMatch on http://127.0.0.1:%d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
