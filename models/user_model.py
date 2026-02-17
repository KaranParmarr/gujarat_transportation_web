from database.db import get_db

class User:
    @staticmethod
    def create(fullname, username, email, password, role="user"):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO users (fullname, username, email, password, role)
            VALUES (%s,%s,%s,%s,%s)
        """, (fullname, username, email, password, role))

        db.commit()
        db.close()

    @staticmethod
    def find_by_username(username):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (username,))
        user = cur.fetchone()

        db.close()
        return user

    @staticmethod
    def find_by_username_password(username, password):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT * FROM users WHERE username=%s AND password=%s LIMIT 1
        """, (username, password))
        user = cur.fetchone()

        db.close()
        return user

    @staticmethod
    def count_all():
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) FROM users")
        total = cur.fetchone()[0]

        db.close()
        return total

    @staticmethod
    def recent(limit=10):
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT fullname, username, email, created_at, status, role
            FROM users
            ORDER BY created_at DESC
            LIMIT %s
        """, (int(limit),))
        users = cur.fetchall()

        db.close()
        return users

    @staticmethod
    def all_users():
        db = get_db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM users ORDER BY id DESC")
        users = cur.fetchall()

        db.close()
        return users

    @staticmethod
    def delete(user_id):
        db = get_db()
        cur = db.cursor()

        cur.execute("DELETE FROM users WHERE id=%s", (int(user_id),))
        db.commit()
        db.close()

    @staticmethod
    def toggle_status(user_id):
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT status FROM users WHERE id=%s", (int(user_id),))
        row = cur.fetchone()
        if not row:
            db.close()
            return None

        status = row[0]
        new_status = "blocked" if status == "active" else "active"

        cur.execute("UPDATE users SET status=%s WHERE id=%s", (new_status, int(user_id)))
        db.commit()
        db.close()

        return new_status

    @staticmethod
    def update_basic(user_id, fullname, email):
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            UPDATE users SET fullname=%s, email=%s
            WHERE id=%s
        """, (fullname, email, int(user_id)))

        db.commit()
        db.close()
