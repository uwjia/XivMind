from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sqlite3
import os
from contextlib import contextmanager


class SQLitePaperRepository:
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
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    abstract TEXT,
                    authors TEXT,
                    primary_category TEXT,
                    categories TEXT,
                    published TEXT,
                    updated TEXT,
                    pdf_url TEXT,
                    abs_url TEXT,
                    comment TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_primary_cat ON papers(primary_category)')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS date_index (
                    date TEXT PRIMARY KEY,
                    total_count INTEGER,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
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
            "title": row["title"] or "",
            "abstract": row["abstract"] or "",
            "authors": json.loads(row["authors"]) if row["authors"] else [],
            "primary_category": row["primary_category"] or "",
            "categories": json.loads(row["categories"]) if row["categories"] else [],
            "published": row["published"] or "",
            "updated": row["updated"] or "",
            "pdf_url": row["pdf_url"] or "",
            "abs_url": row["abs_url"] or "",
            "comment": row["comment"] or "",
            "fetched_at": row["fetched_at"] or "",
        }

    def insert_paper(self, data: Dict[str, Any]) -> None:
        title = self._safe_str(data.get("title"), 2048)
        abstract = self._safe_str(data.get("abstract"), 32768)
        comment = self._safe_str(data.get("comment"), 8192)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO papers (
                    id, title, abstract, authors, primary_category, categories,
                    published, updated, pdf_url, abs_url, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self._safe_str(data.get("id")),
                title,
                abstract,
                json.dumps(data.get("authors") or []),
                self._safe_str(data.get("primary_category")),
                json.dumps(data.get("categories") or []),
                self._safe_str(data.get("published")),
                self._safe_str(data.get("updated")),
                self._safe_str(data.get("pdf_url")),
                self._safe_str(data.get("abs_url")),
                comment,
            ))
            conn.commit()

    def insert_papers_batch(self, papers: List[Dict[str, Any]]) -> int:
        inserted = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for data in papers:
                title = self._safe_str(data.get("title"), 2048)
                abstract = self._safe_str(data.get("abstract"), 32768)
                comment = self._safe_str(data.get("comment"), 8192)

                cursor.execute('''
                    INSERT OR IGNORE INTO papers (
                        id, title, abstract, authors, primary_category, categories,
                        published, updated, pdf_url, abs_url, comment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self._safe_str(data.get("id")),
                    title,
                    abstract,
                    json.dumps(data.get("authors") or []),
                    self._safe_str(data.get("primary_category")),
                    json.dumps(data.get("categories") or []),
                    self._safe_str(data.get("published")),
                    self._safe_str(data.get("updated")),
                    self._safe_str(data.get("pdf_url")),
                    self._safe_str(data.get("abs_url")),
                    comment,
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            conn.commit()
        return inserted

    def get_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM date_index WHERE date = ?', (date,))
            row = cursor.fetchone()
            if row:
                return {
                    "date": row["date"],
                    "total_count": row["total_count"],
                    "fetched_at": row["fetched_at"],
                }
        return None

    def insert_date_index(self, date: str, total_count: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO date_index (date, total_count, fetched_at)
                VALUES (?, ?, ?)
            ''', (date, total_count, datetime.utcnow().isoformat()))
            conn.commit()

    def query_papers_by_date(
        self, 
        date: str, 
        category: Optional[str] = None,
        start: int = 0, 
        max_results: int = 50
    ) -> tuple[List[Dict[str, Any]], int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                count_query = '''
                    SELECT COUNT(*) FROM papers 
                    WHERE date(published) = ? AND categories LIKE ?
                '''
                count_params = [date, f'%"{category}"%']
            else:
                count_query = 'SELECT COUNT(*) FROM papers WHERE date(published) = ?'
                count_params = [date]
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]
            
            if category:
                query = '''
                    SELECT * FROM papers 
                    WHERE date(published) = ? AND categories LIKE ?
                    ORDER BY published DESC
                    LIMIT ? OFFSET ?
                '''
                params = [date, f'%"{category}"%', max_results, start]
            else:
                query = '''
                    SELECT * FROM papers 
                    WHERE date(published) = ?
                    ORDER BY published DESC
                    LIMIT ? OFFSET ?
                '''
                params = [date, max_results, start]
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows], total

    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
        return None

    def delete_date_index(self, date: str) -> None:
        """Delete date index for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM date_index WHERE date = ?', (date,))
            conn.commit()

    def delete_all_date_index(self) -> None:
        """Delete all date index records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM date_index')
            conn.commit()

    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        """Get all date index records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM date_index ORDER BY date DESC')
            rows = cursor.fetchall()
            return [
                {
                    "date": row["date"],
                    "total_count": row["total_count"],
                    "fetched_at": row["fetched_at"],
                }
                for row in rows
            ]

    def get_total_paper_count(self) -> int:
        """Get total count of papers in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM papers')
            return cursor.fetchone()[0]
