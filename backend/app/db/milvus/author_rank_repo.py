import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import AuthorRankRepository
from app.db.milvus.client import milvus_client

logger = logging.getLogger(__name__)


class MilvusAuthorRankRepository(AuthorRankRepository):
    """Milvus implementation of author ranking repository."""

    COLLECTION_NAME = "author_ranks"
    STATS_COLLECTION_NAME = "author_analysis_stats"

    def __init__(self):
        self._collection = None
        self._stats_collection = None

    def _get_collection(self):
        if self._collection is None:
            try:
                from pymilvus import Collection, FieldSchema, CollectionSchema, DataType
                
                fields = [
                    FieldSchema(name="author_id", dtype=DataType.VARCHAR, max_length=512, is_primary=True),
                    FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="paper_count", dtype=DataType.INT64),
                    FieldSchema(name="pagerank", dtype=DataType.DOUBLE),
                    FieldSchema(name="degree_centrality", dtype=DataType.DOUBLE),
                    FieldSchema(name="betweenness_centrality", dtype=DataType.DOUBLE),
                    FieldSchema(name="clustering_coeff", dtype=DataType.DOUBLE),
                    FieldSchema(name="primary_category", dtype=DataType.VARCHAR, max_length=256),
                    FieldSchema(name="first_year", dtype=DataType.INT64),
                    FieldSchema(name="latest_year", dtype=DataType.INT64),
                    FieldSchema(name="collaborator_count", dtype=DataType.INT64),
                    FieldSchema(name="calculated_at", dtype=DataType.VARCHAR, max_length=64),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=8),
                ]
                
                schema = CollectionSchema(fields=fields, description="Author ranking data")
                
                self._collection = milvus_client.get_or_create_collection(
                    self.COLLECTION_NAME,
                    schema=schema,
                )
                
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                }
                self._collection.create_index(field_name="embedding", index_params=index_params)
                
                logger.info(f"Got/created {self.COLLECTION_NAME} collection")
            except Exception as e:
                logger.error(f"Failed to get/create author_ranks collection: {e}")
                import traceback
                traceback.print_exc()
                return None
        return self._collection

    def _get_stats_collection(self):
        if self._stats_collection is None:
            try:
                from pymilvus import Collection, FieldSchema, CollectionSchema, DataType
                
                fields = [
                    FieldSchema(name="key", dtype=DataType.VARCHAR, max_length=256, is_primary=True),
                    FieldSchema(name="value", dtype=DataType.VARCHAR, max_length=4096),
                    FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
                ]
                
                schema = CollectionSchema(fields=fields, description="Author analysis stats")
                
                self._stats_collection = milvus_client.get_or_create_collection(
                    self.STATS_COLLECTION_NAME,
                    schema=schema,
                )
                
                logger.info(f"Got/created {self.STATS_COLLECTION_NAME} collection")
            except Exception as e:
                logger.error(f"Failed to get/create stats collection: {e}")
                return None
        return self._stats_collection

    def save_rankings(
        self,
        authors: Dict[str, Any],
        metrics: Dict[str, Dict[str, float]],
    ) -> int:
        """Save author ranking data."""
        collection = self._get_collection()
        if collection is None:
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

            records.append([
                author_id,
                name,
                paper_count,
                metrics['pagerank'].get(author_id, 0.0),
                metrics['degree'].get(author_id, 0.0),
                metrics['betweenness'].get(author_id, 0.0),
                metrics['clustering'].get(author_id, 0.0),
                primary_cat,
                first_year,
                latest_year,
                collaborator_count,
                now,
                [0.0] * 8,
            ])

        if records:
            try:
                collection.delete(f'author_id in ["' + '","'.join([r[0] for r in records]) + '"]')
                collection.insert(records)
                collection.flush()
                logger.info(f"Saved {len(records)} author ranking records")
            except Exception as e:
                logger.error(f"Failed to save rankings: {e}")

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
        collection = self._get_collection()
        if collection is None:
            return []

        try:
            collection.load()
            
            filter_parts = []
            if category:
                filter_parts.append(f'primary_category == "{category}"')
            if name_search:
                filter_parts.append(f'name like "%{name_search}%"')
            
            filter_expr = " && ".join(filter_parts) if filter_parts else None
            
            results = collection.query(
                expr=filter_expr,
                output_fields=[
                    "author_id", "name", "paper_count", "pagerank",
                    "degree_centrality", "betweenness_centrality", "clustering_coeff",
                    "primary_category", "first_year", "latest_year", "collaborator_count",
                    "calculated_at"
                ],
                limit=limit,
                offset=offset,
            )
            
            sorted_results = sorted(results, key=lambda x: x.get(metric, 0), reverse=True)
            
            return sorted_results
        except Exception as e:
            logger.error(f"Failed to get top authors: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_author_by_id(self, author_id: str) -> Optional[Dict[str, Any]]:
        """Get author by ID."""
        collection = self._get_collection()
        if collection is None:
            return None

        try:
            collection.load()
            results = collection.query(
                expr=f'author_id == "{author_id}"',
                output_fields=[
                    "author_id", "name", "paper_count", "pagerank",
                    "degree_centrality", "betweenness_centrality", "clustering_coeff",
                    "primary_category", "first_year", "latest_year", "collaborator_count",
                    "calculated_at"
                ],
                limit=1,
            )
            if not results:
                return None
            return results[0]
        except Exception as e:
            logger.error(f"Failed to get author: {e}")
            return None

    def count_authors(self, category: Optional[str] = None, name_search: Optional[str] = None) -> int:
        """Get total author count, optionally filtered by category and/or name."""
        collection = self._get_collection()
        if collection is None:
            return 0
        try:
            collection.load()
            
            filter_parts = []
            if category:
                filter_parts.append(f'primary_category == "{category}"')
            if name_search:
                filter_parts.append(f'name like "%{name_search}%"')
            
            if filter_parts:
                results = collection.query(
                    expr=" && ".join(filter_parts),
                    output_fields=["author_id"],
                )
                return len(results)
            return collection.num_entities
        except Exception:
            return 0

    def clear_all(self) -> None:
        """Clear all ranking data."""
        collection = self._get_collection()
        if collection is None:
            return
        try:
            collection.delete("author_id != ''")
            collection.flush()
            logger.info("Cleared all author ranking data")
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")

    def get_disambiguation_stats(self) -> Dict[str, Any]:
        """Get disambiguation statistics."""
        stats_collection = self._get_stats_collection()
        if stats_collection is None:
            return {}

        try:
            stats_collection.load()
            results = stats_collection.query(
                expr='key == "disambiguation_stats"',
                output_fields=["key", "value", "updated_at"],
                limit=1,
            )
            if not results:
                return {}
            return json.loads(results[0]['value'])
        except Exception as e:
            logger.error(f"Failed to get disambiguation stats: {e}")
            return {}

    def save_disambiguation_stats(self, stats: Dict[str, Any]) -> None:
        """Save disambiguation statistics."""
        stats_collection = self._get_stats_collection()
        if stats_collection is None:
            return

        try:
            now = datetime.utcnow().isoformat()
            stats_collection.delete('key == "disambiguation_stats"')
            stats_collection.insert([["disambiguation_stats", json.dumps(stats), now]])
            stats_collection.flush()
            logger.info("Saved disambiguation stats")
        except Exception as e:
            logger.error(f"Failed to save disambiguation stats: {e}")
