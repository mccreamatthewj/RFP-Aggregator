import sqlite3
from typing import List, Dict, Optional
import datetime
import os

DB_PATH = os.getenv("LOCAL_DB_PATH", "data/rfps.db")

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS rfps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    event_id TEXT,
    agency TEXT,
    description TEXT,
    due_date TEXT,
    url TEXT UNIQUE,
    contact_email TEXT,
    discovered_at TEXT
);
"""

def _get_conn(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    conn = _get_conn(db_path)
    conn.execute(CREATE_SQL)
    conn.commit()
    return conn

def upsert_rfps(items: List[Dict], db_path: str = DB_PATH) -> List[Dict]:
    """Insert new RFPs into DB. Returns list of newly-inserted items."""
    conn = _get_conn(db_path)
    conn.execute(CREATE_SQL)
    inserted = []
    now = datetime.datetime.utcnow().isoformat()
    for it in items:
        try:
            conn.execute(
                """
                INSERT INTO rfps (title, event_id, agency, description, due_date, url, contact_email, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    it.get("title"),
                    it.get("event_id"),
                    it.get("agency"),
                    it.get("description"),
                    it.get("due_date"),
                    it.get("url"),
                    it.get("contact_email"),
                    now,
                ),
            )
            inserted.append(it)
        except sqlite3.IntegrityError:
            # url UNIQUE constraint => already exists
            continue
    conn.commit()
    return inserted

def list_rfps(limit: Optional[int] = 500, db_path: str = DB_PATH) -> List[Dict]:
    conn = _get_conn(db_path)
    cur = conn.execute("SELECT * FROM rfps ORDER BY discovered_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]

def get_rfp_by_event_id(event_id: str, db_path: str = DB_PATH) -> Optional[Dict]:
    conn = _get_conn(db_path)
    cur = conn.execute("SELECT * FROM rfps WHERE event_id = ? LIMIT 1", (event_id,))
    r = cur.fetchone()
    return dict(r) if r else None
