from database.db import get_db

class Booking:
    @staticmethod
    def create(user_id, bus_id, seats_csv, amount, payment_status="paid"):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO bookings (user_id, bus_id, seats, amount, payment_status)
            VALUES (%s,%s,%s,%s,%s)
        """, (int(user_id), int(bus_id), seats_csv, int(amount), payment_status))

        db.commit()
        db.close()

    @staticmethod
    def recent(limit=10):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT b.id, u.fullname, u.username, b.bus_id, b.seats, b.amount, b.payment_status, b.created_at
            FROM bookings b
            JOIN users u ON u.id = b.user_id
            ORDER BY b.created_at DESC
            LIMIT %s
        """, (int(limit),))

        rows = cur.fetchall()
        db.close()
        return rows

    @staticmethod
    def total_revenue_paid():
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT IFNULL(SUM(amount),0) FROM bookings WHERE payment_status='paid'")
        total = cur.fetchone()[0]

        db.close()
        return int(total)
