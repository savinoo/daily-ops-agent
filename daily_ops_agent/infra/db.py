from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from daily_ops_agent.infra.settings import settings


def init_db() -> None:
    with sqlite3.connect(settings.sqlite_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_memory (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              day TEXT,
              decision TEXT NOT NULL,
              outcome TEXT
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
