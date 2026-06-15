"""
SQLite Handler – Local persistent storage for user watchlist and movie reviews.
Falls back gracefully if database operations fail.
"""

import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_DB_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_DB_DIR, "cinematch.db")

def init_db():
    """Initialise database connection and create necessary tables."""
    try:
        os.makedirs(_DB_DIR, exist_ok=True)
        conn = sqlite3.connect(_DB_PATH)
        cursor = conn.cursor()
        
        # Create watchlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                movie_title TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT,
                username TEXT,
                rating INTEGER,
                review_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("SQLite database initialised at %s", _DB_PATH)
    except Exception as exc:
        logger.error("Failed to initialise SQLite database: %s", exc)

# Initialize database immediately on module import
init_db()

def _get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Watchlist Operations ──────────────────────────────────────────────

def add_to_watchlist(movie_title: str) -> bool:
    """Add a movie to the user's watchlist. Returns True on success."""
    if not movie_title:
        return False
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO watchlist (movie_title, added_at) VALUES (?, ?)",
            (movie_title.strip(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logger.info("Added '%s' to watchlist.", movie_title)
        return True
    except Exception as exc:
        logger.error("Failed to add '%s' to watchlist: %s", movie_title, exc)
        return False

def remove_from_watchlist(movie_title: str) -> bool:
    """Remove a movie from the user's watchlist. Returns True on success."""
    if not movie_title:
        return False
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM watchlist WHERE LOWER(movie_title) = LOWER(?)",
            (movie_title.strip(),)
        )
        conn.commit()
        conn.close()
        logger.info("Removed '%s' from watchlist.", movie_title)
        return True
    except Exception as exc:
        logger.error("Failed to remove '%s' from watchlist: %s", movie_title, exc)
        return False

def get_watchlist() -> list[str]:
    """Retrieve all movie titles from the watchlist ordered by added_at desc."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT movie_title FROM watchlist ORDER BY added_at DESC")
        rows = cursor.fetchall()
        watchlist = [row["movie_title"] for row in rows]
        conn.close()
        return watchlist
    except Exception as exc:
        logger.error("Failed to fetch watchlist: %s", exc)
        return []

def is_in_watchlist(movie_title: str) -> bool:
    """Check if a movie is in the user's watchlist."""
    if not movie_title:
        return False
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM watchlist WHERE LOWER(movie_title) = LOWER(?)",
            (movie_title.strip(),)
        )
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception as exc:
        logger.error("Failed to check watchlist status for '%s': %s", movie_title, exc)
        return False

# ── Reviews Operations ────────────────────────────────────────────────

def add_review(movie_title: str, username: str, rating: int, review_text: str) -> bool:
    """Submit a rating and review for a movie. Returns True on success."""
    if not movie_title or not username or rating < 1 or rating > 10:
        return False
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reviews (movie_title, username, rating, review_text, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (movie_title.strip(), username.strip(), int(rating), review_text.strip(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        logger.info("Saved review for '%s' by '%s'.", movie_title, username)
        return True
    except Exception as exc:
        logger.error("Failed to add review for '%s' by '%s': %s", movie_title, username, exc)
        return False

def get_reviews(movie_title: str) -> list[dict]:
    """Retrieve all reviews for a movie ordered by created_at desc."""
    if not movie_title:
        return []
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, rating, review_text, created_at FROM reviews WHERE LOWER(movie_title) = LOWER(?) ORDER BY created_at DESC",
            (movie_title.strip(),)
        )
        rows = cursor.fetchall()
        reviews = []
        for row in rows:
            reviews.append({
                "username": row["username"],
                "rating": row["rating"],
                "review_text": row["review_text"],
                "created_at": row["created_at"]
            })
        conn.close()
        return reviews
    except Exception as exc:
        logger.error("Failed to fetch reviews for '%s': %s", movie_title, exc)
        return []

def get_average_rating(movie_title: str) -> float | None:
    """Retrieve the average user star rating for a movie."""
    if not movie_title:
        return None
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT AVG(rating) as avg_rating FROM reviews WHERE LOWER(movie_title) = LOWER(?)",
            (movie_title.strip(),)
        )
        row = cursor.fetchone()
        conn.close()
        if row and row["avg_rating"] is not None:
            return round(float(row["avg_rating"]), 1)
        return None
    except Exception as exc:
        logger.error("Failed to compute average rating for '%s': %s", movie_title, exc)
        return None
