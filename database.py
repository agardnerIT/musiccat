from models import db
import os


def init_db(app):
    db_path = os.path.join(os.path.dirname(__file__), "..", "musiccat.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
