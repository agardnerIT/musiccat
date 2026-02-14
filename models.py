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
    tracks = db.relationship(
        "Track", backref="cd", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_tracks=False):
        result = {
            "id": self.id,
            "barcode": self.barcode,
            "title": self.title,
            "artist": self.artist,
            "year": self.year,
            "genre": self.genre,
            "cover_url": self.cover_url,
            "added_date": self.added_date.isoformat() if self.added_date else None,
        }
        if include_tracks:
            result["tracks"] = [t.to_dict() for t in self.tracks]
        return result


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cd_id = db.Column(db.Integer, db.ForeignKey("cd.id"), nullable=False)
    track_number = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "track_number": self.track_number,
            "title": self.title,
            "duration": self.duration,
        }
