from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()

#  User Table
class User(db.Model):
    id = db.Column(db.Interger, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # One to many relationship, User can create multiple playlists
    playlists = db.relationship('Playlist', backref='user', lazy=True)