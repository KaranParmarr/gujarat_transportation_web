import re
import os
import json
import sqlite3
import requests
import mysql.connector
from config import Config
from flask import jsonify
from datetime import datetime
from extensions import socketio
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from routes.bus_routes import bus_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from flask import Flask, render_template, request, redirect, session

# ✅ Set your Google Maps API key here or in ENV
GOOGLE_MAPS_KEY = "AIzaSyBczHR9oMy1EjYW-e9ibnd8IrBmeYpPMbM"

app = Flask(__name__)
app.secret_key = "gujarat_secret_key"
app.config.from_object(Config)
socketio.init_app(app)
app.register_blueprint(bus_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(payment_bp)

# ================= MONGODB (PyMongo) =================
# Local MongoDB (recommended for now)
app.config["MONGO_URI"] = "mongodb://localhost:27017/gujarat_transport"

# If you use MongoDB Atlas, use something like:
# app.config["MONGO_URI"] = "mongodb+srv://USER:PASS@cluster0.xxxxx.mongodb.net/gujarat_transport?retryWrites=true&w=majority"

mongo = PyMongo(app)

# ✅ MONGO COLLECTIONS (ADDED ONLY)
mongo_users = mongo.db.users
mongo_bus_bookings = mongo.db.bus_bookings
mongo_truck_bookings = mongo.db.truck_bookings
mongo_queries = mongo.db.queries

# ================= DATABASE =================
DATA_FILE = "queries.json"
SHIPMENTS_FILE = os.path.join(app.root_path, "shipments.json")
BUS_JSON_PATH = os.path.join(os.path.dirname(__file__), "bus_bookings.json")
USER_JSON_PATH = os.path.join(os.path.dirname(__file__), "user.json")


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="karan@05",
        database="gujarat_transport"
    )


def init_db():
    db = get_db()
    cur = db.cursor()
    # Add missing columns safely
    try:
        cur.execute(
            "ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
    except mysql.connector.Error:
        pass

    try:
        cur.execute(
            "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except mysql.connector.Error:
        pass

    # User Sign-UP/ Login Data
    cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(150),
    username VARCHAR(100) UNIQUE,
    email VARCHAR(150),
    password VARCHAR(255),
    role VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
    cur.execute("""CREATE TABLE IF NOT EXISTS buses(
  id INT AUTO_INCREMENT PRIMARY KEY,
  operator VARCHAR(120),
  bus_type VARCHAR(120),
  from_city VARCHAR(120),
  to_city VARCHAR(120),
  departure_time VARCHAR(20),
  arrival_time VARCHAR(20),
  price INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

    cur.execute("""CREATE TABLE IF NOT EXISTS truck_bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  fullname VARCHAR(100),
  contact VARCHAR(20),
  email VARCHAR(120),
  service VARCHAR(50),
  truck VARCHAR(50),
  insurance VARCHAR(20),
  cargo INT,
  distance INT,
  pickup VARCHAR(255),
  delivery VARCHAR(255),
  pickup_date DATE,
  payment INT,
  status VARCHAR(20) DEFAULT 'Confirmed',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

    cur.execute("""CREATE TABLE IF NOT EXISTS bus_bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  fullname VARCHAR(100),
  phone VARCHAR(20),
  email VARCHAR(120),
  busType VARCHAR(20),
  seaterType VARCHAR(20),
  journeyDate DATE,
  from_city VARCHAR(100),
  to_city VARCHAR(100),
  distance INT,
  ratePerKm INT,
  totalAmount INT,
  status VARCHAR(20) DEFAULT 'Confirmed',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

    # Create admin Login data
    cur.execute("SELECT * FROM users WHERE username=%s", ("admin",))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users (fullname, username, email, password, role)
        VALUES (%s,%s,%s,%s,%s)
        """, ("Administrator", "admin", "admin@site.com", "karan@2004", "admin"))

    db.commit()
    db.close()


init_db()

# ================= PAGES =================


@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


@app.route("/about")
def about():
    return render_template("about.html", user=session.get("user"))


@app.route("/contact")
def contact():
    return render_template("contact.html", user=session.get("user"))


@app.route("/service")
def service():
    return render_template("service.html", user=session.get("user"))


@app.route("/booking")
def booking():
    return render_template("booking.html", user=session.get("user"))


@app.route("/cargotransport")
def truck_booking():
    return render_template("cargotransport.html", user=session.get("user"))


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", user=session.get("user"))


@app.route("/login-modal")
def login_modal():
    return render_template("login-modal.html")


@app.route("/queries")
def queries():
    data = load_queries()
    return render_template("queries.html", queries=data, total=len(data))

# Load saved queries


def load_queries():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save queries


def save_queries(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/submit", methods=["POST"])
def submit():
    data = load_queries()

    # Username from login system (stored in session)
    username = session.get("username", "Guest")

    new_query = {
        "username": username,
        "fullname": request.form.get("data[NAME]"),
        "phone": request.form.get("data[PHONE]"),
        "email": request.form.get("data[EMAIL]"),
        "bus": request.form.get("data[BUS]"),
        "truck": request.form.get("data[TRUCK]"),
        "message": request.form.get("data[MESSAGE]"),
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    data.append(new_query)
    save_queries(data)

    # ✅ ALSO SAVE QUERY IN MONGO (ADDED ONLY)
    try:
        mongo_queries.insert_one({
            **new_query,
            "created_at": datetime.now()
        })
    except Exception as e:
        print("Mongo insert query error:", e)

    return redirect("/queries")


def load_users_json():
    try:
        with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_users_json(data):
    with open(USER_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.route("/export-users-json")
def export_users_json():
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        db.close()

        out_path = os.path.join(os.path.dirname(__file__), "user.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

        return jsonify({"status": "success", "count": len(users), "file": out_path})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/view-users-json")
def view_users_json():
    try:
        out_path = os.path.join(os.path.dirname(__file__), "user.json")
        with open(out_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ MONGO HEALTH CHECK (ADDED ONLY)
@app.route("/mongo-health")
def mongo_health():
    try:
        mongo.db.command("ping")
        return jsonify({"ok": True, "message": "MongoDB connected"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


# ✅ MONGO MIGRATION / SEED (ADDED ONLY)
@app.route("/mongo-seed")
def mongo_seed():
    """
    Copies existing data from:
    - MySQL users -> mongo.users
    - bus_bookings.json -> mongo.bus_bookings
    - shipments.json -> mongo.truck_bookings
    - queries.json -> mongo.queries
    So Compass shows data immediately.
    """
    report = {"users": 0, "bus_bookings": 0, "truck_bookings": 0, "queries": 0}

    # 1) Seed USERS from MySQL
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        db.close()

        for u in users:
            try:
                mongo_users.update_one(
                    {"username": u.get("username")},
                    {"$set": {
                        "mysql_id": u.get("id"),
                        "fullname": u.get("fullname"),
                        "username": u.get("username"),
                        "email": u.get("email"),
                        "password": u.get("password"),
                        "role": u.get("role"),
                        "status": u.get("status", "active"),
                        "created_at": u.get("created_at") or datetime.now()
                    }},
                    upsert=True
                )
                report["users"] += 1
            except Exception as e:
                print("Seed user error:", e)
    except Exception as e:
        print("Seed users(MySQL) error:", e)

    # 2) Seed BUS BOOKINGS from JSON
    try:
        bus_data = load_bus_bookings()
        for b in bus_data:
            try:
                mongo_bus_bookings.update_one(
                    {"id": str(b.get("id"))},
                    {"$set": {**b, "type": "bus", "created_at": datetime.now()}},
                    upsert=True
                )
                report["bus_bookings"] += 1
            except Exception as e:
                print("Seed bus_booking error:", e)
    except Exception as e:
        print("Seed bus_bookings(JSON) error:", e)

    # 3) Seed TRUCK BOOKINGS from JSON (shipments)
    try:
        shipments = load_shipments()
        for t in shipments:
            try:
                # use combo key to avoid duplicates
                key = f'{t.get("username", "")}|{t.get("date", "")}|{t.get("pickup", "")}|{t.get("delivery", "")}'
                mongo_truck_bookings.update_one(
                    {"seed_key": key},
                    {"$set": {**t, "type": "truck", "seed_key": key,
                              "created_at": datetime.now()}},
                    upsert=True
                )
                report["truck_bookings"] += 1
            except Exception as e:
                print("Seed truck_booking error:", e)
    except Exception as e:
        print("Seed truck_bookings(JSON) error:", e)

    # 4) Seed QUERIES from JSON
    try:
        qdata = load_queries()
        for q in qdata:
            try:
                key = f'{q.get("username", "")}|{q.get("date", "")}|{q.get("email", "")}'
                mongo_queries.update_one(
                    {"seed_key": key},
                    {"$set": {**q, "seed_key": key, "created_at": datetime.now()}},
                    upsert=True
                )
                report["queries"] += 1
            except Exception as e:
                print("Seed query error:", e)
    except Exception as e:
        print("Seed queries(JSON) error:", e)

    return jsonify({"ok": True, "seeded": report})

# ================= MIGRATION ROUTE (ADDED ONLY) =================


@app.route("/migrate-to-mongo")
def migrate_to_mongo():
    # ✅ secure (admin only)
    if "user" not in session or session["user"].get("role") != "admin":
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    report = {
        "users_from_mysql": 0,
        "queries_from_json": 0,
        "bus_from_json": 0,
        "truck_from_json": 0,
        "errors": []
    }

    # ---------- 1) MIGRATE USERS (MySQL -> Mongo) ----------
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        db.close()

        for u in users:
            try:
                # unique by mysql id OR username
                mongo_users.update_one(
                    {"$or": [{"mysql_id": u.get("id")}, {
                        "username": u.get("username")}]},
                    {"$set": {
                        "mysql_id": u.get("id"),
                        "fullname": u.get("fullname"),
                        "username": u.get("username"),
                        "email": u.get("email"),
                        "password": u.get("password"),
                        "role": u.get("role"),
                        "status": u.get("status", "active"),
                        "created_at": u.get("created_at") or datetime.now()
                    }},
                    upsert=True
                )
                report["users_from_mysql"] += 1
            except Exception as e:
                report["errors"].append(f"user mongo insert error: {e}")
    except Exception as e:
        report["errors"].append(f"mysql users fetch error: {e}")

    # ---------- 2) MIGRATE QUERIES (queries.json -> Mongo) ----------
    try:
        q_data = load_queries()
        for q in q_data:
            try:
                # dedupe by username + message + date
                mongo_queries.update_one(
                    {"username": q.get("username"), "message": q.get(
                        "message"), "date": q.get("date")},
                    {"$setOnInsert": {**q, "created_at": datetime.now()}},
                    upsert=True
                )
                report["queries_from_json"] += 1
            except Exception as e:
                report["errors"].append(f"query mongo insert error: {e}")
    except Exception as e:
        report["errors"].append(f"queries.json read error: {e}")

    # ---------- 3) MIGRATE BUS BOOKINGS (bus_bookings.json -> Mongo) ----------
    try:
        b_data = load_bus_bookings()
        for b in b_data:
            try:
                # dedupe by id OR (username + date + from + to)
                mongo_bus_bookings.update_one(
                    {"$or": [
                        {"id": str(b.get("id"))},
                        {"username": b.get("username"), "date": b.get(
                            "date"), "from": b.get("from"), "to": b.get("to")}
                    ]},
                    {"$set": {**b, "type": "bus", "created_at": datetime.now()}},
                    upsert=True
                )
                report["bus_from_json"] += 1
            except Exception as e:
                report["errors"].append(f"bus mongo insert error: {e}")
    except Exception as e:
        report["errors"].append(f"bus_bookings.json read error: {e}")

    # ---------- 4) MIGRATE TRUCK SHIPMENTS/BOOKINGS (shipments.json -> Mongo) ----------
    try:
        t_data = load_shipments()
        for t in t_data:
            try:
                # dedupe by username + date + pickup + delivery
                mongo_truck_bookings.update_one(
                    {"username": t.get("username"), "date": t.get("date"),
                     "pickup": t.get("pickup"), "delivery": t.get("delivery")},
                    {"$set": {**t, "type": "truck", "created_at": datetime.now()}},
                    upsert=True
                )
                report["truck_from_json"] += 1
            except Exception as e:
                report["errors"].append(f"truck mongo insert error: {e}")
    except Exception as e:
        report["errors"].append(f"shipments.json read error: {e}")

    return jsonify({"ok": True, "report": report})

# ================= MONGO MIGRATION ROUTE (ADDED ONLY) =================


@app.route("/mongo-migrate")
def mongo_migrate():
    """
    Migrates existing data from:
    - MySQL users table
    - queries.json
    - bus_bookings.json
    - shipments.json
    into MongoDB collections.
    """

    report = {
        "ok": True,
        "mongo_db": "gujarat_transport",
        "migrated": {
            "users_mysql_to_mongo": 0,
            "queries_json_to_mongo": 0,
            "bus_bookings_json_to_mongo": 0,
            "truck_shipments_json_to_mongo": 0
        },
        "errors": []
    }

    # ---- 0) check mongo ping ----
    try:
        mongo.db.command("ping")
    except Exception as e:
        return jsonify({"ok": False, "error": f"MongoDB not connected: {str(e)}"}), 500

    # ---- 1) MySQL USERS -> Mongo USERS ----
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        db.close()

        count = 0
        for u in users:
            # store mysql id inside mongo as mysql_id for mapping
            doc = {
                "mysql_id": u.get("id"),
                "fullname": u.get("fullname"),
                "username": u.get("username"),
                "email": u.get("email"),
                "password": u.get("password"),
                "role": u.get("role"),
                "status": u.get("status", "active"),
                "created_at": u.get("created_at")  # can be datetime from mysql
            }

            # upsert by username (unique)
            mongo_users.update_one(
                {"username": doc["username"]},
                {"$set": doc},
                upsert=True
            )
            count += 1

        report["migrated"]["users_mysql_to_mongo"] = count

    except Exception as e:
        report["errors"].append(f"MySQL->Mongo users error: {str(e)}")

    # ---- 2) queries.json -> Mongo queries ----
    try:
        qdata = load_queries()
        count = 0
        for q in qdata:
            # upsert on (username + date + message) to avoid duplicates
            key = {
                "username": q.get("username", "Guest"),
                "date": q.get("date", ""),
                "message": q.get("message", "")
            }
            mongo_queries.update_one(
                key,
                {"$setOnInsert": {**q, "created_at": datetime.now()}},
                upsert=True
            )
            count += 1

        report["migrated"]["queries_json_to_mongo"] = count
    except Exception as e:
        report["errors"].append(f"queries.json->Mongo error: {str(e)}")

    # ---- 3) bus_bookings.json -> Mongo bus_bookings ----
    try:
        bdata = load_bus_bookings()
        count = 0
        for b in bdata:
            # your bus json uses "id" as unique booking id
            bid = str(b.get("id", "")).strip()
            if not bid:
                # fallback: unique key by username+date+from+to
                bid = f'{b.get("username", "")}|{b.get("date", "")}|{b.get("from", "")}|{b.get("to", "")}'

            doc = {**b}
            doc["type"] = "bus"
            doc["created_at"] = datetime.now()

            mongo_bus_bookings.update_one(
                {"id": str(b.get("id", bid))},
                {"$set": doc},
                upsert=True
            )
            count += 1

        report["migrated"]["bus_bookings_json_to_mongo"] = count
    except Exception as e:
        report["errors"].append(f"bus_bookings.json->Mongo error: {str(e)}")

    # ---- 4) shipments.json -> Mongo truck_bookings ----
    try:
        tdata = load_shipments()
        count = 0
        for t in tdata:
            # build a stable unique key to prevent duplicates
            key = {
                "username": t.get("username", ""),
                "date": t.get("date", ""),
                "pickup": t.get("pickup", ""),
                "delivery": t.get("delivery", "")
            }

            doc = {**t}
            doc["type"] = "truck"
            doc["created_at"] = datetime.now()

            mongo_truck_bookings.update_one(
                key,
                {"$setOnInsert": doc},
                upsert=True
            )
            count += 1

        report["migrated"]["truck_shipments_json_to_mongo"] = count
    except Exception as e:
        report["errors"].append(f"shipments.json->Mongo error: {str(e)}")

    # ---- done ----
    if report["errors"]:
        report["ok"] = False

    return jsonify(report)

# ================= AUTH =================


@app.route("/register", methods=["POST"])
def register():
    db = get_db()
    cur = db.cursor()

    try:
        cur.execute("""
        INSERT INTO users (fullname, username, email, password, role)
        VALUES (%s,%s,%s,%s,%s)
        """, (
            request.form["fullname"],
            request.form["username"],
            request.form["email"],
            request.form["password"],
            "user"
        ))
        db.commit()
    except:
        return "exists"

    cur.execute("SELECT * FROM users WHERE username=%s",
                (request.form["username"],))
    user = cur.fetchone()

    session["user"] = {
        "id": user[0],
        "username": user[2],
        "email": user[3],
        "role": user[5]
    }
    session["username"] = session["user"]["username"]

    session["new_signup"] = True

    # ✅ ALSO SAVE USER IN user.json (ADDED ONLY)
    users = load_users_json()

    users.append({
        "id": user[0],  # same id from MySQL
        "fullname": request.form["fullname"],
        "username": request.form["username"],
        "email": request.form["email"],
        "password": request.form["password"],
        "role": "user",
        "status": "active",
        "created_at": datetime.now().strftime("%d-%m-%Y %H:%M")
    })

    save_users_json(users)

    # ✅ ALSO SAVE USER IN MONGO (ADDED ONLY)
    try:
        mongo_users.update_one(
            {"username": request.form["username"]},
            {"$setOnInsert": {
                "mysql_id": user[0],
                "fullname": request.form["fullname"],
                "username": request.form["username"],
                "email": request.form["email"],
                "password": request.form["password"],
                "role": "user",
                "status": "active",
                "created_at": datetime.now()
            }},
            upsert=True
        )
    except Exception as e:
        print("Mongo insert user error:", e)

    return "success"


@app.route("/login", methods=["POST"])
def login():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    SELECT * FROM users
    WHERE username=%s AND password=%s
    """, (request.form["username"], request.form["password"]))

    user = cur.fetchone()
    # validate user here
    if user:
        session["user"] = {
            "id": user[0],
            "username": user[2],
            "email": user[3],
            "role": user[5]
        }
        session["username"] = session["user"]["username"]

        # ✅ OPTIONAL: update last_login in Mongo (ADDED ONLY)
        try:
            mongo_users.update_one(
                {"username": session["user"]["username"]},
                {"$set": {"last_login": datetime.now()}},
                upsert=True
            )
        except Exception as e:
            print("Mongo update last_login error:", e)

        return user[5]   # "admin" or "user"

    return "invalid"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= PROFILE =================


@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/")
    return render_template("profile.html", user=session["user"])

# ================= MY BOOKINGS =================


@app.route("/mybookings")
def mybookings():
    if "user" not in session:
        return redirect("/")

    username = session["user"]["username"]

    # ✅ Load both json lists
    bus_data = load_bus_bookings()
    truck_data = load_shipments()  # you already use this

    # ✅ Filter only current user's bookings
    my_bus = [b for b in bus_data if b.get("username") == username]
    my_truck = [t for t in truck_data if t.get("username") == username]

    # ===== COMBINE + AUTO SORT BY DATE (NEWEST FIRST) =====
    combined = []

    for b in my_bus:
        b["type"] = "bus"
        combined.append(b)

    for t in my_truck:
        t["type"] = "truck"
        combined.append(t)

    # sort by date (your format: dd-mm-YYYY HH:MM)
    def parse_dt(x):
        try:
            return datetime.strptime(x.get("date", ""), "%d-%m-%Y %H:%M")
        except:
            return datetime.min

    combined = sorted(combined, key=parse_dt, reverse=True)

    return render_template(
        "mybookings.html",
        user=session["user"],
        all_bookings=combined
    )


# ================= ADMIN PANEL =================
@app.route("/adminpanel")
def adminpanel():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # TOTAL USERS
    cur.execute("SELECT COUNT(*) AS total FROM users")
    user_count = cur.fetchone()["total"]

    # RECENT SIGNUPS (Last 10 users)
    cur.execute(
        "SELECT fullname, username, email FROM users ORDER BY created_at DESC LIMIT 8")
    users = cur.fetchall()

    # -------------------------------
    # 🔥 ADD TRUCK SHIPMENT SYSTEM
    # -------------------------------

    def to_int(val):
        try:
            digits = "".join(ch for ch in str(val) if ch.isdigit())
            return int(digits) if digits else 0
        except:
            return 0

    shipments = load_shipments()   # ✅ IMPORTANT: uses fixed path

    truck_count = len(shipments)
    truck_revenue = sum(to_int(s.get("payment", 0)) for s in shipments)

    bookings = []
    for s in shipments[::-1]:   # newest first (shows old also)
        bookings.append({
            "username": s.get("username", "guest"),
            "type": "Truck",
            "amount": to_int(s.get("payment", 0)),
            "date": s.get("date", "")
        })

    # -------------------------------
    # ✅ ADD BUS BOOKING SYSTEM (ONLY ADD)
    # -------------------------------
    bus_bookings = load_bus_bookings()
    bus_count = len(bus_bookings)
    bus_revenue = sum(to_int(b.get("payment", 0)) for b in bus_bookings)

    # Add bus bookings into same recent list
    for b in bus_bookings[::-1]:  # newest first
        bookings.append({
            "username": b.get("username", "guest"),
            "type": "Bus",
            "amount": to_int(b.get("payment", 0)),
            "date": b.get("date", "")
        })

    # ✅ TOTAL REVENUE = Truck + Bus
    total_revenue = truck_revenue + bus_revenue

    # ✅ Keep only LAST 5 in "Recent Bookings" table (new comes → old hides)
    def parse_dt(s):
        try:
            return datetime.strptime(str(s), "%d-%m-%Y %H:%M")
        except:
            return datetime.min

    bookings = sorted(bookings, key=lambda x: parse_dt(
        x.get("date", "")), reverse=True)[:5]

    # -------------------------------
    db.close()

    return render_template(
        "adminpanel.html",
        user_count=user_count,
        users=users,
        bus_count=bus_count,         # ✅ now updates Bus card
        truck_count=truck_count,     # ✅ updates Truck card
        total_revenue=total_revenue,  # ✅ updates Revenue card (Bus+Truck)
        bookings=bookings            # ✅ only latest 5 (Bus+Truck)
    )


@app.route("/api/admin-stats")
def admin_stats():
    if "user" not in session or session["user"]["role"] != "admin":
        return {"error": "unauthorized"}

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Total users
    cur.execute("SELECT COUNT(*) AS total FROM users")
    user_count = cur.fetchone()["total"]

    # Recent users
    cur.execute(
        "SELECT fullname, username, email FROM users ORDER BY created_at DESC LIMIT 10")
    users = cur.fetchall()

    db.close()

    return {
        "user_count": user_count,
        "users": users
    }


@app.route("/users")
def manage_users():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/")
    return render_template("manage-users.html")


@app.route("/get-users")
def get_users():
    if "user" not in session or session["user"]["role"] != "admin":
        return "unauthorized"

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users ORDER BY id DESC")
    users = cur.fetchall()
    db.close()

    return jsonify(users)


@app.route("/delete-user/<int:id>")
def delete_user(id):
    if "user" not in session or session["user"]["role"] != "admin":
        return "unauthorized"

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    db.commit()
    db.close()

    # ✅ ALSO DELETE FROM MONGO (ADDED ONLY)
    try:
        mongo_users.delete_many({"mysql_id": id})
    except Exception as e:
        print("Mongo delete user error:", e)

    return "deleted"


@app.route("/toggle-user/<int:id>")
def toggle_user(id):
    if "user" not in session or session["user"]["role"] != "admin":
        return "unauthorized"

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT status FROM users WHERE id=%s", (id,))
    status = cur.fetchone()[0]

    new_status = "blocked" if status == "active" else "active"
    cur.execute("UPDATE users SET status=%s WHERE id=%s", (new_status, id))
    db.commit()
    db.close()

    # ✅ ALSO UPDATE IN MONGO (ADDED ONLY)
    try:
        mongo_users.update_many(
            {"mysql_id": id}, {"$set": {"status": new_status}})
    except Exception as e:
        print("Mongo toggle user error:", e)

    return new_status


@app.route("/edit-user", methods=["POST"])
def edit_user():
    if "user" not in session or session["user"]["role"] != "admin":
        return "unauthorized"

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    UPDATE users SET fullname=%s, email=%s
    WHERE id=%s
    """, (
        request.form["fullname"],
        request.form["email"],
        request.form["id"]
    ))

    db.commit()
    db.close()

    # ✅ ALSO UPDATE IN MONGO (ADDED ONLY)
    try:
        mongo_users.update_many(
            {"mysql_id": int(request.form["id"])},
            {"$set": {
                "fullname": request.form["fullname"],
                "email": request.form["email"]
            }}
        )
    except Exception as e:
        print("Mongo edit user error:", e)

    return "updated"


@app.route("/seat_layout")
def seat_layout():
    return render_template("seat_layout.html", user=session.get("user"))


def load_shipments():
    try:
        with open(SHIPMENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_shipments(data):
    with open(SHIPMENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/trucks-shipment")
def shipments():
    return render_template("trucks-shipment.html", user=session.get("user"))


@app.route("/save-truck-shipment", methods=["POST"])
def save_truck_shipment():
    shipments = load_shipments()

    data = request.json
    username = session.get("username", "guest")

    cost = int(data["distance"]) * 60

    shipment = {
        "username": username,
        "fullname": data["fullname"],
        "email": data["email"],
        "contact": data["contact"],
        "distance": data["distance"],
        "pickup": data["pickup"],
        "delivery": data["delivery"],
        "insurance": data["insurance"],
        "cargo": data["cargo"],
        "service": data["service"],
        "truck": data["truck"],
        "payment": cost,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    shipments.append(shipment)
    save_shipments(shipments)

    # ✅ ALSO SAVE TRUCK SHIPMENT IN MONGO (ADDED ONLY)
    try:
        mongo_truck_bookings.insert_one({
            **shipment,
            "type": "truck",
            "created_at": datetime.now()
        })
    except Exception as e:
        print("Mongo insert truck_shipment error:", e)

    return jsonify({"success": True})


@app.route("/api/truck-admin")
def truck_admin_api():
    shipments = load_shipments()

    def to_int(val):
        # accepts "3600", "₹ 3,600", "3600\n"
        s = str(val or "")
        digits = re.sub(r"[^\d]", "", s)
        return int(digits) if digits else 0

    total_revenue = sum(to_int(s.get("payment")) for s in shipments)
    total_shipments = len(shipments)

    return jsonify({
        "total_revenue": total_revenue,
        "total_shipments": total_shipments,
        "shipments": shipments[::-1]  # newest first
    })


@app.route("/save-shipments", methods=["POST"])
def save_shipments_api():

    data = request.json
    with open("shipments.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"status": "success"})


@app.route("/save-truck-booking", methods=["POST"])
def save_truck_booking():

    # Block guest users
    if "user" not in session:
        return jsonify({"status": "login_required"})

    data = load_shipments()

    new = {
        "username": session["user"]["username"],
        "fullname": request.form["fullname"],
        "email": request.form["email"],
        "contact": request.form["contact"],
        "distance": request.form["distance"],
        "pickup": request.form["pickup"],
        "delivery": request.form["delivery"],
        "insurance": request.form["insurance"],
        "cargo": request.form["cargo"],
        "service": request.form["service"],
        "truck": request.form["truck"],
        "pickup_date": request.form.get("date", ""),
        "payment": request.form["payment"],
        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }

    data.append(new)
    save_shipments(data)

    # ✅ ALSO SAVE TRUCK BOOKING IN MONGO (ADDED ONLY)
    try:
        mongo_truck_bookings.insert_one({
            **new,
            "type": "truck",
            "created_at": datetime.now()
        })
    except Exception as e:
        print("Mongo insert truck_booking error:", e)

    return jsonify({"status": "success"})


@app.route("/pay-truck", methods=["POST"])
def pay_truck():
    if "user" not in session:
        return redirect("/login")

    data = request.form
    db = get_db()
    cur = db.cursor()

    payment = int(data["distance"]) * 60

    cur.execute("""
        INSERT INTO truck_shipments
        (username, fullname, email, contact, distance, pickup, delivery,
         insurance, cargo_weight, service_type, truck_type, payment)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        session["user"]["username"],
        data["fullname"],
        data["email"],
        data["contact"],
        data["distance"],
        data["pickup"],
        data["delivery"],
        data["insurance"],
        data["cargo"],
        data["service"],
        data["truck"],
        payment
    ))

    db.commit()
    db.close()

    return redirect("/thankyou")

# ================ API =================


@app.route("/api/distance")
def api_distance():
    origin = (request.args.get("origin")
              or request.args.get("from") or "").strip()
    destination = (request.args.get("destination")
                   or request.args.get("to") or "").strip()

    if not origin or not destination:
        return jsonify({"ok": False, "error": "missing origin/destination"}), 400

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }

    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": 0,
                    "longitude": 0
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": 0,
                    "longitude": 0
                }
            }
        },
        "travelMode": "DRIVE"
    }

    # ✅ Routes API needs address strings differently
    body["origin"] = {"address": origin}
    body["destination"] = {"address": destination}

    try:
        r = requests.post(url, headers=headers, json=body, timeout=10)
        data = r.json()

        if "error" in data:
            return jsonify({"ok": False, "error": data["error"].get("status"), "raw": data}), 400

        if "routes" not in data or not data["routes"]:
            return jsonify({"ok": False, "error": "No routes returned", "raw": data}), 404

        route = data["routes"][0]

        km = route["distanceMeters"] / 1000

        return jsonify({
            "ok": True,
            "km": round(km),
            "distance_text": f"{round(km)} km",
            "duration_text": route["duration"]
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ================bus booking API=================


@app.route("/bus-booking")
def bus_booking_admin_page():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/")
    return render_template("bus-booking.html", user=session.get("user"))


def load_bus_bookings():
    try:
        with open(BUS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_bus_booking(data):
    with open(BUS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def to_int(val):
    try:
        digits = "".join(ch for ch in str(val) if ch.isdigit())
        return int(digits) if digits else 0
    except:
        return 0

# ---------- SAVE BUS BOOKING ----------


@app.route("/save-bus-booking", methods=["POST"])
def save_bus_booking_route():
    # block guest users
    if "user" not in session:
        return jsonify({"status": "login_required"})

    def to_int(val):
        digits = "".join(ch for ch in str(val) if ch.isdigit())
        return int(digits) if digits else 0

    # read form
    username = session["user"]["username"]
    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip()
    contact = request.form.get("phone", "").strip()
    distance = to_int(request.form.get("distance", 0))
    from_city = request.form.get("from", "").strip()
    to_city = request.form.get("to", "").strip()
    bus_type = request.form.get("busType", "").strip()
    seater_type = request.form.get("seaterType", "").strip()
    payment = to_int(request.form.get(
        "totalAmount", request.form.get("payment", 0)))

    journey_date = request.form.get("journeyDate", "").strip()
    if not (fullname and email and contact and distance and from_city and to_city and bus_type and seater_type and journey_date and payment):
        return jsonify({"status": "invalid"})

    now_str = datetime.now().strftime("%d-%m-%Y %H:%M")
    booking_id = str(int(datetime.now().timestamp() * 1000))  # unique id

    # ---- 1) SAVE TO JSON ----
    data = load_bus_bookings()
    next_id = 1
    if data:
        try:
            next_id = max(int(x.get("id", 0)) for x in data) + 1
        except:
            next_id = len(data) + 1

    booking_doc = {
        "id": booking_id,
        "username": username,
        "fullname": fullname,
        "email": email,
        "contact": contact,
        "distance": distance,
        "from": from_city,
        "to": to_city,
        "busType": bus_type,
        "seaterType": seater_type,
        "journeyDate": journey_date,
        "payment": payment,
        "date": now_str
    }

    data.append(booking_doc)
    save_bus_booking(data)

    # ---- 2) SAVE TO MYSQL ----
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("""
    INSERT INTO bus_bookings
    (username, fullname, phone, email, distance, from_city, to_city,
     bus_type, seater_type, journey_date, payment, created_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
""", (
            username, fullname, contact, email, distance, from_city, to_city,
            bus_type, seater_type, journey_date, payment, datetime.now()
        ))

        db.commit()
        db.close()
    except Exception as e:
        # If MySQL fails, JSON still saved — keep running
        print("MySQL insert bus_bookings error:", e)

    # ✅ ALSO SAVE BUS BOOKING IN MONGO (ADDED ONLY)
    try:
        mongo_bus_bookings.insert_one({
            **booking_doc,
            "type": "bus",
            "created_at": datetime.now()
        })
    except Exception as e:
        print("Mongo insert bus_booking error:", e)

    return jsonify({"status": "success", "username": username, "fullname": fullname})


@app.route("/api/bus-admin")
def bus_admin_api():
    def to_int(val):
        digits = "".join(ch for ch in str(val) if ch.isdigit())
        return int(digits) if digits else 0

    bookings = load_bus_bookings()   # newest last in file
    total_revenue = sum(to_int(b.get("payment", 0)) for b in bookings)
    total_bookings = len(bookings)

    # return newest first for UI
    return jsonify({
        "ok": True,
        "total_revenue": total_revenue,
        "total_bookings": total_bookings,
        "bookings": bookings[::-1]
    })


@app.route("/api/delete-bus-booking/<id>", methods=["DELETE"])
def delete_bus_booking(id):
    data = load_bus_bookings()
    data = [b for b in data if str(b.get("id")) != str(id)]
    save_bus_booking(data)

    # ✅ ALSO DELETE FROM MONGO (ADDED ONLY)
    try:
        mongo_bus_bookings.delete_many({"id": str(id)})
    except Exception as e:
        print("Mongo delete bus_booking error:", e)

    return jsonify({"ok": True})


@app.route("/api/edit-bus-booking", methods=["POST"])
def edit_bus_booking():
    payload = request.json
    data = load_bus_bookings()

    for b in data:
        if str(b.get("id")) == str(payload["id"]):
            b.update(payload)

    save_bus_booking(data)

    # ✅ ALSO UPDATE IN MONGO (ADDED ONLY)
    try:
        mongo_bus_bookings.update_many(
            {"id": str(payload["id"])}, {"$set": payload})
    except Exception as e:
        print("Mongo edit bus_booking error:", e)

    return jsonify({"ok": True})


if __name__ == "__main__":
    socketio.run(app, debug=True)
    # app.run(debug=True)
