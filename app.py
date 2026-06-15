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


# ── SQLite local database handler ─────────────────────────────────────────────
import database.sqlite_handler as sqlite

# ══════════════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Home page – movie search with featured movies grid and watchlist."""
    featured = recommender.get_random_movies(n=12)
    watchlist_titles = sqlite.get_watchlist()
    
    # Hydrate watchlist details
    watchlist_movies = []
    for title in watchlist_titles:
        details = recommender.get_movie_details(title)
        if details:
            watchlist_movies.append(details)
            
    # Personalized recommendations based on watchlist
    personalized_recs = []
    if watchlist_titles:
        personalized_recs = recommender.get_profile_recommendations(watchlist_titles, n=6)
        
    return render_template(
        "index.html",
        featured_movies=featured,
        watchlist=watchlist_movies,
        personalized_recs=personalized_recs
    )


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
    
    # Retrieve local ratings/reviews
    reviews = sqlite.get_reviews(movie_title)
    avg_user_rating = sqlite.get_average_rating(movie_title)
    is_watchlisted = sqlite.is_in_watchlist(movie_title)

    recommendations = []
    if movie:
        recommendations = recommender.get_recommendations(movie_title, n=10)
        # Compute explanations for recommendations
        for r in recommendations:
            r["explanation"] = recommender.get_recommendation_explanation(movie_title, r["title"])

        # Log to MongoDB (if available)
        if mongo:
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
        reviews=reviews,
        avg_user_rating=avg_user_rating,
        is_watchlisted=is_watchlisted
    )


@app.route("/watchlist/add", methods=["POST"])
def add_to_watchlist():
    """Add a movie to the local watchlist."""
    movie_title = request.form.get("movie_title", "").strip()
    if not movie_title:
        return jsonify({"success": False, "error": "No movie title provided"}), 400
    
    success = sqlite.add_to_watchlist(movie_title)
    return jsonify({"success": success})


@app.route("/watchlist/remove", methods=["POST"])
def remove_from_watchlist():
    """Remove a movie from the local watchlist."""
    movie_title = request.form.get("movie_title", "").strip()
    if not movie_title:
        return jsonify({"success": False, "error": "No movie title provided"}), 400
    
    success = sqlite.remove_from_watchlist(movie_title)
    return jsonify({"success": success})


@app.route("/review/add", methods=["POST"])
def add_review():
    """Add a review for a movie."""
    movie_title = request.form.get("movie_title", "").strip()
    username = request.form.get("username", "Anonymous").strip() or "Anonymous"
    rating = request.form.get("rating", type=int)
    review_text = request.form.get("review_text", "").strip()

    if not movie_title or not rating:
        return "Invalid parameters", 400

    sqlite.add_review(movie_title, username, rating, review_text)
    return render_template(
        "recommendations.html",
        movie=recommender.get_movie_details(movie_title),
        recommendations=recommender.get_recommendations(movie_title, n=10),
        reviews=sqlite.get_reviews(movie_title),
        avg_user_rating=sqlite.get_average_rating(movie_title),
        is_watchlisted=sqlite.is_in_watchlist(movie_title),
        show_review_anchor=True
    )


@app.route("/api/movies", methods=["GET"])
def api_movies():
    """JSON API – returns list of all movie titles (for autocomplete)."""
    return jsonify({"movies": recommender.get_all_movies()})


@app.route("/api/movies/filter", methods=["GET"])
def api_filter_movies():
    """Advanced search/filter API for movies."""
    df = recommender.df
    if df is None:
        recommender.load_data()
        df = recommender.df

    filtered_df = df.copy()
    if filtered_df.empty:
        return jsonify({"movies": []})

    # 1. Search text query
    q = request.args.get("query", "").strip().lower()
    if q:
        mask = (
            filtered_df["title"].str.lower().str.contains(q) |
            filtered_df["director"].str.lower().str.contains(q) |
            filtered_df["cast"].str.lower().str.contains(q) |
            filtered_df["keywords"].str.lower().str.contains(q)
        )
        filtered_df = filtered_df[mask]
        if filtered_df.empty:
            return jsonify({"movies": []})

    # 2. Genres
    genre_filter = request.args.get("genres", "").strip()
    if genre_filter:
        genres_list = [g.strip().lower() for g in genre_filter.split(",") if g.strip()]
        if genres_list:
            def match_genres(movie_genres_str):
                movie_genres = [g.strip().lower() for g in movie_genres_str.split(",")]
                return any(g in movie_genres for g in genres_list)
            filtered_df = filtered_df[filtered_df["genres"].apply(match_genres)]
            if filtered_df.empty:
                return jsonify({"movies": []})

    # 3. Year Range
    try:
        start_year = int(request.args.get("start_year", 1990))
        end_year = int(request.args.get("end_year", 2026))
        filtered_df = filtered_df[(filtered_df["year"] >= start_year) & (filtered_df["year"] <= end_year)]
        if filtered_df.empty:
            return jsonify({"movies": []})
    except (ValueError, TypeError):
        pass

    # 4. Rating Range
    try:
        min_rating = float(request.args.get("min_rating", 0.0))
        filtered_df = filtered_df[filtered_df["rating"] >= min_rating]
        if filtered_df.empty:
            return jsonify({"movies": []})
    except (ValueError, TypeError):
        pass

    # 5. Sorting
    sort_by = request.args.get("sort_by", "rating")
    if sort_by == "rating":
        filtered_df = filtered_df.sort_values(by="rating", ascending=False)
    elif sort_by == "year":
        filtered_df = filtered_df.sort_values(by="year", ascending=False)
    elif sort_by == "title":
        filtered_df = filtered_df.sort_values(by="title", ascending=True)

    # Convert to JSON records
    results = filtered_df.head(48).to_dict("records")
    return jsonify({"movies": results})


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    logger.info("Starting CineMatch on http://127.0.0.1:%d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
