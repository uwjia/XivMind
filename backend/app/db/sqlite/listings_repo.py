from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import sqlite3
import os
from contextlib import contextmanager
from app.db.base import ListingsRepository
from app.core.utils import safe_json_loads


class SQLiteListingsRepository(ListingsRepository):
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
                CREATE TABLE IF NOT EXISTS new_submissions (
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
                    journal_ref TEXT,
                    doi TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    listing_date TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_new_sub_fetched ON new_submissions(fetched_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_new_sub_listing ON new_submissions(listing_date)')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cross_submissions (
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
                    journal_ref TEXT,
                    doi TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    listing_date TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_sub_fetched ON cross_submissions(fetched_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cross_sub_listing ON cross_submissions(listing_date)')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS replacement_submissions (
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
                    journal_ref TEXT,
                    doi TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    listing_date TEXT
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_replacement_sub_fetched ON replacement_submissions(fetched_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_replacement_sub_listing ON replacement_submissions(listing_date)')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listings_date_index (
                    date TEXT PRIMARY KEY,
                    new_count INTEGER DEFAULT 0,
                    cross_count INTEGER DEFAULT 0,
                    replacement_count INTEGER DEFAULT 0,
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
            "authors": safe_json_loads(row["authors"], []),
            "primary_category": row["primary_category"] or "",
            "categories": safe_json_loads(row["categories"], []),
            "published": row["published"] or "",
            "updated": row["updated"] or "",
            "pdf_url": row["pdf_url"] or "",
            "abs_url": row["abs_url"] or "",
            "comment": row["comment"] or "",
            "journal_ref": row["journal_ref"] or "",
            "doi": row["doi"] or "",
            "fetched_at": row["fetched_at"] or "",
            "listing_date": row["listing_date"] or "",
        }

    def _listings_date_index_to_response(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "date": row["date"],
            "new_count": row["new_count"] or 0,
            "cross_count": row["cross_count"] or 0,
            "replacement_count": row["replacement_count"] or 0,
            "fetched_at": row["fetched_at"] or "",
        }

    def _prepare_paper_record(self, data: Dict[str, Any], listing_date: str = None) -> Tuple:
        now = datetime.utcnow().isoformat()
        return (
            self._safe_str(data.get("id"), 128),
            self._safe_str(data.get("title"), 2048),
            self._safe_str(data.get("abstract"), 32768),
            self._safe_str(json.dumps(data.get("authors") or []), 16384),
            self._safe_str(data.get("primary_category"), 64),
            self._safe_str(json.dumps(data.get("categories") or []), 2048),
            self._safe_str(data.get("published"), 64),
            self._safe_str(data.get("updated"), 64),
            self._safe_str(data.get("pdf_url"), 512),
            self._safe_str(data.get("abs_url"), 512),
            self._safe_str(data.get("comment"), 8192),
            self._safe_str(data.get("journal_ref"), 1024),
            self._safe_str(data.get("doi"), 256),
            now,
            listing_date or now[:10],
        )

    def _insert_submissions_batch(self, table_name: str, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        if not papers:
            return 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            inserted = 0
            
            for data in papers:
                record = self._prepare_paper_record(data, listing_date)
                try:
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO {table_name} 
                        (id, title, abstract, authors, primary_category, categories,
                         published, updated, pdf_url, abs_url, comment, journal_ref, doi, fetched_at, listing_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', record)
                    inserted += 1
                except Exception as e:
                    pass
            
            conn.commit()
            return inserted

    def insert_new_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        return self._insert_submissions_batch("new_submissions", papers, listing_date)

    def insert_cross_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        return self._insert_submissions_batch("cross_submissions", papers, listing_date)

    def insert_replacement_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        return self._insert_submissions_batch("replacement_submissions", papers, listing_date)

    def insert_listings_date_index(
        self,
        date: str,
        new_count: int,
        cross_count: int,
        replacement_count: int
    ) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO listings_date_index 
                (date, new_count, cross_count, replacement_count, fetched_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, new_count, cross_count, replacement_count, now))
            
            conn.commit()

    def get_listings_date_indexes(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, new_count, cross_count, replacement_count, fetched_at
                FROM listings_date_index
                ORDER BY date DESC
            ''')
            rows = cursor.fetchall()
            return [self._listings_date_index_to_response(row) for row in rows]

    def get_listings_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, new_count, cross_count, replacement_count, fetched_at
                FROM listings_date_index
                WHERE date = ?
            ''', (date,))
            row = cursor.fetchone()
            if row:
                return self._listings_date_index_to_response(row)
            return None

    def get_latest_listings_date_index(self) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, new_count, cross_count, replacement_count, fetched_at
                FROM listings_date_index
                ORDER BY date DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                return self._listings_date_index_to_response(row)
            return None

    def _get_submissions_by_date(
        self,
        table_name: str,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT COUNT(*) FROM {table_name}
                WHERE listing_date = ?
            ''', (date,))
            total = cursor.fetchone()[0]
            
            cursor.execute(f'''
                SELECT id, title, abstract, authors, primary_category, categories,
                       published, updated, pdf_url, abs_url, comment, journal_ref, doi, fetched_at, listing_date
                FROM {table_name}
                WHERE listing_date = ?
                ORDER BY published DESC
                LIMIT ? OFFSET ?
            ''', (date, max_results, start))
            
            rows = cursor.fetchall()
            results = [self._row_to_response(row) for row in rows]
            return results, total

    def get_new_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        return self._get_submissions_by_date("new_submissions", date, start, max_results)

    def get_cross_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        return self._get_submissions_by_date("cross_submissions", date, start, max_results)

    def get_replacement_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        return self._get_submissions_by_date("replacement_submissions", date, start, max_results)

    def clear_listings_by_date(self, date: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM new_submissions WHERE listing_date = ?', (date,))
            cursor.execute('DELETE FROM cross_submissions WHERE listing_date = ?', (date,))
            cursor.execute('DELETE FROM replacement_submissions WHERE listing_date = ?', (date,))
            cursor.execute('DELETE FROM listings_date_index WHERE date = ?', (date,))
            
            conn.commit()
