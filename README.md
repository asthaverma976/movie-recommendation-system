# Movie Recommendation System

A content-based movie recommendation engine built with **Python**, **Flask**, and **Scikit-learn**. The system analyzes movie metadata (genres, cast, directors, plot keywords) using TF-IDF vectorization and cosine similarity to suggest films that match your taste.

---

## Features

| Feature | Description |
|---|---|
| **Content-Based Filtering** | TF-IDF + cosine similarity on combined movie metadata |
| **220+ Movies** | Diverse synthetic dataset spanning 10 genres (1990-2024) |
| **Beautiful Web UI** | Premium cinematic dark theme with glassmorphism, animations, and gold accents |
| **Autocomplete Search** | Real-time movie title suggestions as you type |
| **Featured Grid** | Random movie showcase on the home page |
| **Similarity Scores** | Visual percentage match for every recommendation |
| **Star Ratings** | Five-star display for movie ratings |
| **Genre Badges** | Color-coded genre tags |
| **Model Persistence** | Save / load pre-computed similarity matrices with joblib |
| **MongoDB (Optional)** | Log recommendations and store movies in MongoDB |
| **REST API** | `/api/movies` endpoint for programmatic access |

---

## Tech Stack

| Layer          | Technology                                    |
|----------------|-----------------------------------------------|
| **Backend**    | Python 3, Flask                               |
| **ML**         | Scikit-learn (TF-IDF Vectorizer, Cosine Similarity) |
| **Data**       | Pandas, NumPy                                 |
| **Database**   | MongoDB via PyMongo (optional)                |
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
│   └── mongo_handler.py        # MongoDB handler (optional)
├── templates/
│   ├── index.html              # Home / search page
│   └── recommendations.html    # Results page
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
| `GET` | `/` | Home page with search and featured movies |
| `POST` | `/recommend` | Get recommendations (form: `movie_title`) |
| `GET` | `/recommend?movie_title=...` | Get recommendations (query param) |
| `GET` | `/api/movies` | JSON list of all movie titles |

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
