import hashlib
import re
import sqlite3

from config import DB_PATH

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize(text):
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def dedup_key(listing):
    if listing.get("dedup_id"):
        # Sources with unstable/repeating titles (e.g. LinkedIn posts)
        # supply an explicit identity such as the post URL.
        normalized = _normalize(listing["dedup_id"])
    else:
        normalized = "|".join([
            _normalize(listing["company"]),
            _normalize(listing["title"]),
            _normalize(listing["location"]),
        ])
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class SeenStore:
    def __init__(self, db_path=None):
        self.conn = sqlite3.connect(db_path or DB_PATH)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS seen_jobs (key TEXT PRIMARY KEY, first_seen TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
        self.conn.commit()

    def is_new(self, key):
        cursor = self.conn.execute("SELECT 1 FROM seen_jobs WHERE key = ?", (key,))
        return cursor.fetchone() is None

    def mark_seen(self, key):
        self.conn.execute("INSERT OR IGNORE INTO seen_jobs (key) VALUES (?)", (key,))
        self.conn.commit()

    def close(self):
        self.conn.close()
