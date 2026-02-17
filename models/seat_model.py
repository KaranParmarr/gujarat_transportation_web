from database.db import get_db
import time

class Seat:
    LOCK_DURATION = 300  # 5 minutes

    @staticmethod
    def get_by_bus(bus_id):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT seat_no, status, lock_time
            FROM seats
            WHERE bus_id=%s
            ORDER BY seat_no ASC
        """, (int(bus_id),))
        seats = cur.fetchall()

        db.close()
        return seats

    @staticmethod
    def lock(bus_id, seat_no):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT status, lock_time
            FROM seats
            WHERE bus_id=%s AND seat_no=%s
            LIMIT 1
        """, (int(bus_id), str(seat_no)))
        seat = cur.fetchone()

        if not seat:
            db.close()
            return {"error": "Seat not found"}

        # locked not expired?
        if seat["status"] == "locked" and seat["lock_time"]:
            if int(time.time()) - int(seat["lock_time"]) < Seat.LOCK_DURATION:
                db.close()
                return {"error": "Seat already locked"}

        if seat["status"] == "booked":
            db.close()
            return {"error": "Seat already booked"}

        cur.execute("""
            UPDATE seats
            SET status='locked', lock_time=%s
            WHERE bus_id=%s AND seat_no=%s
        """, (int(time.time()), int(bus_id), str(seat_no)))

        db.commit()
        db.close()
        return {"success": True}

    @staticmethod
    def book(bus_id, seat_no):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            UPDATE seats
            SET status='booked', lock_time=NULL
            WHERE bus_id=%s AND seat_no=%s
        """, (int(bus_id), str(seat_no)))

        db.commit()
        db.close()
