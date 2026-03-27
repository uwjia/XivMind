import logging
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from app.config import get_settings
from app.db.base import PaperReader
from app.core.utils import safe_json_loads

logger = logging.getLogger(__name__)


class SQLitePaperReader(PaperReader):
    """SQLite paper data reader."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            settings = get_settings()
            self._db_path = settings.SQLITE_DB_PATH
        else:
            self._db_path = db_path

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_total_count(self) -> int:
        """Get total paper count."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers")
            return cursor.fetchone()[0]

    def iter_papers_batch(
        self,
        batch_size: int = 10000,
        columns: Optional[List[str]] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Stream paper data in batches.

        Uses SQLite cursor for efficient batch reading.
        """
        total = self.get_total_count()

        if total == 0:
            return

        if columns is None:
            columns = ["id", "title", "authors", "primary_category", "published"]

        column_str = ", ".join(columns)
        offset = 0

        while offset < total:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"""
                        SELECT {column_str} FROM papers
                        ORDER BY published DESC
                        LIMIT ? OFFSET ?
                        """,
                        (batch_size, offset),
                    )

                    rows = cursor.fetchall()

                    if not rows:
                        break

                    papers = []
                    for row in rows:
                        authors = safe_json_loads(row["authors"], [])

                        papers.append({
                            "id": row["id"],
                            "title": row["title"],
                            "authors": authors,
                            "primary_category": row["primary_category"] or "",
                            "published": row["published"] or "",
                        })

                    yield papers
                    offset += batch_size

                    logger.info(f"Read {min(offset, total)}/{total} papers...")

            except Exception as e:
                logger.error(f"Failed to read paper data: {e}")
                break

    def iter_all_papers(
        self,
        columns: Optional[List[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Iterate all papers one by one."""
        for batch in self.iter_papers_batch(batch_size=5000, columns=columns):
            for paper in batch:
                yield paper
