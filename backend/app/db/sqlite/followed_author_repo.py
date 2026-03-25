import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.db.base import FollowedAuthorRepository


class SQLiteFollowedAuthorRepository(FollowedAuthorRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_db_dir()
        self._init_tables()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self._db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS followed_authors (
                    id TEXT PRIMARY KEY,
                    author_name TEXT UNIQUE NOT NULL,
                    paper_count INTEGER DEFAULT 0,
                    latest_published TEXT,
                    notes TEXT,
                    followed_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_followed_authors_name 
                ON followed_authors(author_name)
            """)
            conn.commit()
        finally:
            conn.close()

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            author_id = str(uuid.uuid4())
            followed_at = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO followed_authors (id, author_name, paper_count, latest_published, notes, followed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                author_id,
                data["author_name"],
                data.get("paper_count", 0),
                data.get("latest_published"),
                data.get("notes"),
                followed_at,
            ))
            conn.commit()
            
            return self.get(author_id)
        finally:
            conn.close()

    def remove(self, id: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM followed_authors WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM followed_authors WHERE id = ?", (id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM followed_authors")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT * FROM followed_authors 
                ORDER BY followed_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows], total
        finally:
            conn.close()

    def exists(self, id: str) -> bool:
        return self.get(id) is not None

    def get_by_author_name(self, author_name: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM followed_authors WHERE author_name = ?", (author_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def is_followed(self, author_name: str) -> bool:
        return self.get_by_author_name(author_name) is not None

    def update_notes(self, author_name: str, notes: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE followed_authors SET notes = ? WHERE author_name = ?
            """, (notes, author_name))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_paper_info(self, author_name: str, paper_count: int, latest_published: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE followed_authors 
                SET paper_count = ?, latest_published = ? 
                WHERE author_name = ?
            """, (paper_count, latest_published, author_name))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
