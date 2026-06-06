"""
MongoDB Handler – Optional persistence layer for the Movie Recommendation System.
Gracefully degrades when MongoDB is unavailable.
"""

import datetime
import logging

logger = logging.getLogger(__name__)


def _get_pymongo():
    """Lazily import pymongo so the rest of the app works without it."""
    try:
        import pymongo  # noqa: F811
        return pymongo
    except ImportError:
        return None


class MongoHandler:
    """Manages MongoDB operations for movies and recommendation logs.

    Parameters
    ----------
    uri : str
        MongoDB connection string (default ``mongodb://localhost:27017``).
    db_name : str
        Database name (default ``movie_recommendation_db``).
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "movie_recommendation_db",
    ):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connected = False
        self._connect()

    # ── Connection ────────────────────────────────────────────────────────

    def _connect(self):
        """Attempt to connect to MongoDB; set *connected* flag accordingly."""
        pymongo = _get_pymongo()
        if pymongo is None:
            logger.info("pymongo is not installed – MongoDB features disabled.")
            return

        try:
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            # Force a round-trip to verify connectivity
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.connected = True
            logger.info("Connected to MongoDB at %s (db: %s)", self.uri, self.db_name)
        except Exception as exc:
            logger.warning("MongoDB unavailable (%s) – running without database.", exc)
            self.client = None
            self.db = None
            self.connected = False

    # ── Movies collection ─────────────────────────────────────────────────

    def insert_movies(self, movies: list[dict]) -> int:
        """Bulk-insert movie documents. Returns the number inserted."""
        if not self.connected:
            return 0
        try:
            col = self.db["movies"]
            col.drop()  # fresh load each time
            result = col.insert_many(movies)
            logger.info("Inserted %d movies into MongoDB.", len(result.inserted_ids))
            return len(result.inserted_ids)
        except Exception as exc:
            logger.error("Failed to insert movies: %s", exc)
            return 0

    def get_all_movies(self) -> list[dict]:
        """Return all movies from the database."""
        if not self.connected:
            return []
        try:
            return list(self.db["movies"].find({}, {"_id": 0}))
        except Exception as exc:
            logger.error("Failed to fetch movies: %s", exc)
            return []

    def get_movie_by_title(self, title: str) -> dict | None:
        """Return a single movie document by title (case-insensitive)."""
        if not self.connected:
            return None
        try:
            return self.db["movies"].find_one(
                {"title": {"$regex": f"^{title}$", "$options": "i"}},
                {"_id": 0},
            )
        except Exception as exc:
            logger.error("Failed to fetch movie '%s': %s", title, exc)
            return None

    # ── Recommendations log ───────────────────────────────────────────────

    def log_recommendation(
        self,
        source_movie: str,
        recommendations: list[dict],
        user_ip: str | None = None,
    ) -> bool:
        """Log a recommendation event. Returns True on success."""
        if not self.connected:
            return False
        try:
            doc = {
                "source_movie": source_movie,
                "recommendations": [r.get("title", "") for r in recommendations],
                "count": len(recommendations),
                "user_ip": user_ip,
                "timestamp": datetime.datetime.utcnow(),
            }
            self.db["recommendations"].insert_one(doc)
            logger.info("Logged recommendation for '%s'.", source_movie)
            return True
        except Exception as exc:
            logger.error("Failed to log recommendation: %s", exc)
            return False

    def get_recommendation_history(self, limit: int = 50) -> list[dict]:
        """Return the most recent recommendation logs."""
        if not self.connected:
            return []
        try:
            cursor = (
                self.db["recommendations"]
                .find({}, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return list(cursor)
        except Exception as exc:
            logger.error("Failed to fetch recommendation history: %s", exc)
            return []

    # ── Utilities ─────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Return basic database statistics."""
        if not self.connected:
            return {"connected": False}
        try:
            return {
                "connected": True,
                "movies_count": self.db["movies"].count_documents({}),
                "recommendations_count": self.db["recommendations"].count_documents({}),
            }
        except Exception:
            return {"connected": False}

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB connection closed.")


# ── Quick smoke test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    handler = MongoHandler()
    if handler.connected:
        print("[+] MongoDB connected -", handler.get_stats())
    else:
        print("[!] MongoDB not available - app will run without it.")
