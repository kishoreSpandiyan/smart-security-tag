"""
Smart Security Tag System — Database Initializer
Run once: python init_db.py
Creates database.db with payments and tamper_logs tables.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            amount       INTEGER NOT NULL,
            status       TEXT NOT NULL,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tamper_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message    TEXT NOT NULL,
            timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[OK] Database initialized at {DB_PATH}")
    print("[OK] Tables created: payments, tamper_logs")


if __name__ == "__main__":
    init_database()
