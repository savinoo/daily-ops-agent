from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from daily_ops_agent.infra.settings import settings


def init_db() -> None:
    with sqlite3.connect(settings.sqlite_path) as conn:
        # Use executescript because SQLite `execute()` only supports a single statement at a time.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS decision_memory (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              day TEXT,
              decision TEXT NOT NULL,
              outcome TEXT
            );

            CREATE TABLE IF NOT EXISTS page_hashes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              url TEXT NOT NULL,
              content_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_metrics (
              day TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              revenue REAL NOT NULL,
              orders INTEGER NOT NULL,
              sessions INTEGER NOT NULL,
              meta_spend REAL NOT NULL,
              meta_revenue REAL NOT NULL,
              google_spend REAL NOT NULL,
              google_revenue REAL NOT NULL
            );
            """
        )
        conn.commit()


@contextmanager
def db_conn():
    init_db()
    conn = sqlite3.connect(settings.sqlite_path)
    try:
        yield conn
    finally:
        conn.close()
