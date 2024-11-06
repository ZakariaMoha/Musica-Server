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

    # One to many relationship, User can create multiple playlists, Table user related to playlist table 
    playlists = db.relationship('Playlist', backref='user', lazy=True)

# Artist Table
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    bio = db.Column(db.Text)

    # One to many relationship, Artist can create multiple albums, Table artist related to albums table
    albums = db.relationship('Album', backref='artist', lazy=True)
    # One to many relationship, An artist can be associated with multiple genres. Table artist related to genre table
    genres = db.relationship('Genre', secondary='artist_genre', backref=db.backref('artists', lazy='dynamic'))





    