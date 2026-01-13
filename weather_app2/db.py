import sqlite3
from datetime import datetime

DB_NAME = "weather.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT,
            date TEXT,
            weather TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_forecast(area_code, date, weather):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO forecast (area_code, date, weather, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        area_code,
        date,
        weather,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_forecast_by_area(area_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT date, weather
        FROM forecast
        WHERE area_code = ?
        ORDER BY date ASC
    """, (area_code,))

    rows = cur.fetchall()
    conn.close()
    return rows

