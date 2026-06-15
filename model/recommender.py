"""
Movie Recommendation Engine
Content-based filtering using TF-IDF vectorisation and cosine similarity.
"""

import os
import re
import logging

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Default paths
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE_DIR, "data", "movies.csv")
_MODEL_DIR = os.path.join(_BASE_DIR, "model", "artifacts")


class MovieRecommender:
    """Content-based movie recommender powered by TF-IDF + cosine similarity."""

    def __init__(self, data_path: str | None = None, model_dir: str | None = None):
        self.data_path = data_path or _DATA_PATH
        self.model_dir = model_dir or _MODEL_DIR
        self.df: pd.DataFrame | None = None
        self.similarity_matrix: np.ndarray | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self._title_index: dict[str, int] = {}

    # ── Data loading ──────────────────────────────────────────────────────

    def load_data(self) -> pd.DataFrame:
        """Load movies from CSV. Generates the dataset first if the file is missing."""
        if not os.path.exists(self.data_path):
            logger.info("movies.csv not found – generating synthetic dataset …")
            from data.generate_data import generate_movies, save_to_csv
            movies = generate_movies(220)
            save_to_csv(movies, self.data_path)

        self.df = pd.read_csv(self.data_path)
        self.df.fillna("", inplace=True)
        logger.info("Loaded %d movies from %s", len(self.df), self.data_path)
        return self.df

    # ── Preprocessing ─────────────────────────────────────────────────────

    @staticmethod
    def _clean_text(text: str) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def preprocess(self) -> pd.DataFrame:
        """Combine key columns into a single 'tags' feature for vectorisation."""
        if self.df is None:
            self.load_data()

        self.df["tags"] = (
            self.df["genres"].astype(str) + " " +
            self.df["director"].astype(str) + " " +
            self.df["cast"].astype(str) + " " +
            self.df["overview"].astype(str) + " " +
            self.df["keywords"].astype(str)
        ).apply(self._clean_text)

        # Build a case-insensitive title → index lookup
        self._title_index = {
            title.strip().lower(): idx
            for idx, title in enumerate(self.df["title"])
        }

        logger.info("Preprocessing complete – %d movies ready.", len(self.df))
        return self.df

    # ── Model building ────────────────────────────────────────────────────

    def build_model(self) -> np.ndarray:
        """Vectorise tags with TF-IDF and compute the cosine similarity matrix."""
        if "tags" not in self.df.columns:
            self.preprocess()

        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = self.vectorizer.fit_transform(self.df["tags"])
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        logger.info(
            "Model built – similarity matrix shape: %s", self.similarity_matrix.shape
        )
        return self.similarity_matrix

    # ── Recommendations ───────────────────────────────────────────────────

    def get_recommendations(self, movie_title: str, n: int = 10) -> list[dict]:
        """Return the top-*n* most similar movies to *movie_title*.

        Each result dict contains movie details plus a ``similarity`` score.
        """
        if self.similarity_matrix is None:
            self.build_model()

        key = movie_title.strip().lower()
        idx = self._title_index.get(key)
        if idx is None:
            logger.warning("Movie '%s' not found.", movie_title)
            return []

        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        # Exclude itself (index 0 after sorting will be self with score 1.0)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [s for s in sim_scores if s[0] != idx][:n]

        results = []
        for other_idx, score in sim_scores:
            row = self.df.iloc[other_idx]
            results.append({
                "title": row["title"],
                "genres": row["genres"],
                "director": row["director"],
                "cast": row["cast"],
                "overview": row["overview"],
                "keywords": row["keywords"],
                "rating": float(row["rating"]),
                "year": int(row["year"]),
                "similarity": round(float(score), 4),
            })

        return results

    def get_profile_recommendations(self, movie_titles: list[str], n: int = 10) -> list[dict]:
        """Return the top-*n* recommendation based on a list of profile/watchlist movie titles."""
        if self.similarity_matrix is None:
            self.build_model()

        valid_indices = []
        for title in movie_titles:
            key = title.strip().lower()
            idx = self._title_index.get(key)
            if idx is not None:
                valid_indices.append(idx)

        if not valid_indices:
            # Fall back to random featured movies if no valid profile items
            return self.get_random_movies(n)

        # Average similarity vector across all profile items
        sum_sims = np.zeros(len(self.df))
        for idx in valid_indices:
            sum_sims += self.similarity_matrix[idx]
        sum_sims /= len(valid_indices)

        # Exclude the profile movies themselves from recommendation pool
        for idx in valid_indices:
            sum_sims[idx] = -1.0

        # Sort and select top-n
        top_indices = np.argsort(sum_sims)[::-1][:n]
        
        results = []
        for other_idx in top_indices:
            score = sum_sims[other_idx]
            if score <= 0:
                continue
            row = self.df.iloc[other_idx]
            results.append({
                "title": row["title"],
                "genres": row["genres"],
                "director": row["director"],
                "cast": row["cast"],
                "overview": row["overview"],
                "keywords": row["keywords"],
                "rating": float(row["rating"]),
                "year": int(row["year"]),
                "similarity": round(float(score), 4),
            })
        return results

    def get_recommendation_explanation(self, source_title: str, target_title: str) -> dict:
        """Explain the relationship between the source and target movie."""
        source = self.get_movie_details(source_title)
        target = self.get_movie_details(target_title)
        
        if not source or not target:
            return {"reasons": []}
            
        reasons = []
        
        # 1. Compare genres
        source_genres = {g.strip().lower() for g in source["genres"].split(",") if g.strip()}
        target_genres = {g.strip().lower() for g in target["genres"].split(",") if g.strip()}
        shared_genres = source_genres.intersection(target_genres)
        if shared_genres:
            cased_genres = []
            for g in target["genres"].split(","):
                if g.strip().lower() in shared_genres:
                    cased_genres.append(g.strip())
            if cased_genres:
                reasons.append(f"Similar genre: {', '.join(cased_genres[:2])}")
                
        # 2. Compare director
        if source["director"] and target["director"] and source["director"].strip().lower() == target["director"].strip().lower():
            reasons.append(f"Directed by {source['director']}")
            
        # 3. Compare cast
        source_cast = {c.strip().lower() for c in source["cast"].split(",") if c.strip()}
        target_cast = {c.strip().lower() for c in target["cast"].split(",") if c.strip()}
        shared_cast = source_cast.intersection(target_cast)
        if shared_cast:
            cased_cast = []
            for c in target["cast"].split(","):
                if c.strip().lower() in shared_cast:
                    cased_cast.append(c.strip())
            if cased_cast:
                reasons.append(f"Stars {cased_cast[0]}")
                
        # 4. Compare keywords
        source_kws = {k.strip().lower() for k in source["keywords"].split(",") if k.strip()}
        target_kws = {k.strip().lower() for k in target["keywords"].split(",") if k.strip()}
        shared_kws = source_kws.intersection(target_kws)
        if shared_kws:
            cased_kws = []
            for k in target["keywords"].split(","):
                if k.strip().lower() in shared_kws:
                    cased_kws.append(k.strip())
            if cased_kws:
                reasons.append(f"Similar themes: {', '.join(cased_kws[:2])}")
                
        # If no reasons, default to high similarity score
        if not reasons:
            reasons.append("Highly correlated storyline")
            
        return {
            "shared_genres": list(shared_genres),
            "same_director": source["director"] == target["director"] if source["director"] else False,
            "shared_cast": list(shared_cast),
            "shared_keywords": list(shared_kws),
            "reasons": reasons
        }

    # ── Accessors ─────────────────────────────────────────────────────────

    def get_all_movies(self) -> list[str]:
        """Return a sorted list of all movie titles."""
        if self.df is None:
            self.load_data()
        return sorted(self.df["title"].tolist())

    def get_movie_details(self, title: str) -> dict | None:
        """Return full details for a single movie."""
        if self.df is None:
            self.load_data()
        key = title.strip().lower()
        idx = self._title_index.get(key)
        if idx is None:
            return None
        row = self.df.iloc[idx]
        return {
            "title": row["title"],
            "genres": row["genres"],
            "director": row["director"],
            "cast": row["cast"],
            "overview": row["overview"],
            "keywords": row["keywords"],
            "rating": float(row["rating"]),
            "year": int(row["year"]),
        }

    def get_random_movies(self, n: int = 12) -> list[dict]:
        """Return *n* random movies (for the featured section)."""
        if self.df is None:
            self.load_data()
        sample = self.df.sample(n=min(n, len(self.df)))
        return sample.to_dict("records")

    # ── Persistence ───────────────────────────────────────────────────────

    def save_model(self) -> str:
        """Persist the similarity matrix, vectorizer, DataFrame, and title index."""
        os.makedirs(self.model_dir, exist_ok=True)
        payload = {
            "similarity_matrix": self.similarity_matrix,
            "vectorizer": self.vectorizer,
            "df": self.df,
            "title_index": self._title_index,
        }
        path = os.path.join(self.model_dir, "recommender_model.joblib")
        joblib.dump(payload, path, compress=3)
        logger.info("Model saved to %s", path)
        return path

    def load_model(self) -> bool:
        """Load a previously saved model. Returns True on success."""
        path = os.path.join(self.model_dir, "recommender_model.joblib")
        if not os.path.exists(path):
            logger.info("No saved model found at %s", path)
            return False
        try:
            payload = joblib.load(path)
            self.similarity_matrix = payload["similarity_matrix"]
            self.vectorizer = payload["vectorizer"]
            self.df = payload["df"]
            self._title_index = payload["title_index"]
            logger.info("Model loaded from %s", path)
            return True
        except Exception as exc:
            logger.error("Failed to load model: %s", exc)
            return False

    # ── Convenience initialiser ───────────────────────────────────────────

    def initialize(self) -> None:
        """Full pipeline: try loading a saved model, else build from scratch."""
        if self.load_model():
            return
        self.load_data()
        self.preprocess()
        self.build_model()
        self.save_model()
        logger.info("Recommender initialised (fresh build).")


# ── CLI quick test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rec = MovieRecommender()
    rec.initialize()

    titles = rec.get_all_movies()
    print(f"\nTotal movies: {len(titles)}")
    test_movie = titles[0]
    print(f"\nRecommendations for '{test_movie}':\n")
    for r in rec.get_recommendations(test_movie, n=5):
        print(f"  - {r['title']} ({r['year']}) - {r['similarity']*100:.1f}% match")
