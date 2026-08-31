"""SQLite database for tracking downloaded files and preventing duplicates."""

import sqlite3
import hashlib
from pathlib import Path
from typing import Optional


class DownloadDB:
    """SQLite-backed deduplication and history tracker."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS downloads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        file_path TEXT,
        file_size INTEGER,
        file_hash TEXT,
        post_id TEXT,
        creator_id TEXT,
        service TEXT,
        domain TEXT,
        downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'completed'
    );
    CREATE INDEX IF NOT EXISTS idx_url ON downloads(url);
    CREATE INDEX IF NOT EXISTS idx_post ON downloads(post_id);
    CREATE INDEX IF NOT EXISTS idx_creator ON downloads(creator_id);
    """

    def __init__(self, db_path: str = "./coomertool.db"):
        self.db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()

    def is_downloaded(self, url: str) -> bool:
        """Check if a URL has already been successfully downloaded."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT 1 FROM downloads WHERE url = ? AND status = 'completed' LIMIT 1",
                (url,),
            )
            return cur.fetchone() is not None

    def record_download(
        self,
        url: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        file_hash: Optional[str] = None,
        post_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        service: Optional[str] = None,
        domain: Optional[str] = None,
        status: str = "completed",
    ) -> None:
        """Record a download attempt in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO downloads (url, file_path, file_size, file_hash, post_id, creator_id, service, domain, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    file_path=excluded.file_path,
                    file_size=excluded.file_size,
                    file_hash=excluded.file_hash,
                    status=excluded.status,
                    downloaded_at=CURRENT_TIMESTAMP
                """,
                (url, file_path, file_size, file_hash, post_id, creator_id, service, domain, status),
            )
            conn.commit()

    def get_stats(self) -> dict:
        """Return download statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
            completed = conn.execute("SELECT COUNT(*) FROM downloads WHERE status = 'completed'").fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM downloads WHERE status = 'failed'").fetchone()[0]
            total_size = conn.execute("SELECT COALESCE(SUM(file_size), 0) FROM downloads WHERE status = 'completed'").fetchone()[0]
            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "total_size": total_size,
            }

    def reset(self) -> None:
        """Clear all records. Use with caution."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM downloads")
            conn.commit()


def compute_hash(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()
