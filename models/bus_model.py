from database.db import get_db


class Bus:
    @staticmethod
    def create(operator, bus_type, from_city, to_city, departure_time, arrival_time, price):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO buses (operator, bus_type, from_city, to_city, departure_time, arrival_time, price)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (operator, bus_type, from_city, to_city, departure_time, arrival_time, price))

        db.commit()
        db.close()

    @staticmethod
    def all():
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM buses ORDER BY id DESC")
        buses = cur.fetchall()

        db.close()
        return buses

    @staticmethod
    def find(bus_id):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM buses WHERE id=%s LIMIT 1", (int(bus_id),))
        bus = cur.fetchone()

        db.close()
        return bus
