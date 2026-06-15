# Movie Recommendation System

A content-based movie recommendation engine built with **Python**, **Flask**, and **Scikit-learn**. The system analyzes movie metadata (genres, cast, directors, plot keywords) using TF-IDF vectorization and cosine similarity to suggest films that match your taste.

---

## Features

| Feature | Description |
|---|---|
| **Content-Based Filtering** | TF-IDF + cosine similarity on combined movie metadata (genres, director, cast, keywords) |
| **Personalized Recommendations** | Dynamic suggestions based on items in your active Watchlist |
| **Advanced Filter & Sort** | Collapsible menu on the home page to filter by genres, release year range, min rating, and keywords; sort by Rating, Year, or Alphabetical |
| **Similarity Match Explainer** | Dynamic badges explaining *why* each movie is suggested (e.g., matching genres, director, or cast) |
| **Local Persistent DB (SQLite)** | Stores user watchlist, movie ratings, and reviews locally; falls back gracefully if MongoDB is disabled |
| **User Reviews & Ratings** | Submit 1-10 star ratings and detailed reviews for any movie |
| **High-Res Genre Posters** | Replaces generic emojis with beautiful, thematic cinematic photography from Unsplash |
| **Autocomplete Search** | Real-time movie title suggestions as you type |
| **Featured Grid** | Random movie showcase on the home page |
| **Model Persistence** | Save / load pre-computed similarity matrices with joblib |
| **MongoDB (Optional)** | Log recommendations and store movies in MongoDB |
| **REST APIs** | endpoints for autocomplete and advanced filtering |

---

## Tech Stack

| Layer          | Technology                                    |
|----------------|-----------------------------------------------|
| **Backend**    | Python 3, Flask                               |
| **ML**         | Scikit-learn (TF-IDF Vectorizer, Cosine Similarity) |
| **Data**       | Pandas, NumPy                                 |
| **Database**   | SQLite (Local persistent DB), MongoDB (Optional) |
| **Frontend**   | HTML5, CSS3, Vanilla JavaScript               |
| **Serialization** | Joblib                                     |

---

## Project Structure

```
movie-recommendation-system/
├── app.py                      # Flask web application
├── model/
│   └── recommender.py          # Recommendation engine (TF-IDF + cosine similarity)
├── data/
│   ├── generate_data.py        # Synthetic dataset generator
│   └── movies.csv              # (generated) Movie dataset
├── database/
│   ├── mongo_handler.py        # MongoDB handler (optional)
│   ├── sqlite_handler.py       # SQLite handler (local watchlist & reviews database)
│   └── cinematch.db            # (generated) Local SQLite database
├── templates/
│   ├── index.html              # Home / search page with filters and watchlist
│   └── recommendations.html    # Results page with explanation badges and reviews
├── static/
│   └── style.css               # Premium cinematic theme
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### 1. Navigate to the project

```bash
cd movie-recommendation-system
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

### Step 1 - Generate the movie dataset

```bash
python data/generate_data.py
```

Creates `data/movies.csv` with 220 realistic movie entries across 10 genres.

### Step 2 - Launch the web app

```bash
python app.py
```

Open **http://127.0.0.1:5002** in your browser.

> **Note:** The recommendation model is built automatically on first launch. Subsequent launches load the cached model from `model/artifacts/`.

---

## How It Works

1. **Data Preparation** - Movie metadata (genres, director, cast, overview, keywords) is combined into a single text feature called *tags*
2. **Vectorization** - Tags are converted to numerical vectors using **TF-IDF** (Term Frequency-Inverse Document Frequency)
3. **Similarity** - **Cosine similarity** is computed between all movie pairs to build a similarity matrix
4. **Recommendation** - For a given movie, the system returns the top-N most similar movies based on their cosine similarity scores

```
Tags -> TF-IDF Vectorizer -> Cosine Similarity Matrix -> Top-N Results
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page with search, featured, watchlist and personalized movies |
| `POST` | `/recommend` | Get recommendations (form: `movie_title`) |
| `GET` | `/recommend?movie_title=...` | Get recommendations (query param) |
| `POST` | `/watchlist/add` | Add a movie to the local watchlist |
| `POST` | `/watchlist/remove` | Remove a movie from the local watchlist |
| `POST` | `/review/add` | Submit a star rating & text comment for a movie |
| `GET` | `/api/movies` | JSON list of all movie titles (for autocomplete) |
| `GET` | `/api/movies/filter` | Search/filter/sort API (returns JSON list) |

---

## Usage

1. Open the web app at `http://127.0.0.1:5002`
2. Search for a movie using the autocomplete search bar
3. Click on a movie or submit the search
4. View recommended movies with similarity scores, ratings, and genres

---

## MongoDB (Optional)

The system works **fully without MongoDB**. To enable database features:

1. Install and start MongoDB locally (`mongodb://localhost:27017`)
2. The app will automatically detect and use MongoDB for:
   - Storing movie data
   - Logging recommendation queries
3. If MongoDB is unavailable, the app gracefully falls back to in-memory operation

---

## License

This project is open source and available under the [MIT License](LICENSE).
