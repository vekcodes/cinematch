# CineMatch — Movie Recommendation System

A full-stack movie recommendation engine built in **pure Python** (only
Flask is an external dependency — everything else uses the standard
library) with a custom **HTML/CSS/JS** front end. It implements three
classic recommendation strategies side by side so you can see how each
one works and compare their results on the same catalogue.

> **Note on implementation:** TF-IDF, cosine similarity, and the
> collaborative-filtering rating prediction are all hand-written in
> `recommender.py` from the underlying math — no numpy, pandas, or
> scikit-learn. This keeps the project lightweight (installs in
> seconds, runs on any machine) and means every formula in section 2
> below is real code you can point to, not a library call.

---

## 1. Project plan (step by step)

| Step | What | File(s) |
|---|---|---|
| 1 | Define the problem & choose algorithms | this README |
| 2 | Generate a synthetic dataset (movies + user ratings) | `data/generate_data.py` |
| 3 | Build **Content-Based Filtering** (hand-coded TF-IDF + Cosine Similarity) | `recommender.py` → `ContentBasedRecommender` |
| 4 | Build **Collaborative Filtering** (sparse user–item structure + Cosine Similarity) | `recommender.py` → `CollaborativeFiltering` |
| 5 | Build **Hybrid Recommender** (weighted blend of both) | `recommender.py` → `HybridRecommender` |
| 6 | Expose everything through a REST API | `app.py` |
| 7 | Build the web UI (HTML/CSS/JS) | `templates/index.html`, `static/style.css`, `static/script.js` |
| 8 | Wire the UI to the API and test all three modes | `static/script.js` |
| 9 | Package & document | `requirements.txt`, this `README.md` |

---

## 2. How the algorithms work

### 2.1 Content-Based Filtering — TF-IDF + Cosine Similarity
Every movie is turned into a "soup" of text: `genres + director + cast + overview`
(genres are repeated to weight them more heavily). A **hand-written TF-IDF
step** (`ContentBasedRecommender._vectorize` in `recommender.py`) converts
each soup into a sparse numeric vector where rare, distinctive words score
higher than common ones:

```
tf(t, d)  = count of term t in document d / total terms in d
idf(t)    = ln( (1 + N) / (1 + df(t)) ) + 1        # N = number of movies
tfidf(t,d) = tf(t, d) * idf(t)
```

Similarity between two movies is then the **cosine of the angle** between
their TF-IDF vectors, computed directly with `cosine_similarity_sparse()`:

```
cos(θ) = (A · B) / (‖A‖ ‖B‖)
```

A score near `1.0` means "almost the same content", near `0.0` means
"no shared vocabulary". This powers *"Because you liked X…"* recommendations
and works even for a brand-new movie with zero ratings (no cold-start problem).

### 2.2 Collaborative Filtering — User–Item Matrix + Cosine Similarity
We build a **sparse user × movie rating structure** (`dict` of `dict`s,
so unrated pairs cost nothing to store) from the ratings dataset.

- **Item-based CF**: two movies are similar if they received similar
  ratings across many users (cosine similarity of their rating columns).
- **User-based CF**: two users are similar if they rated movies similarly
  (cosine similarity of their rating rows). To recommend for a user, we
  find their *k* nearest-neighbour users and predict ratings for unseen
  movies as a similarity-weighted average:

```
predicted(u, i) = Σ_v [ sim(u, v) · rating(v, i) ] / Σ_v |sim(u, v)|
```

This captures patterns content alone can't ("people with your taste also
loved this obscure film"), but needs enough rating history to work well.

### 2.3 Hybrid Recommender
Combines both signals with a tunable weight `alpha`:

```
hybrid_score = alpha · content_score + (1 − alpha) · collaborative_score
```

`alpha → 1` leans on content (safer for niche/new movies), `alpha → 0`
leans on the crowd's collaborative signal. The UI exposes this as the
**blend slider**.

---

## 3. Project structure

```
movie_recommendation_system/
├── app.py                  # Flask server + REST API
├── recommender.py          # All 3 algorithms (content, collaborative, hybrid)
├── requirements.txt
├── data/
│   ├── generate_data.py    # Builds the synthetic dataset
│   ├── movies.csv          # 50 movies (title, genres, director, cast, overview)
│   └── ratings.csv         # 45 synthetic users × ratings
├── templates/
│   └── index.html          # Main UI page (Flask/Jinja2 template)
└── static/
    ├── style.css            # Design system (dark cinema theme)
    └── script.js             # Tab switching, API calls, result rendering
```

---

## 4. Running it locally

```bash
cd movie_recommendation_system
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# (optional) regenerate the dataset
python data/generate_data.py

python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 5. Using the app

1. Pick an **algorithm tab**: Content-Based, Collaborative, or Hybrid.
2. Content-Based / Hybrid → choose a **seed movie** you like.
   Collaborative → choose a **viewer profile** (`User #1`…`User #45`).
   Hybrid → also drag the **blend slider** between content and collaborative.
3. Click **Generate recommendations**.
4. Each result card shows the movie, its genres, and a "match meter" bar
   with the raw similarity/prediction score behind the ranking.

## 6. REST API reference

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `/api/movies` | – | List all movies |
| GET | `/api/users` | – | List all synthetic user ids |
| GET | `/api/movie/<id>/ratings` | – | Rating count/average for one movie |
| POST | `/api/recommend` | `{mode, title, user_id, alpha, top_n}` | Run a recommender (`mode` = `content` \| `collaborative` \| `hybrid`) |

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"mode": "hybrid", "title": "Galaxy Horizon", "alpha": 0.6, "top_n": 5}'
```

## 7. Extending this project

- Swap the synthetic CSVs for the real **MovieLens** dataset for production-grade results.
- Add **matrix factorization** (SVD / ALS) as a 4th algorithm for sparse, large-scale rating data.
- Add real poster images via an external movie API and cache them.
- Persist the trained TF-IDF/CF models to disk instead of rebuilding on every server start.
- Add user authentication so real users can rate movies and get personalized results.
