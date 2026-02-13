from app.db.base import DownloadRepository
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid
import sqlite3
import os
from contextlib import contextmanager


class SQLiteDownloadRepository(DownloadRepository):
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
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL,
                    arxiv_id TEXT,
                    title TEXT,
                    pdf_url TEXT,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    file_path TEXT,
                    file_size INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_paper_id ON downloads(paper_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_created_at ON downloads(created_at)')
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
            "pdf_url": row["pdf_url"] or "",
            "status": row["status"] or "pending",
            "progress": row["progress"] or 0,
            "file_path": row["file_path"] or "",
            "file_size": row["file_size"] or 0,
            "error_message": row["error_message"] or "",
            "created_at": row["created_at"] or "",
            "updated_at": row["updated_at"] or "",
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        title = self._safe_str(data.get("title"), 1024)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads (
                    id, paper_id, arxiv_id, title, pdf_url, status, progress,
                    file_path, file_size, error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id,
                self._safe_str(data.get("paper_id")),
                self._safe_str(data.get("arxiv_id")),
                title,
                self._safe_str(data.get("pdf_url")),
                "pending",
                0,
                "",
                0,
                "",
                now,
                now,
            ))
            conn.commit()

        return {
            "id": task_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "status": "pending",
            "progress": 0,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": now,
            "updated_at": now,
        }

    def remove(self, id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM downloads WHERE id = ?', (id,))
            conn.commit()
            return cursor.rowcount > 0

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM downloads WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
        return None

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM downloads')
            total = cursor.fetchone()[0]

            cursor.execute('''
                SELECT * FROM downloads ORDER BY created_at DESC LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows], total

    def exists(self, id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM downloads WHERE id = ?', (id,))
            return cursor.fetchone() is not None

    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM downloads WHERE paper_id = ? ORDER BY created_at DESC LIMIT 1', (paper_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
        return None

    def get_all_by_paper_id(self, paper_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM downloads WHERE paper_id = ? ORDER BY created_at DESC', (paper_id,))
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows]

    def update_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        file_path: Optional[str] = None,
        file_size: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM downloads WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            if not row:
                return False

            update_fields = ['status = ?', 'progress = ?', 'updated_at = ?']
            update_values = [status, progress, now]

            if file_path is not None:
                update_fields.append('file_path = ?')
                update_values.append(file_path)
            if file_size:
                update_fields.append('file_size = ?')
                update_values.append(file_size)
            if error_message is not None:
                update_fields.append('error_message = ?')
                update_values.append(error_message)

            update_values.append(task_id)
            
            cursor.execute(
                f'UPDATE downloads SET {", ".join(update_fields)} WHERE id = ?',
                update_values
            )
            conn.commit()
            return cursor.rowcount > 0

    def reset_incomplete_tasks(self) -> int:
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE downloads 
                SET status = 'failed', 
                    error_message = 'Download interrupted - please retry',
                    updated_at = ?
                WHERE status IN ('downloading', 'pending')
            ''', (now,))
            conn.commit()
            return cursor.rowcount
