from flask import Blueprint, request, jsonify
from models.bus_model import Bus
from database.db import get_db

bus_bp = Blueprint("bus_bp", __name__)


@bus_bp.route("/api/buses")
def get_buses():
    return jsonify(Bus.all())


@bus_bp.route("/api/search-buses")
def search_buses():
    from_city = request.args.get("from", "").strip()
    to_city = request.args.get("to", "").strip()
    bus_type = request.args.get("type", "").strip().lower()

    db = get_db()
    cur = db.cursor(dictionary=True)

    query = "SELECT * FROM buses WHERE 1=1"
    params = []

    if from_city:
        query += " AND LOWER(from_city)=LOWER(%s)"
        params.append(from_city)

    if to_city:
        query += " AND LOWER(to_city)=LOWER(%s)"
        params.append(to_city)

    if bus_type:
        query += " AND LOWER(bus_type) LIKE %s"
        params.append(f"%{bus_type}%")

    query += " ORDER BY id DESC"

    cur.execute(query, tuple(params))
    buses = cur.fetchall()
    db.close()

    return jsonify(buses)
