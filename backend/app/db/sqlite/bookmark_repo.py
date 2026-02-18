from app.db.base import BookmarkRepository
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid
import json
import sqlite3
import os
from contextlib import contextmanager


class SQLiteBookmarkRepository(BookmarkRepository):
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
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id TEXT PRIMARY KEY,
                    paper_id TEXT UNIQUE NOT NULL,
                    arxiv_id TEXT,
                    title TEXT,
                    authors TEXT,
                    abstract TEXT,
                    comment TEXT,
                    journal_ref TEXT,
                    doi TEXT,
                    primary_category TEXT,
                    categories TEXT,
                    pdf_url TEXT,
                    abs_url TEXT,
                    published TEXT,
                    updated TEXT,
                    created_at TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_paper_id ON bookmarks(paper_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at)')
            
            cursor.execute("PRAGMA table_info(bookmarks)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'journal_ref' not in columns:
                cursor.execute('ALTER TABLE bookmarks ADD COLUMN journal_ref TEXT')
            if 'doi' not in columns:
                cursor.execute('ALTER TABLE bookmarks ADD COLUMN doi TEXT')
            
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
            "arxiv_id": row["arxiv_id"] or "",
            "title": row["title"] or "",
            "authors": json.loads(row["authors"]) if row["authors"] else [],
            "abstract": row["abstract"] or "",
            "comment": row["comment"] or "",
            "journal_ref": row["journal_ref"] or "",
            "doi": row["doi"] or "",
            "primary_category": row["primary_category"] or "",
            "categories": json.loads(row["categories"]) if row["categories"] else [],
            "pdf_url": row["pdf_url"] or "",
            "abs_url": row["abs_url"] or "",
            "published": row["published"] or "",
            "updated": row["updated"] or "",
            "created_at": row["created_at"] or "",
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        bookmark_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        title = self._safe_str(data.get("title"), 1024)
        abstract = self._safe_str(data.get("abstract"), 16384)
        comment = self._safe_str(data.get("comment"), 4096)
        journal_ref = self._safe_str(data.get("journal_ref"), 1024)
        doi = self._safe_str(data.get("doi"), 256)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookmarks (
                    id, paper_id, arxiv_id, title, authors, abstract, comment,
                    journal_ref, doi, primary_category, categories, 
                    pdf_url, abs_url, published, updated, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bookmark_id,
                self._safe_str(data.get("paper_id")),
                self._safe_str(data.get("arxiv_id")),
                title,
                json.dumps(data.get("authors") or []),
                abstract,
                comment,
                journal_ref,
                doi,
                self._safe_str(data.get("primary_category")),
                json.dumps(data.get("categories") or []),
                self._safe_str(data.get("pdf_url")),
                self._safe_str(data.get("abs_url")),
                self._safe_str(data.get("published")),
                self._safe_str(data.get("updated")),
                now,
            ))
            conn.commit()

        return {
            "id": bookmark_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "authors": data.get("authors") or [],
            "abstract": abstract,
            "comment": comment,
            "journal_ref": journal_ref,
            "doi": doi,
            "primary_category": self._safe_str(data.get("primary_category")),
            "categories": data.get("categories") or [],
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "abs_url": self._safe_str(data.get("abs_url")),
            "published": self._safe_str(data.get("published")),
            "updated": self._safe_str(data.get("updated")),
            "created_at": now,
        }

    def remove(self, id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bookmarks WHERE paper_id = ?', (id,))
            conn.commit()
            return cursor.rowcount > 0

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bookmarks WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
        return None

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM bookmarks')
            total = cursor.fetchone()[0]

            cursor.execute('''
                SELECT * FROM bookmarks ORDER BY created_at DESC LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows], total

    def exists(self, id: str) -> bool:
        return self.is_bookmarked(id)

    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bookmarks WHERE paper_id = ?', (paper_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
        return None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT * FROM bookmarks 
                WHERE paper_id LIKE ? OR title LIKE ? OR abstract LIKE ?
                ORDER BY created_at DESC LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit))
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows]

    def is_bookmarked(self, paper_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM bookmarks WHERE paper_id = ?', (paper_id,))
            return cursor.fetchone() is not None
