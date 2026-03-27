import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import AuthorRankRepository
from app.config import get_settings

logger = logging.getLogger(__name__)


class SQLiteAuthorRankRepository(AuthorRankRepository):
    """SQLite implementation of author ranking repository."""

    TABLE_NAME = "author_ranks"
    STATS_TABLE_NAME = "author_analysis_stats"

    def __init__(self):
        self._db_path = self._get_db_path()
        self._init_tables()

    def _get_db_path(self) -> str:
        settings = get_settings()
        data_dir = getattr(settings, 'DATA_DIR', 'data')
        db_dir = os.path.join(data_dir, 'sqlite')
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, 'xivmind.db')

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
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                    author_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    paper_count INTEGER DEFAULT 0,
                    pagerank REAL DEFAULT 0.0,
                    degree_centrality REAL DEFAULT 0.0,
                    betweenness_centrality REAL DEFAULT 0.0,
                    clustering_coeff REAL DEFAULT 0.0,
                    primary_category TEXT,
                    first_year INTEGER,
                    latest_year INTEGER,
                    collaborator_count INTEGER DEFAULT 0,
                    calculated_at TEXT
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.STATS_TABLE_NAME} (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_author_ranks_pagerank 
                ON {self.TABLE_NAME}(pagerank DESC)
            """)
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_author_ranks_category 
                ON {self.TABLE_NAME}(primary_category)
            """)
            conn.commit()

    def save_rankings(
        self,
        authors: Dict[str, Any],
        metrics: Dict[str, Dict[str, float]],
    ) -> int:
        """Save author ranking data."""
        now = datetime.utcnow().isoformat()
        count = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()

            for author_id, stats in authors.items():
                primary_cat = ""
                if hasattr(stats, 'categories') and stats.categories:
                    primary_cat = max(stats.categories.items(), key=lambda x: x[1])[0]
                elif isinstance(stats, dict) and stats.get('categories'):
                    primary_cat = max(stats['categories'].items(), key=lambda x: x[1])[0]

                if hasattr(stats, 'display_name'):
                    name = stats.display_name
                    paper_count = stats.paper_count
                    first_year = stats.first_paper_year or 0
                    latest_year = stats.latest_paper_year or 0
                    collaborator_count = stats.collaborator_count
                else:
                    name = stats.get('display_name', author_id)
                    paper_count = stats.get('paper_count', 0)
                    first_year = stats.get('first_paper_year', 0) or 0
                    latest_year = stats.get('latest_paper_year', 0) or 0
                    collaborator_count = stats.get('collaborator_count', 0)

                cursor.execute(f"""
                    INSERT OR REPLACE INTO {self.TABLE_NAME} (
                        author_id, name, paper_count, pagerank, degree_centrality,
                        betweenness_centrality, clustering_coeff, primary_category,
                        first_year, latest_year, collaborator_count, calculated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    author_id, name, paper_count,
                    metrics['pagerank'].get(author_id, 0.0),
                    metrics['degree'].get(author_id, 0.0),
                    metrics['betweenness'].get(author_id, 0.0),
                    metrics['clustering'].get(author_id, 0.0),
                    primary_cat, first_year, latest_year, collaborator_count, now
                ))
                count += 1

            conn.commit()

        logger.info(f"Saved {count} author ranking records")
        return count

    def get_top_authors(
        self,
        metric: str = "pagerank",
        limit: int = 100,
        offset: int = 0,
        category: Optional[str] = None,
        name_search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get top-ranked authors with pagination and optional name search."""
        valid_metrics = ['pagerank', 'degree_centrality', 'betweenness_centrality', 
                         'paper_count', 'clustering_coeff']
        if metric not in valid_metrics:
            metric = 'pagerank'

        with self._get_connection() as conn:
            cursor = conn.cursor()

            conditions = []
            params = []
            
            if category:
                conditions.append("primary_category = ?")
                params.append(category)
            if name_search:
                conditions.append("name LIKE ?")
                params.append(f"%{name_search}%")
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            params.extend([limit, offset])
            
            cursor.execute(f"""
                SELECT author_id, name, paper_count, pagerank, degree_centrality,
                       betweenness_centrality, clustering_coeff, primary_category,
                       first_year, latest_year, collaborator_count, calculated_at
                FROM {self.TABLE_NAME}
                {where_clause}
                ORDER BY {metric} DESC
                LIMIT ? OFFSET ?
            """, params)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_author_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT author_id, name, paper_count, pagerank, degree_centrality,
                       betweenness_centrality, clustering_coeff, primary_category,
                       first_year, latest_year, collaborator_count, calculated_at
                FROM {self.TABLE_NAME}
                WHERE author_id = ?
            """, (author_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def count_authors(self, category: Optional[str] = None, name_search: Optional[str] = None) -> int:
        """Get total author count, optionally filtered by category and/or name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if category:
                conditions.append("primary_category = ?")
                params.append(category)
            if name_search:
                conditions.append("name LIKE ?")
                params.append(f"%{name_search}%")
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            cursor.execute(f"SELECT COUNT(*) FROM {self.TABLE_NAME} {where_clause}", params)
            return cursor.fetchone()[0]

    def clear_all(self) -> None:
        """Clear all ranking data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.TABLE_NAME}")
            conn.commit()
            logger.info("Cleared all author ranking data")

    def get_disambiguation_stats(self) -> Dict[str, Any]:
        """Get disambiguation statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT value FROM {self.STATS_TABLE_NAME}
                WHERE key = 'disambiguation_stats'
            """)
            row = cursor.fetchone()
            if row:
                return json.loads(row['value'])
            return {}

    def save_disambiguation_stats(self, stats: Dict[str, Any]) -> None:
        """Save disambiguation statistics."""
        now = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT OR REPLACE INTO {self.STATS_TABLE_NAME} (key, value, updated_at)
                VALUES (?, ?, ?)
            """, ('disambiguation_stats', json.dumps(stats), now))
            conn.commit()
            logger.info("Saved disambiguation stats")
