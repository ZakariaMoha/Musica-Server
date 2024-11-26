from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    playlists = db.relationship('Playlist', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Artist Model
class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(500))
    password = db.Column(db.String(100), nullable=False)
    albums = db.relationship('Album', backref='artist', lazy=True)
    genres = db.relationship('Genre', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.name}>'

# Album Model
class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    songs = db.relationship('Song', backref='album', lazy=True)

    def __repr__(self):
        return f'<Album {self.title}>'

# Genre Model
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    songs = db.relationship('Song', backref='genre', lazy=True)

    def __repr__(self):
        return f'<Genre {self.title}>'

# Song Model
class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer)  # Duration in seconds
    file_path = db.Column(db.String(500), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    playlists = db.relationship('PlaylistSong', backref='song', lazy=True)

    def __repr__(self):
        return f'<Song {self.title}>'

# Playlist Model
class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)

    def __repr__(self):
        return f'<Playlist {self.title}>'

# PlaylistSong Model (Join Table for Songs and Playlists)
class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PlaylistSong playlist_id={self.playlist_id}, song_id={self.song_id}>'
