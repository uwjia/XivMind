import json
import logging
from typing import Any, Dict, Iterator, List, Optional

from app.db.base import PaperReader
from app.db.milvus.client import milvus_client, Collection
from app.core.utils import safe_json_loads

logger = logging.getLogger(__name__)


class MilvusPaperReader(PaperReader):
    """Milvus paper data reader."""

    def __init__(self):
        self._papers_collection: Optional[Collection] = None

    def _get_papers_collection(self) -> Collection:
        if not self._papers_collection:
            self._papers_collection = milvus_client.get_collection("papers")
        return self._papers_collection

    def get_total_count(self) -> int:
        """Get total paper count."""
        collection = self._get_papers_collection()
        collection.load()
        return collection.num_entities

    def iter_papers_batch(
        self,
        batch_size: int = 10000,
        columns: Optional[List[str]] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Stream paper data in batches.

        Uses Milvus query with pagination for batch reading.
        """
        collection = self._get_papers_collection()
        collection.load()
        total = collection.num_entities

        if total == 0:
            return

        if columns is None:
            columns = ["id", "title", "authors", "primary_category", "published"]

        offset = 0

        while offset < total:
            try:
                results = collection.query(
                    expr='id != ""',
                    output_fields=columns,
                    limit=batch_size,
                    offset=offset,
                )

                if not results:
                    break

                papers = []
                for row in results:
                    authors = safe_json_loads(row.get("authors"), [])

                    papers.append({
                        "id": row.get("id", ""),
                        "title": row.get("title", ""),
                        "authors": authors,
                        "primary_category": row.get("primary_category", ""),
                        "published": row.get("published", ""),
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
