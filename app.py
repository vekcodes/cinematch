from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Movie, Rating
from recommender import ContentBasedRecommender, CollaborativeFiltering
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cine_match.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'

recommenders = {}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables initialized")

@app.before_request
def initialize():
    global recommenders
    with app.app_context():
        if not recommenders:
            build_recommenders()

def build_recommenders():
    global recommenders
    try:
        movies = Movie.query.all()
        if not movies:
            recommenders = {}
            return

        movie_dict = {}
        for m in movies:
            movie_dict[m.id] = {
                'title': m.title,
                'genres': m.genres or '',
                'director': m.director or '',
                'cast': m.cast or '',
                'overview': m.overview or ''
            }

        ratings_dict = {}
        for r in Rating.query.all():
            if r.user_id not in ratings_dict:
                ratings_dict[r.user_id] = {}
            ratings_dict[r.user_id][r.movie_id] = r.rating

        recommenders = {
            'content': ContentBasedRecommender(movie_dict),
            'collaborative': CollaborativeFiltering(ratings_dict),
            'movie_dict': movie_dict
        }
    except Exception as e:
        print(f"Error building recommenders: {e}")
        recommenders = {}

# Authentication Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify({'success': True, 'message': 'Signup successful'}), 201

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        return jsonify({'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Main App Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rated_movies = [(r.movie_id, r.rating) for r in user_ratings]
    return render_template('profile.html', user=current_user, rated_movies=rated_movies)

# API Routes
@app.route('/api/movies')
@login_required
def get_movies():
    movies = Movie.query.all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'genres': m.genres,
        'director': m.director,
        'cast': m.cast,
        'overview': m.overview,
        'poster_url': m.poster_url,
        'release_date': m.release_date,
        'rating_avg': m.rating_avg
    } for m in movies])

@app.route('/api/tmdb/search', methods=['POST'])
@login_required
def search_tmdb():
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB API key not configured'}), 500

    data = request.json
    query = data.get('query', '')

    try:
        response = requests.get(
            f'{TMDB_BASE_URL}/search/movie',
            params={'api_key': TMDB_API_KEY, 'query': query}
        )
        results = response.json().get('results', [])

        formatted = []
        for r in results[:10]:
            formatted.append({
                'tmdb_id': r['id'],
                'title': r['title'],
                'overview': r.get('overview', ''),
                'poster_url': f"{TMDB_IMAGE_BASE}{r['poster_path']}" if r.get('poster_path') else '',
                'release_date': r.get('release_date', '')
            })

        return jsonify(formatted)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tmdb/details/<int:tmdb_id>', methods=['GET'])
@login_required
def get_tmdb_details(tmdb_id):
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB API key not configured'}), 500

    try:
        movie_res = requests.get(
            f'{TMDB_BASE_URL}/movie/{tmdb_id}',
            params={'api_key': TMDB_API_KEY}
        )
        movie = movie_res.json()

        credits_res = requests.get(
            f'{TMDB_BASE_URL}/movie/{tmdb_id}/credits',
            params={'api_key': TMDB_API_KEY}
        )
        credits = credits_res.json()

        genres = ', '.join([g['name'] for g in movie.get('genres', [])])
        director = next((p['name'] for p in credits.get('crew', []) if p['job'] == 'Director'), '')
        cast = ', '.join([p['name'] for p in credits.get('cast', [])[:5]])

        return jsonify({
            'title': movie['title'],
            'genres': genres,
            'director': director,
            'cast': cast,
            'overview': movie.get('overview', ''),
            'poster_url': f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get('poster_path') else '',
            'release_date': movie.get('release_date', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies', methods=['POST'])
@login_required
def add_movie():
    try:
        data = request.json

        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        # Check for duplicates by title (more practical than tmdb_id)
        existing = Movie.query.filter_by(title=data.get('title')).first()
        if existing:
            return jsonify({'error': f'Movie "{data["title"]}" already in database'}), 400

        movie = Movie(
            title=data['title'],
            genres=data.get('genres', ''),
            director=data.get('director', ''),
            cast=data.get('cast', ''),
            overview=data.get('overview', ''),
            poster_url=data.get('poster_url', ''),
            tmdb_id=data.get('tmdb_id'),
            release_date=data.get('release_date', ''),
            added_by=current_user.id
        )

        db.session.add(movie)
        db.session.commit()

        print(f"✅ Movie added: {movie.title} (ID: {movie.id})")

        build_recommenders()

        return jsonify({
            'id': movie.id,
            'title': movie.title,
            'message': 'Movie added successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding movie: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/rate', methods=['POST'])
@login_required
def rate_movie():
    data = request.json
    movie_id = data.get('movie_id')
    rating_value = float(data.get('rating', 0))

    if rating_value < 0 or rating_value > 5:
        return jsonify({'error': 'Rating must be 0-5'}), 400

    rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if rating:
        rating.rating = rating_value
    else:
        rating = Rating(user_id=current_user.id, movie_id=movie_id, rating=rating_value)
        db.session.add(rating)

    db.session.commit()

    movie = Movie.query.get(movie_id)
    avg_rating = db.session.query(db.func.avg(Rating.rating)).filter_by(movie_id=movie_id).scalar() or 0
    movie.rating_avg = round(avg_rating, 1)
    db.session.commit()

    build_recommenders()

    return jsonify({'success': True}), 200

@app.route('/api/recommend', methods=['POST'])
@login_required
def recommend():
    if not recommenders:
        return jsonify({'error': 'Not enough data for recommendations'}), 400

    data = request.json
    mode = data.get('mode', 'hybrid')
    movie_id = data.get('movie_id')
    alpha = float(data.get('alpha', 0.5))
    top_n = data.get('top_n', 10)

    user_ratings = {r.movie_id: r.rating for r in Rating.query.filter_by(user_id=current_user.id).all()}
    movie_dict = recommenders.get('movie_dict', {})

    try:
        if mode == 'content' and movie_id:
            movie = Movie.query.get(movie_id)
            recs = recommenders['content'].recommend(movie.title, top_n=top_n)
            rec_movies = [(Movie.query.get(mid), score) for mid, score in recs if mid in movie_dict]
        elif mode == 'collaborative':
            recs = recommenders['collaborative'].recommend(current_user.id, top_n=top_n)
            rec_movies = [(Movie.query.get(mid), score) for mid, score in recs if mid in movie_dict]
        elif mode == 'hybrid':
            if movie_id:
                movie = Movie.query.get(movie_id)
                content_recs = recommenders['content'].recommend(movie.title, top_n=50)
                content_scores = {mid: score for mid, score in content_recs}
            else:
                content_scores = {}

            collab_recs = recommenders['collaborative'].recommend(current_user.id, top_n=50)
            collab_scores = {mid: score for mid, score in collab_recs}

            all_movies = set(content_scores.keys()) | set(collab_scores.keys())
            hybrid_scores = {}
            for mid in all_movies:
                c = content_scores.get(mid, 0)
                col = collab_scores.get(mid, 0)
                hybrid_scores[mid] = alpha * c + (1 - alpha) * col

            rec_movies = [(Movie.query.get(mid), score) for mid, score in sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]]
        else:
            return jsonify({'error': 'Invalid mode'}), 400

        results = []
        for movie, score in rec_movies:
            if movie:
                results.append({
                    'id': movie.id,
                    'title': movie.title,
                    'genres': movie.genres,
                    'director': movie.director,
                    'poster_url': movie.poster_url,
                    'overview': movie.overview,
                    'score': round(score, 3),
                    'user_rating': user_ratings.get(movie.id)
                })

        return jsonify({'results': results, 'mode': mode})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
