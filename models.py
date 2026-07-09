from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')
    added_movies = db.relationship('Movie', backref='added_by_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genres = db.Column(db.String(200))
    director = db.Column(db.String(200))
    cast = db.Column(db.String(500))
    overview = db.Column(db.Text)
    poster_url = db.Column(db.String(500))
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)
    release_date = db.Column(db.String(20))
    rating_avg = db.Column(db.Float, default=0.0)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ratings = db.relationship('Rating', backref='movie', lazy=True, cascade='all, delete-orphan')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie'),)
