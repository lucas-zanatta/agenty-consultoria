import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "reviews.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id       TEXT PRIMARY KEY,
                location_name   TEXT NOT NULL,
                rating          INTEGER,
                author          TEXT,
                text            TEXT,
                created_at      TEXT,
                status          TEXT DEFAULT 'pending',
                draft_response  TEXT,
                final_response  TEXT,
                approval_token  TEXT UNIQUE,
                processed_at    TEXT
            )
        """)


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_review(review: dict):
    with _conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO reviews
                (review_id, location_name, rating, author, text, created_at, status)
            VALUES
                (:review_id, :location_name, :rating, :author, :text, :created_at, 'pending')
        """, review)


def get_pending() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reviews WHERE status = 'pending'"
        ).fetchall()
        return [dict(r) for r in rows]


def set_draft(review_id: str, draft: str) -> str:
    token = str(uuid.uuid4())
    with _conn() as conn:
        conn.execute("""
            UPDATE reviews
            SET status = 'draft_sent', draft_response = ?, approval_token = ?
            WHERE review_id = ?
        """, (draft, token, review_id))
    return token


def set_replied(review_id: str, response: str):
    with _conn() as conn:
        conn.execute("""
            UPDATE reviews
            SET status = 'replied', final_response = ?, processed_at = ?
            WHERE review_id = ?
        """, (response, datetime.utcnow().isoformat(), review_id))


def get_by_token(token: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM reviews WHERE approval_token = ? AND status = 'draft_sent'",
            (token,)
        ).fetchone()
        return dict(row) if row else None
