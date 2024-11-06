from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()

#  User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Interger, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    # One to many relationship, User can create multiple playlists, Table user related to playlist table 
    playlists = db.relationship('Playlist', backref='user', lazy=True)

# Artist Table
class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    bio = db.Column(db.Text)

    # One to many relationship, Artist can create multiple albums, Table artist related to albums table
    albums = db.relationship('Album', backref='artist', lazy=True)
    # One to many relationship, An artist can be associated with multiple genres. Table artist related to genre table
    genres = db.relationship('Genre', secondary='artist_genre', backref=db.backref('artists', lazy='dynamic'))

# Album Table
class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    # one to many relationship, Album can contain multiple songs, Table album related to songs table
    songs = db.relationship('Song', secondary='album_songs', backref=db.backref('albums', lazy='dynamic'))

# Genre Table
class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    # one to many relationship, Genre can categorize multiple songs, Table genre related to songs table
    songs = db.relationship('Song', backref='genre', lazy=True)

# Song table
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    file_path = db.Column(db.Text, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    
    # many to many relationship, playlist can contain multiple songs, and vice versa
    playlists = db.relationship('PlaylistSong', backref='song', lazy=True)

# Playlist Table
class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)

# PlaylistSong Table
class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)








    