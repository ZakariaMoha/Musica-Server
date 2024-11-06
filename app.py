from flask import Flask
from models import User, Playlist, Song, Genre, Artist, Album, PlaylistSong

app = Flask(__name__)

# Configure the database URI ( SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musica_.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create all tables in the database
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")

if __name__ == "__main__":
    app.run(port=0000, debug=True)
