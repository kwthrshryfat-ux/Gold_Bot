"""ذخیره تاریخچه قیمت و تحلیل‌ها در یک دیتابیس SQLite محلی."""

import sqlite3
from datetime import datetime

from config import DB_PATH


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                price REAL NOT NULL,
                rsi REAL NOT NULL,
                macd REAL NOT NULL,
                macd_signal REAL NOT NULL,
                sma20 REAL NOT NULL,
                sma50 REAL NOT NULL
            )
            """
        )
        conn.commit()


def save_snapshot(symbol: str, snap) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO price_history
                (symbol, requested_at, price, rsi, macd, macd_signal, sma20, sma50)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol,
                datetime.utcnow().isoformat(timespec="seconds"),
                snap.price,
                snap.rsi,
                snap.macd,
                snap.macd_signal,
                snap.sma20,
                snap.sma50,
            ),
        )
        conn.commit()


def get_recent_history(symbol: str, limit: int = 5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            SELECT requested_at, price, rsi
            FROM price_history
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (symbol, limit),
        )
        return cursor.fetchall()
