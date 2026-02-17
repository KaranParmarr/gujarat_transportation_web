import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    
    # ✅ SQLite by default (no extra install)
    database_url = os.getenv("DATABASE_URL", "sqlite:///redbus_clone.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app


def init_db():
    app = create_app()

    with app.app_context():
        # Import models AFTER db is ready
        from models.user_model import User
        from models.bus_model import Bus
        from models.seat_model import Seat
        from models.booking_model import Booking

        print("✅ Creating tables...")
        db.create_all()

        # -----------------------------
        # ✅ SEED ADMIN + USERS
        # -----------------------------
        if User.query.count() == 0:
            users = [
                User(full_name="Karan Parmar", username="karan_parmar", email="official.karanparmar@gmail.com",
                     password="admin@2004", role="admin"),
                User(full_name="Rahul Sharma", username="rahul_s", email="rahul@gmail.com", password="rahul123",
                     role="user"),
                User(full_name="Priya Patel", username="priya_p", email="priya@gmail.com", password="priya123",
                     role="user"),
                User(full_name="Amit Verma", username="amit_v", email="amit@gmail.com", password="amit123",
                     role="user"),
                User(full_name="Neha Singh", username="neha_s", email="neha@gmail.com", password="neha123",
                     role="user"),
                User(full_name="Sahil Khan", username="sahil_k", email="sahil@gmail.com", password="sahil123",
                     role="user"),
                User(full_name="Anjali Mehta", username="anjali_m", email="anjali@gmail.com", password="anjali123",
                     role="user"),
            ]
            db.session.add_all(users)
            db.session.commit()
            print("✅ Seeded 7 users (including admin).")

        # -----------------------------
        # ✅ SEED BUSES
        # -----------------------------
        if Bus.query.count() == 0:
            bus1 = Bus(
                operator_name="Falcon Travels",
                route_from="Mumbai",
                route_to="Ahmedabad",
                bus_type="AC Sleeper",
                departure_time="20:00",
                arrival_time="04:45",
                price=3200
            )

            bus2 = Bus(
                operator_name="Ganga Travels",
                route_from="Mumbai",
                route_to="Ahmedabad",
                bus_type="Sleeper",
                departure_time="22:40",
                arrival_time="09:35",
                price=1259
            )

            db.session.add_all([bus1, bus2])
            db.session.commit()
            print("✅ Seeded 2 buses.")

        # -----------------------------
        # ✅ SEED SEATS (Upper/Lower Sleeper + Side Sleeper)
        # -----------------------------
        if Seat.query.count() == 0:
            buses = Bus.query.all()

            for bus in buses:
                seats = []

                # Lower Sleeper (L1-L12)
                for i in range(1, 13):
                    seats.append(
                        Seat(bus_id=bus.id, seat_no=f"L{i}", deck="lower", seat_type="sleeper", price=bus.price,
                             is_booked=False)
                    )

                # Upper Sleeper (U1-U12)
                for i in range(1, 13):
                    seats.append(
                        Seat(bus_id=bus.id, seat_no=f"U{i}", deck="upper", seat_type="sleeper", price=bus.price,
                             is_booked=False)
                    )

                # Side Sleeper (SL1-SL4 lower, SU1-SU4 upper)
                for i in range(1, 5):
                    seats.append(
                        Seat(bus_id=bus.id, seat_no=f"SL{i}", deck="lower", seat_type="side_sleeper", price=bus.price,
                             is_booked=False)
                    )
                    seats.append(
                        Seat(bus_id=bus.id, seat_no=f"SU{i}", deck="upper", seat_type="side_sleeper", price=bus.price,
                             is_booked=False)
                    )

                db.session.add_all(seats)

            db.session.commit()
            print("✅ Seeded seats for all buses (lower/upper + side sleeper).")

        print("🎉 Database initialized successfully!")


if __name__ == "__main__":
    init_db()
