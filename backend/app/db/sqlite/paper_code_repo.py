from app.db.base import PaperCodeRepository
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
import os
from contextlib import contextmanager


class SQLitePaperCodeRepository(PaperCodeRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_db_dir()
        self._init_tables()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self._db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS paper_codes (
                    id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    platform TEXT,
                    owner TEXT,
                    repo TEXT,
                    is_official INTEGER DEFAULT 1,
                    stars INTEGER DEFAULT 0,
                    language TEXT,
                    fetched_at TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_paper_codes_paper_id ON paper_codes(paper_id)')
            conn.commit()

    @staticmethod
    def _safe_str(value, max_len=None) -> str:
        if value is None:
            return ""
        s = str(value)
        return s[:max_len] if max_len else s

    def _row_to_response(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "paper_id": row["paper_id"],
            "url": row["url"],
            "platform": row["platform"] or "",
            "owner": row["owner"] or "",
            "repo": row["repo"] or "",
            "is_official": bool(row["is_official"]),
            "stars": row["stars"] or 0,
            "language": row["language"] or "",
            "fetched_at": row["fetched_at"] or "",
        }

    def upsert_paper_codes(self, codes: List[Dict[str, Any]]) -> int:
        if not codes:
            return 0
        
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            
            for code in codes:
                paper_id = self._safe_str(code.get("paper_id"))
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO paper_codes 
                        (id, paper_id, url, platform, owner, repo, is_official, stars, language, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        paper_id,
                        paper_id,
                        self._safe_str(code.get("url")),
                        self._safe_str(code.get("platform")),
                        self._safe_str(code.get("owner")),
                        self._safe_str(code.get("repo")),
                        1 if code.get("is_official", True) else 0,
                        code.get("stars", 0) or 0,
                        self._safe_str(code.get("language")),
                        self._safe_str(code.get("fetched_at") or now),
                    ))
                    count += 1
                except Exception:
                    pass
            
            conn.commit()
            return count

    def get_code_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM paper_codes WHERE id = ?',
                (paper_id,)
            )
            row = cursor.fetchone()
            return self._row_to_response(row) if row else None

    def get_paper_ids_with_code(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT paper_id FROM paper_codes')
            return [row[0] for row in cursor.fetchall()]

    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        if not paper_ids:
            return {}
        
        result = {pid: False for pid in paper_ids}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(paper_ids))
            cursor.execute(
                f'SELECT DISTINCT id FROM paper_codes WHERE id IN ({placeholders})',
                paper_ids
            )
            for row in cursor.fetchall():
                if row[0] in result:
                    result[row[0]] = True
        
        return result

    def get_codes_by_paper_ids(self, paper_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        if not paper_ids:
            return {}
        
        result = {pid: None for pid in paper_ids}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(paper_ids))
            cursor.execute(
                f'SELECT * FROM paper_codes WHERE id IN ({placeholders})',
                paper_ids
            )
            for row in cursor.fetchall():
                paper_id = row["id"]
                if paper_id in result:
                    result[paper_id] = self._row_to_response(row)
        
        return result
