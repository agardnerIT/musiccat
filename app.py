import json

from flask import Flask, render_template, jsonify, request, redirect, url_for
from models import db, CD, Track
from api_client import lookup_barcode
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
        matching_tracks = Track.query.filter(Track.title.ilike(search_query)).all()
    else:
        cds = CD.query.all()
        matching_tracks = []
    return render_template(
        "index.html",
        cds=cds,
        matching_tracks=matching_tracks,
        search_query=search_query,
    )


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

    mb_data = lookup_barcode(barcode)
    if mb_data:
        return jsonify({"exists": False, "mb_data": mb_data})

    return jsonify({"exists": False, "mb_data": None})


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.json
    barcode = data.get("barcode")
    print(f"DEBUG api_add: received data keys = {data.keys()}")
    print(f"DEBUG api_add: tracks = {data.get('tracks')}")

    existing = CD.query.filter_by(barcode=barcode).first()
    if existing:
        return jsonify(
            {
                "error": "CD already in collection",
                "exists": True,
                "cd": existing.to_dict(include_tracks=True),
            }
        ), 400

    cd = CD(
        barcode=barcode,
        title=data.get("title"),
        artist=data.get("artist"),
        year=data.get("year"),
        genre=data.get("genre"),
        cover_url=data.get("cover_url"),
    )
    db.session.add(cd)
    db.session.flush()

    tracks_raw = data.get("tracks")
    tracks_data = []
    if tracks_raw:
        if isinstance(tracks_raw, str):
            try:
                tracks_data = json.loads(tracks_raw)
            except json.JSONDecodeError:
                tracks_data = []
        elif isinstance(tracks_raw, list):
            tracks_data = tracks_raw

    for track_data in tracks_data:
        track = Track(
            cd_id=cd.id,
            track_number=track_data.get("track_number"),
            title=track_data.get("title"),
            duration=track_data.get("duration"),
        )
        db.session.add(track)

    db.session.commit()

    return jsonify({"success": True, "cd": cd.to_dict(include_tracks=True)})


@app.route("/api/duplicates", methods=["GET"])
def api_duplicates():
    all_cds = CD.query.all()

    barcode_dups = {}
    title_artist_dups = {}

    for cd in all_cds:
        if cd.barcode:
            if cd.barcode not in barcode_dups:
                barcode_dups[cd.barcode] = []
            barcode_dups[cd.barcode].append(cd.to_dict())

        key = f"{cd.title}|{cd.artist}".lower()
        if key not in title_artist_dups:
            title_artist_dups[key] = []
        title_artist_dups[key].append(cd.to_dict())

    barcode_duplicates = {k: v for k, v in barcode_dups.items() if len(v) > 1}
    title_artist_duplicates = {k: v for k, v in title_artist_dups.items() if len(v) > 1}

    return jsonify(
        {
            "barcode_duplicates": barcode_duplicates,
            "title_artist_duplicates": title_artist_duplicates,
        }
    )


@app.route("/duplicates")
def duplicates():
    all_cds = CD.query.all()

    barcode_dups = {}
    title_artist_dups = {}

    for cd in all_cds:
        if cd.barcode:
            if cd.barcode not in barcode_dups:
                barcode_dups[cd.barcode] = []
            barcode_dups[cd.barcode].append(cd)

        key = f"{cd.title}|{cd.artist}".lower()
        if key not in title_artist_dups:
            title_artist_dups[key] = []
        title_artist_dups[key].append(cd)

    barcode_duplicates = {k: v for k, v in barcode_dups.items() if len(v) > 1}
    title_artist_duplicates = {k: v for k, v in title_artist_dups.items() if len(v) > 1}

    return render_template(
        "duplicates.html",
        barcode_duplicates=barcode_duplicates,
        title_artist_duplicates=title_artist_duplicates,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=6123, ssl_context=("cert.pem", "key.pem"))
