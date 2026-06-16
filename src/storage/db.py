from __future__ import annotations
import json, sqlite3
from pathlib import Path
from src.models import ReviewItem, SourceRunStatus
from src.normalize.dedupe import review_key

SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, review_key TEXT UNIQUE, artist TEXT, album TEXT, review_source TEXT, review_url TEXT, review_date TEXT, status TEXT, payload_json TEXT, first_seen_at TEXT, last_seen_at TEXT);
CREATE TABLE IF NOT EXISTS source_runs (id INTEGER PRIMARY KEY, source_name TEXT, status TEXT, items_found INTEGER, items_parsed INTEGER, items_failed INTEGER, error_message TEXT, last_success_at TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""

def connect(path: str | Path = "data/album_reviews.sqlite"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn=sqlite3.connect(path); conn.executescript(SCHEMA); return conn

def upsert_reviews(conn, items: list[ReviewItem]):
    for item in items:
        key = review_key(item.review_source, item.review_url, f"{item.artist} {item.album}", str(item.review_date or ""))
        data=item.to_dict()
        conn.execute("INSERT INTO reviews(review_key,artist,album,review_source,review_url,review_date,status,payload_json,first_seen_at,last_seen_at) VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) ON CONFLICT(review_key) DO UPDATE SET last_seen_at=CURRENT_TIMESTAMP,payload_json=excluded.payload_json,status=excluded.status", (key,item.artist,item.album,item.review_source,item.review_url,str(item.review_date or ""),item.status,json.dumps(data,ensure_ascii=False)))
    conn.commit()

def insert_source_statuses(conn, statuses: list[SourceRunStatus]):
    for s in statuses:
        conn.execute("INSERT INTO source_runs(source_name,status,items_found,items_parsed,items_failed,error_message,last_success_at) VALUES(?,?,?,?,?,?,datetime('now'))", (s.source_name,s.status,s.items_found,s.items_parsed,s.items_failed,s.error_message))
    conn.commit()

def load_reviews(conn):
    return [json.loads(r[0]) for r in conn.execute("SELECT payload_json FROM reviews")]
