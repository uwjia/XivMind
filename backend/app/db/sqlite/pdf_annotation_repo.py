from app.db.base import PdfAnnotationRepository
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json
import sqlite3
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SQLitePdfAnnotationRepository(PdfAnnotationRepository):
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
                CREATE TABLE IF NOT EXISTS pdf_annotations (
                    id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    position TEXT NOT NULL,
                    content TEXT,
                    color TEXT NOT NULL,
                    stroke_width INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_annotations_paper_id ON pdf_annotations(paper_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_annotations_page ON pdf_annotations(paper_id, page_number)')
            
            self._migrate_annotations_table(conn)
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pdf_reading_progress (
                    paper_id TEXT PRIMARY KEY,
                    current_page INTEGER DEFAULT 1,
                    total_pages INTEGER,
                    zoom_level REAL DEFAULT 1.0,
                    view_mode TEXT DEFAULT 'continuous',
                    last_read_at TEXT NOT NULL
                )
            ''')
            conn.commit()

    def _migrate_annotations_table(self, conn):
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(pdf_annotations)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if 'stroke_width' not in columns:
            logger.info("Migrating pdf_annotations table: adding stroke_width column")
            cursor.execute("ALTER TABLE pdf_annotations ADD COLUMN stroke_width INTEGER")
            conn.commit()
            logger.info("Migration completed: stroke_width column added")

    def _row_to_annotation(self, row: sqlite3.Row) -> Dict[str, Any]:
        result = {
            "id": row["id"],
            "paper_id": row["paper_id"],
            "type": row["type"],
            "page_number": row["page_number"],
            "position": json.loads(row["position"]),
            "content": row["content"],
            "color": row["color"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        if "stroke_width" in row.keys() and row["stroke_width"] is not None:
            result["stroke_width"] = row["stroke_width"]
        return result

    def get_annotations(self, paper_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pdf_annotations WHERE paper_id = ? ORDER BY page_number, created_at",
                (paper_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_annotation(row) for row in rows]

    def create_annotation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        annotation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pdf_annotations (id, paper_id, type, page_number, position, content, color, stroke_width, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    annotation_id,
                    data["paper_id"],
                    data["type"],
                    data["page_number"],
                    json.dumps(data["position"]),
                    data.get("content"),
                    data["color"],
                    data.get("stroke_width"),
                    now,
                    now,
                )
            )
            conn.commit()
        
        return self.get_annotation(annotation_id)

    def get_annotation(self, annotation_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pdf_annotations WHERE id = ?",
                (annotation_id,)
            )
            row = cursor.fetchone()
            return self._row_to_annotation(row) if row else None

    def update_annotation(self, annotation_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return None
        
        now = datetime.utcnow().isoformat()
        position = data.get("position") or annotation["position"]
        content = data.get("content") if data.get("content") is not None else annotation.get("content")
        color = data.get("color") or annotation["color"]
        stroke_width = data.get("stroke_width") if data.get("stroke_width") is not None else annotation.get("stroke_width")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE pdf_annotations 
                SET position = ?, content = ?, color = ?, stroke_width = ?, updated_at = ?
                WHERE id = ?
                """,
                (json.dumps(position), content, color, stroke_width, now, annotation_id)
            )
            conn.commit()
        
        return self.get_annotation(annotation_id)

    def delete_annotation(self, annotation_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM pdf_annotations WHERE id = ?",
                (annotation_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_reading_progress(self, paper_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pdf_reading_progress WHERE paper_id = ?",
                (paper_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "paper_id": row["paper_id"],
                    "current_page": row["current_page"],
                    "total_pages": row["total_pages"],
                    "zoom_level": row["zoom_level"],
                    "view_mode": row["view_mode"],
                    "last_read_at": row["last_read_at"],
                }
            return None

    def save_reading_progress(
        self,
        paper_id: str,
        current_page: int,
        total_pages: int,
        zoom_level: float,
        view_mode: str,
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO pdf_reading_progress 
                (paper_id, current_page, total_pages, zoom_level, view_mode, last_read_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (paper_id, current_page, total_pages, zoom_level, view_mode, now)
            )
            conn.commit()
        
        return {
            "paper_id": paper_id,
            "current_page": current_page,
            "total_pages": total_pages,
            "zoom_level": zoom_level,
            "view_mode": view_mode,
            "last_read_at": now,
        }
