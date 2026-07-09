# CineMatch - Netflix-Style Movie Recommendation System

## 🎬 Overview

A full-stack movie recommendation platform with user authentication, real movie data from TMDB, and three recommendation algorithms (Content-Based, Collaborative, Hybrid).

**Key Features:**
- ✅ User login/signup system with SQLite database
- ✅ Search & add movies from TMDB API (with real posters)
- ✅ Rate movies and get personalized recommendations
- ✅ Netflix-style grid UI with movie posters
- ✅ Three recommendation algorithms working together
- ✅ User profiles with rating history

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **TMDB API Key** (free registration)
3. All dependencies in `requirements.txt`

---

## 🚀 Quick Start

### Step 1: Get TMDB API Key (2 minutes)

1. Visit: https://www.themoviedb.org/settings/api
2. Create a free account
3. Go to Account Settings → API
4. Click "Create" under API Key (v3 auth)
5. Accept terms and Create
6. Copy your **API Key**

### Step 2: Set Up Environment

```bash
cd "/Users/bivek/Documents/Final year proj/Nishan"

# Create .env file
cat > .env << 'EOF'
TMDB_API_KEY=YOUR_API_KEY_HERE
SECRET_KEY=change-me-in-production
EOF
```

Replace `YOUR_API_KEY_HERE` with your actual TMDB API key from Step 1.

### Step 3: Activate Virtual Environment & Run

```bash
source venv/bin/activate
python3 app.py
```

### Step 4: Open in Browser

```
http://127.0.0.1:5000
```

---

## 📝 First Steps

### 1. Create Account
- Click "Sign up" → Enter username, email, password
- Your account is saved in the SQLite database

### 2. Add Movies
Two options:

**Option A: Search TMDB (Recommended)**
- Click "+ Add Movie"
- Type a movie name (e.g., "Inception")
- Select from results → auto-fills metadata & poster
- Click "Add Movie"

**Option B: Add Manually**
- Click "+ Add Movie" → "Add Manually" tab
- Fill in title, genres, director, cast, overview, poster URL
- Click "Add Movie"

### 3. Rate Movies
- Click on any movie poster to open details
- Click ⭐ stars to rate (0-5)
- Your rating is saved

### 4. Get Recommendations

**Based on Your Taste (Collaborative)**
- Click "Get Recommendations"
- Select "Based on Your Taste"
- Click "Get Recommendations"
- See movies users like you enjoyed!

**Similar to a Movie (Content-Based)**
- Click "Get Recommendations"
- Select "Similar to a Movie"
- Pick a movie you like
- Click "Get Recommendations"
- See movies with similar genres/cast/themes

**Hybrid (Balanced)**
- Click "Get Recommendations"
- Select "Hybrid"
- Pick a movie (optional)
- Adjust the blend slider
  - Left (100%): Pure content-based
  - Right (0%): Pure collaborative
- Click "Get Recommendations"

---

## 🗄️ Database Schema

### Users Table
```
id (Primary Key)
username (Unique)
email (Unique)
password_hash (Hashed with Werkzeug)
```

### Movies Table
```
id (Primary Key)
title
genres
director
cast
overview
poster_url
tmdb_id (From TMDB API)
release_date
rating_avg (Calculated from user ratings)
added_by (User ID who added it)
```

### Ratings Table
```
id (Primary Key)
user_id (Foreign Key → Users)
movie_id (Foreign Key → Movies)
rating (1-5 scale)
Unique Constraint: (user_id, movie_id) - each user rates each movie once
```

---

## 🧠 How the Algorithms Work

### Content-Based Filtering
**Goal:** Find movies similar to one you like

**How:**
1. Convert each movie to text vector (genres + director + cast + overview)
2. Calculate TF-IDF scores (rare words weighted higher)
3. Compare using cosine similarity
4. Rank by similarity (0-1 scale)

**Strength:** Works immediately, even for brand-new movies
**Weakness:** Can only recommend similar movies

### Collaborative Filtering
**Goal:** Find what users like you enjoyed

**How:**
1. Build user×movie rating matrix (sparse)
2. Find users with similar rating history (cosine similarity)
3. Predict: "User A + User B similar → User A should like User B's movies"
4. Weight predictions by how similar the users are

**Strength:** Discovers hidden gems & unexpected recommendations
**Weakness:** Needs users to rate movies first (cold-start)

### Hybrid
**Goal:** Combine both signals with tunable weight

**Formula:**
```
score = alpha × content_score + (1-alpha) × collaborative_score

alpha=1.0  → Pure content (safe, predictable)
alpha=0.5  → Balanced
alpha=0.0  → Pure collaborative (crowd wisdom)
```

---

## 🔑 API Endpoints

### Authentication
```
POST   /signup              Create account
POST   /login               Login
GET    /logout              Logout
```

### Movies
```
GET    /api/movies          Get all movies
POST   /api/movies          Add new movie
GET    /api/tmdb/search     Search TMDB
GET    /api/tmdb/details/:id Get movie details from TMDB
```

### Ratings & Recommendations
```
POST   /api/rate            Rate a movie
POST   /api/recommend       Get recommendations
```

### Examples:

**Search TMDB:**
```bash
curl -X POST http://127.0.0.1:5000/api/tmdb/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Inception"}'
```

**Rate a Movie:**
```bash
curl -X POST http://127.0.0.1:5000/api/rate \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 5, "rating": 4.5}'
```

**Get Recommendations:**
```bash
curl -X POST http://127.0.0.1:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "content",
    "movie_id": 5,
    "top_n": 10
  }'
```

---

## 📂 Project Structure

```
Nishan/
├── app.py                          # Flask app + all routes
├── models.py                       # Database models (User, Movie, Rating)
├── recommender.py                  # Recommendation algorithms
├── requirements.txt                # Dependencies
├── .env                            # Environment variables (create this!)
├── cine_match.db                   # SQLite database (auto-created)
├── templates/
│   ├── login.html                  # Login page
│   ├── signup.html                 # Signup page
│   ├── index.html                  # Main app (Netflix-style grid)
│   └── profile.html                # User profile & ratings
└── static/
    ├── auth.css                    # Login/signup styling
    ├── netflix.css                 # Main app styling
    └── netflix.js                  # All frontend logic
```

---

## 🐛 Troubleshooting

### "TMDB API key not configured"
→ Create `.env` file with your TMDB API key

### "ImportError: No module named 'flask_sqlalchemy'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Address already in use"
Another process is on port 5000. Either:
- Kill it: `lsof -i :5000` then `kill -9 <PID>`
- Use a different port: `python3 app.py --port 5001`

### Blank page loads
Check browser console (F12) for errors. Check terminal for Flask errors.

### Movies don't show posters
- TMDB posters didn't load (slow internet?) → refresh page
- Invalid poster URL → use "Add Manually" and provide valid URL
- Movie added before TMDB integration → delete & re-add

---

## 🎓 Learning Points

This project teaches:

1. **Database Design**
   - User authentication (password hashing)
   - Relational schema (foreign keys, constraints)
   - SQLAlchemy ORM

2. **Recommendation Systems**
   - TF-IDF vectorization (hand-coded)
   - Cosine similarity metrics
   - Collaborative filtering (user-based)
   - Hybrid approaches

3. **Web Architecture**
   - REST API design
   - Form data validation
   - Session management
   - CORS & security basics

4. **Frontend Development**
   - Responsive grid layouts
   - Modal windows
   - API integration (fetch)
   - Dynamic DOM manipulation

5. **Third-Party API Integration**
   - TMDB API usage
   - Error handling
   - Rate limiting awareness

---

## 🚀 Future Enhancements

- **Add Features:**
  - Watchlist (save for later)
  - User following (see friends' ratings)
  - Search/filter movies
  - Movie reviews & comments
  - Trending section

- **Improve Algorithms:**
  - Matrix factorization (SVD/NMF)
  - Deep learning embeddings
  - Temporal dynamics (movie freshness)
  - Genre-specific models

- **Production Ready:**
  - PostgreSQL instead of SQLite
  - Redis caching
  - Celery background jobs
  - Docker containerization
  - CI/CD pipeline

---

## 📖 Resources

- TMDB API Docs: https://developers.themoviedb.org/3
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- Flask-Login: https://flask-login.readthedocs.io/
- Recommender Systems: https://www.coursera.org/learn/recommender-systems

---

## 💡 Tips

1. **Rate multiple movies** to improve collaborative recommendations
2. **Adjust the hybrid slider** to see how different blend weights affect results
3. **Search TMDB** for real movies with posters (better UX than manual adds)
4. **Check profile page** to see all your ratings
5. **Try all three modes** to understand the trade-offs

---

Enjoy your Netflix-style recommendation system! 🎬🍿
