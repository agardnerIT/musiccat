from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    cover_url = db.Column(db.String(500), nullable=True)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "barcode": self.barcode,
            "title": self.title,
            "artist": self.artist,
            "year": self.year,
            "genre": self.genre,
            "cover_url": self.cover_url,
            "added_date": self.added_date.isoformat() if self.added_date else None,
        }
