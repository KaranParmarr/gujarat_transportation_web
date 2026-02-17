import mysql.connector
from flask import current_app

def get_db():
    cfg = current_app.config

    return mysql.connector.connect(
        host=cfg.get("MYSQL_HOST", "localhost"),
        user=cfg.get("MYSQL_USER", "root"),
        password=cfg.get("MYSQL_PASSWORD", "karan@05"),
        database=cfg.get("MYSQL_DB", "gujarat_transport")
    )
