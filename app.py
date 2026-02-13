from flask import Flask, render_template, jsonify, request, redirect, url_for
from models import db, CD
import os

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), "musiccat.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    search_query = request.args.get("q", "")
    if search_query:
        cds = CD.query.filter(
            (CD.title.ilike(f"%{search_query}%"))
            | (CD.artist.ilike(f"%{search_query}%"))
        ).all()
    else:
        cds = CD.query.all()
    return render_template("index.html", cds=cds, search_query=search_query)


@app.route("/scan")
def scan():
    return render_template("scan.html")


@app.route("/cd/<int:cd_id>")
def cd_detail(cd_id):
    cd = CD.query.get_or_404(cd_id)
    return render_template("cd_detail.html", cd=cd)


@app.route("/cd/<int:cd_id>/edit", methods=["POST"])
def cd_edit(cd_id):
    cd = CD.query.get_or_404(cd_id)
    cd.title = request.form.get("title", cd.title)
    cd.artist = request.form.get("artist", cd.artist)
    cd.year = request.form.get("year", cd.year)
    cd.genre = request.form.get("genre", cd.genre)
    cd.cover_url = request.form.get("cover_url", cd.cover_url)
    db.session.commit()
    return redirect(url_for("cd_detail", cd_id=cd.id))


@app.route("/cd/<int:cd_id>/delete", methods=["POST"])
def cd_delete(cd_id):
    cd = CD.query.get_or_404(cd_id)
    db.session.delete(cd)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/api/lookup", methods=["GET"])
def api_lookup():
    barcode = request.args.get("barcode")
    if not barcode:
        return jsonify({"error": "No barcode provided"}), 400

    existing = CD.query.filter_by(barcode=barcode).first()
    if existing:
        return jsonify({"exists": True, "cd": existing.to_dict()})

    return jsonify({"exists": False})


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.json
    barcode = data.get("barcode")

    existing = CD.query.filter_by(barcode=barcode).first()
    if existing:
        return jsonify({"error": "CD already in collection"}), 400

    cd = CD(
        barcode=barcode,
        title=data.get("title"),
        artist=data.get("artist"),
        year=data.get("year"),
        genre=data.get("genre"),
        cover_url=data.get("cover_url"),
    )
    db.session.add(cd)
    db.session.commit()

    return jsonify({"success": True, "cd": cd.to_dict()})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=6123)
