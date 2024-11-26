from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Artist, Album, Genre, Song, Playlist, PlaylistSong
from functools import wraps
import os
from flask_jwt_extended import JWTManager, set_access_cookies, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_bcrypt import Bcrypt
from datetime import datetime
from lib.auth import verify_api_key, is_valid_email
from itsdangerous import URLSafeTimedSerializer as Serializer

from dotenv import load_dotenv
load_dotenv()
# CORS(app, supports_credentials=True)
app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI']   = 'sqlite:///MUSICA_DB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['API_KEY'] = os.getenv('API_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_COOKIE_SECURE'] = os.getenv('JWT_COOKIE_SECURE')
app.config['JWT_COOKIE_CSRF_PROTECT'] = os.getenv('JWT_COOKIE_CSRF_PROTECT')
db.init_app(app)
migrate = Migrate(app, db)

# Error handling
def get_or_404(model, id):
    item = model.query.get(id)
    if item is None:
        abort(404, description=f"{model.__name__} not found with id: {id}")
    return item



@app.route('/sign-up/user', methods=['POST'])
@verify_api_key
def create_user():
    """
        Signup for a user 
        : return: 200, 409
    """
    data = request.json

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400
    # check if username and email exists
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Username or email already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    resp = jsonify({'message': 'User registered successfully!', 
                    'username': username,
                    'email':email,
                    'password':hashed_password,
                    'token': access_token})
    set_access_cookies(resp, access_token)
    return resp, 201


# Login user route
@app.route('/login/user', methods=['POST']) 
def login():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Incomplete data'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        resp = jsonify({'message': 'Invalid credentials'})
        return resp, 401

    access_token = create_access_token(identity=username)
    resp = jsonify({
        'username': username,
        'token': access_token
    })
    set_access_cookies(resp, access_token)
    return resp, 200


def generate_token(expiry, username):
    s = Serializer(current_app.config['JWT_SECRET_KEY'], expires_in=expiry)
    return s.dumps({'username': username}).decode('utf-8')


@app.route("/request-password-reset", methods=["POST"])
@verify_api_key
@jwt_required
def request_password_reset():
    """
    Handle forget password logic.
    Generate token for password reset and send to user. 
    Token valid for 1 minute.
    """
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Please provide email"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    token_expiry_time = 60  # Token valid for 1 minute in seconds
    token = generate_token(expiry=token_expiry_time, username=user.email)

    # Mocked email sender
    sent_user_reset_token(recipient=user.email, token=token, name=user.name)

    return jsonify({"message": f"Token sent to your email {email}"}), 200


def sent_user_reset_token(recipient, token, name):
    # Mock email-sending function
    print(f"Sending token {token} to {recipient} for {name}")
# Get all users
@app.route('/all/users', methods=['GET'])
@verify_api_key
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in users])

# Get a specific user by ID
@app.route('/a-user/<int:user_id>', methods=['GET'])
@verify_api_key
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "username": user.username, "email": user.email})

# Update a user
@app.route('/update-user/<int:user_id>', methods=['PUT'])
@verify_api_key
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    db.session.commit()
    return jsonify({"message": "User updated"})

# Delete a user
@app.route('/delete-user/<int:user_id>', methods=['DELETE'])
@verify_api_key
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

# Create a new artist
@app.route('/sign-up/artists', methods=['POST'])
@verify_api_key
def create_artist():
    data = request.get_json()
    new_artist = Artist(name=data['name'], bio=data.get('bio'), password=data.get('password'))
    existing_name = Artist.query.filter_by(name=data['name']).first()
    if existing_name:
        return jsonify({"message": "Artist Name already exists"}), 409
    db.session.add(new_artist)
    db.session.commit()
    return jsonify({"message": "Artist created", "artist": data}), 201

# Get all artists
@app.route('/all/artists', methods=['GET'])
@verify_api_key
def get_artists():
    artists = Artist.query.all()
    return jsonify([{"id": artist.id, "name": artist.name, "bio": artist.bio} for artist in artists])

# Get a specific artist by ID
@app.route('/a-artists/<int:artist_id>', methods=['GET'])
@verify_api_key
def get_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    return jsonify({"id": artist.id, "name": artist.name, "bio": artist.bio})

# Update an artist
@app.route('/update-artist/<int:artist_id>', methods=['PUT'])
@verify_api_key
def update_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    data = request.get_json()
    artist.name = data.get('name', artist.name)
    artist.bio = data.get('bio', artist.bio)
    db.session.commit()
    return jsonify({"message": "Artist updated"})

# Delete an artist
@app.route('/delete-artist/<int:artist_id>', methods=['DELETE'])
@verify_api_key
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    return jsonify({"message": "Artist deleted"})

# CRUD operations for Album
@app.route('/add-album', methods=['POST'])
@verify_api_key
def create_album():
    data = request.get_json()
    new_album = Album(title=data['title'], artist_id=data['artist_id'])
    db.session.add(new_album)
    db.session.commit()
    return jsonify({"message": "Album created", "album": data}), 201

@app.route('/all-albums', methods=['GET'])
@verify_api_key
def get_albums():
    albums = Album.query.all()
    return jsonify([{"id": album.id, "title": album.title, "artist_id": album.artist_id} for album in albums])

@app.route('/a-album/<int:album_id>', methods=['GET'])
@verify_api_key
def get_album(album_id):
    album = Album.query.get_or_404(album_id)
    return jsonify({"id": album.id, "title": album.title, "artist_id": album.artist_id})

@app.route('/update-album/<int:album_id>', methods=['PUT'])
@verify_api_key
def update_album(album_id):
    album = Album.query.get_or_404(album_id)
    data = request.get_json()
    album.title = data.get('title', album.title)
    album.artist_id = data.get('artist_id', album.artist_id)
    db.session.commit()
    return jsonify({"message": "Album updated"})

@app.route('/delete-album/<int:album_id>', methods=['DELETE'])
@verify_api_key
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    return jsonify({"message": "Album deleted"})

# CRUD operations for Song
@app.route('/add-song', methods=['POST'])
@verify_api_key
def create_song():
    data = request.get_json()
    new_song = Song(title=data['title'], duration=data['duration'], file_path=data['file_path'], album_id=data.get('album_id'), genre_id=data.get('genre_id'))
    db.session.add(new_song)
    db.session.commit()
    return jsonify({"message": "Song created", "song": data}), 201

@app.route('/songs', methods=['GET'])
@verify_api_key
def get_songs():
    songs = Song.query.all()
    return jsonify([{"id": song.id, "title": song.title, "duration": song.duration, "file_path": song.file_path} for song in songs])

@app.route('/songs/<int:song_id>', methods=['GET'])
@verify_api_key
def get_song(song_id):
    song = Song.query.get_or_404(song_id)
    return jsonify({"id": song.id, "title": song.title, "duration": song.duration, "file_path": song.file_path})

@app.route('/songs/<int:song_id>', methods=['PUT'])
@verify_api_key
def update_song(song_id):
    song = Song.query.get_or_404(song_id)
    data = request.get_json()
    song.title = data.get('title', song.title)
    song.duration = data.get('duration', song.duration)
    song.file_path = data.get('file_path', song.file_path)
    song.album_id = data.get('album_id', song.album_id)
    song.genre_id = data.get('genre_id', song.genre_id)
    db.session.commit()
    return jsonify({"message": "Song updated"})

@app.route('/songs/<int:song_id>', methods=['DELETE'])
@verify_api_key
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({"message": "Song deleted"})
# Genre Routes (Create, Get, Update, Delete)
@app.route('/add-genre', methods=['POST'])
@verify_api_key
def create_genre():
    data = request.get_json()
    artist = Artist.query.get(data['artist_id'])
    if not artist:
        abort(400, description="Artist not found")
    new_genre = Genre(title=data['title'], artist_id=artist.id)
    db.session.add(new_genre)
    db.session.commit()
    return jsonify({"message": "Genre created", "genre": data}), 201

@app.route('/all/genres', methods=['GET'])
@verify_api_key
def get_genres():
    genres = Genre.query.all()
    return jsonify([{"id": genre.id, "title": genre.title, "artist_id": genre.artist_id} for genre in genres])

@app.route('/a-genre/<int:genre_id>', methods=['GET'])
@verify_api_key
def get_genre(genre_id):
    genre = get_or_404(Genre, genre_id)
    return jsonify({"id": genre.id, "title": genre.title, "artist_id": genre.artist_id})

@app.route('/update-genre/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id):
    genre = get_or_404(Genre, genre_id)
    data = request.get_json()
    genre.title = data.get('title', genre.title)
    genre.artist_id = data.get('artist_id', genre.artist_id)
    db.session.commit()
    return jsonify({"message": "Genre updated"})

@app.route('/delete-genre/<int:genre_id>', methods=['DELETE'])
@verify_api_key
def delete_genre(genre_id):
    genre = get_or_404(Genre, genre_id)
    db.session.delete(genre)
    db.session.commit()
    return jsonify({"message": "Genre deleted"})

# Playlist Routes (Create, Get, Update, Delete)
@app.route('/create-playlist', methods=['POST'])
@verify_api_key
def create_playlist():
    data = request.get_json()
    user = User.query.get(data['user_id'])
    if not user:
        abort(400, description="User not found")
    new_playlist = Playlist(title=data['title'], user_id=user.id)
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify({"message": "Playlist created", "playlist": data}), 201

@app.route('/all/playlists', methods=['GET'])
@verify_api_key
def get_playlists():
    playlists = Playlist.query.all()
    return jsonify([{"id": playlist.id, "title": playlist.title, "user_id": playlist.user_id} for playlist in playlists])

@app.route('/a-playlist/<int:playlist_id>', methods=['GET'])
@verify_api_key
def get_playlist(playlist_id):
    playlist = get_or_404(Playlist, playlist_id)
    return jsonify({"id": playlist.id, "title": playlist.title, "user_id": playlist.user_id})

@app.route('/update-playlist/<int:playlist_id>', methods=['PUT'])
@verify_api_key
def update_playlist(playlist_id):
    playlist = get_or_404(Playlist, playlist_id)
    data = request.get_json()
    playlist.title = data.get('title', playlist.title)
    playlist.user_id = data.get('user_id', playlist.user_id)
    db.session.commit()
    return jsonify({"message": "Playlist updated"})

@app.route('/delete-playlist/<int:playlist_id>', methods=['DELETE'])
@verify_api_key
def delete_playlist(playlist_id):
    playlist = get_or_404(Playlist, playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({"message": "Playlist deleted"})

# PlaylistSong Routes (Create, Get, Delete)
@app.route('/add-song-to-playlist', methods=['POST'])
@verify_api_key
def add_song_to_playlist():
    """
    Adds a song to a specified playlist.

    Expects JSON data with 'playlist_id' and 'song_id'.
    Retrieves the playlist and song from the database.
    If either is not found, aborts with a 400 error.
    Creates a new PlaylistSong entry and commits it to the database.

    Returns:
        JSON response indicating that the song has been added to the playlist.
    """
    data = request.get_json()
    playlist = Playlist.query.get(data['playlist_id'])
    song = Song.query.get(data['song_id'])
    if not playlist or not song:
        abort(400, description="Playlist or Song not found")
    playlist_song = PlaylistSong(playlist_id=playlist.id, song_id=song.id)
    db.session.add(playlist_song)
    db.session.commit()
    return jsonify({"message": "Song added to playlist"})

@app.route('/all/playlist-songs', methods=['GET'])
@verify_api_key
def get_playlist_songs():
    playlist_songs = PlaylistSong.query.all()
    return jsonify([{"id": playlist_song.id, "playlist_id": playlist_song.playlist_id, "song_id": playlist_song.song_id} for playlist_song in playlist_songs])

@app.route('/remove-song-from-playlist/<int:id>', methods=['DELETE'])
@verify_api_key
def remove_song_from_playlist(id):
    playlist_song = get_or_404(PlaylistSong, id)
    db.session.delete(playlist_song)
    db.session.commit()
    return jsonify({"message": "Song removed from playlist"})
if __name__ == '__main__':
    app.run(port=0000, debug=True)