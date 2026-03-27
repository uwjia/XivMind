import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from lance.dataset import ColumnOrdering

from app.db.base import AuthorRankRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBAuthorRankRepository(AuthorRankRepository):
    """LanceDB implementation of author ranking repository."""

    TABLE_NAME = "author_ranks"
    STATS_TABLE_NAME = "author_analysis_stats"

    def __init__(self):
        self._table = None
        self._stats_table = None

    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table(self.TABLE_NAME)
        return self._table

    def _get_stats_table(self):
        if self._stats_table is None:
            self._stats_table = lancedb_client.get_table(self.STATS_TABLE_NAME)
        return self._stats_table

    def save_rankings(
        self,
        authors: Dict[str, Any],
        metrics: Dict[str, Dict[str, float]],
    ) -> int:
        """Save author ranking data."""
        table = self._get_table()
        if table is None:
            return 0

        now = datetime.utcnow().isoformat()

        records = []
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

            records.append({
                "author_id": author_id,
                "name": name,
                "paper_count": paper_count,
                "pagerank": metrics['pagerank'].get(author_id, 0.0),
                "degree_centrality": metrics['degree'].get(author_id, 0.0),
                "betweenness_centrality": metrics['betweenness'].get(author_id, 0.0),
                "clustering_coeff": metrics['clustering'].get(author_id, 0.0),
                "primary_category": primary_cat,
                "first_year": first_year,
                "latest_year": latest_year,
                "collaborator_count": collaborator_count,
                "calculated_at": now,
                "embedding": [0.0] * 8,
            })

        if records:
            table.merge_insert("author_id") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute(records)

            logger.info(f"Saved {len(records)} author ranking records")

        return len(records)

    def get_top_authors(
        self,
        metric: str = "pagerank",
        limit: int = 100,
        offset: int = 0,
        category: Optional[str] = None,
        name_search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get top-ranked authors with pagination and optional name search."""
        try:
            table = self._get_table()

            if table is None:
                logger.warning("author_ranks table does not exist")
                return []

            lance_ds = table.to_lance()

            columns = [
                "author_id", "name", "paper_count", "pagerank",
                "degree_centrality", "betweenness_centrality", "clustering_coeff",
                "primary_category", "first_year", "latest_year", "collaborator_count",
                "calculated_at"
            ]

            filters = []
            if category:
                filters.append(f"primary_category = '{category}'")
            if name_search:
                safe_search = self._escape_filter_string(name_search)
                filters.append(f"name LIKE '%{safe_search}%'")
            
            scanner_kwargs = {
                "columns": columns,
                "limit": limit,
                "offset": offset,
                "order_by": [ColumnOrdering(metric, ascending=False)],
            }

            if filters:
                scanner_kwargs["filter"] = " AND ".join(filters)

            scanner = lance_ds.scanner(**scanner_kwargs)
            df = scanner.to_table().to_pandas()

            if len(df) == 0:
                return []

            records = df.to_dict('records')

            for record in records:
                if 'embedding' in record and hasattr(record['embedding'], 'tolist'):
                    record['embedding'] = record['embedding'].tolist()

            return records
        except Exception as e:
            logger.error(f"Failed to get top authors: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _escape_filter_string(self, value: str) -> str:
        if not value:
            return value
        result = value.replace('\\', '\\\\')
        result = result.replace('"', '\\"')
        result = result.replace("'", "\\'")
        return result

    def get_author_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author by ID."""
        table = self._get_table()

        if table is None:
            return None

        try:
            df = table.search().where(f"author_id = '{author_id}'").limit(1).to_pandas()
            if len(df) == 0:
                return None
            record = df.iloc[0].to_dict()
            if 'embedding' in record and hasattr(record['embedding'], 'tolist'):
                record['embedding'] = record['embedding'].tolist()
            return record
        except Exception as e:
            logger.error(f"Failed to get author: {e}")
            return None

    def count_authors(self, category: Optional[str] = None, name_search: Optional[str] = None) -> int:
        """Get total author count, optionally filtered by category and/or name."""
        table = self._get_table()
        if table is None:
            return 0
        
        filters = []
        if category:
            filters.append(f"primary_category = '{category}'")
        if name_search:
            safe_search = self._escape_filter_string(name_search)
            filters.append(f"name LIKE '%{safe_search}%'")
        
        if filters:
            try:
                lance_ds = table.to_lance()
                scanner = lance_ds.scanner(
                    columns=["author_id"],
                    filter=" AND ".join(filters),
                )
                return scanner.to_table().num_rows
            except Exception as e:
                logger.error(f"Failed to count authors with filters: {e}")
                return 0
        
        return table.count_rows()

    def clear_all(self) -> None:
        """Clear all ranking data."""
        table = self._get_table()
        if table is None:
            return
        try:
            df = table.to_pandas()
            for _, row in df.iterrows():
                table.delete(f"author_id = '{row['author_id']}'")
            logger.info("Cleared all author ranking data")
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")

    def get_disambiguation_stats(self) -> Dict[str, Any]:
        """Get disambiguation statistics."""
        stats_table = self._get_stats_table()
        if stats_table is None:
            return {}

        try:
            df = stats_table.search().where("key = 'disambiguation_stats'").limit(1).to_pandas()
            if len(df) == 0:
                return {}
            return json.loads(df.iloc[0]['value'])
        except Exception as e:
            logger.error(f"Failed to get disambiguation stats: {e}")
            return {}

    def save_disambiguation_stats(self, stats: Dict[str, Any]) -> None:
        """Save disambiguation statistics."""
        stats_table = self._get_stats_table()
        if stats_table is None:
            return

        try:
            now = datetime.utcnow().isoformat()
            record = {
                "key": "disambiguation_stats",
                "value": json.dumps(stats),
                "updated_at": now,
            }
            stats_table.merge_insert("key") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute([record])
            logger.info("Saved disambiguation stats")
        except Exception as e:
            logger.error(f"Failed to save disambiguation stats: {e}")
