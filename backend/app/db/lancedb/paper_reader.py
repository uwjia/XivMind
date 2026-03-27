import json
import logging
from typing import Any, Dict, Iterator, List, Optional

import pyarrow as pa
from lance.dataset import ColumnOrdering

from app.db.base import PaperReader
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBPaperReader(PaperReader):
    """LanceDB paper data reader."""

    def __init__(self):
        self._papers_table = None

    def _get_papers_table(self):
        if self._papers_table is None:
            self._papers_table = lancedb_client.get_table("papers")
        return self._papers_table

    def get_total_count(self) -> int:
        """Get total paper count."""
        table = self._get_papers_table()
        return table.count_rows()

    def iter_papers_batch(
        self,
        batch_size: int = 10000,
        columns: Optional[List[str]] = None,
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Stream paper data in batches.

        Uses LanceDB scanner for efficient paginated reading.
        """
        table = self._get_papers_table()
        total = table.count_rows()

        if total == 0:
            return

        if columns is None:
            columns = ["id", "title", "authors", "primary_category", "published"]

        offset = 0
        lance_ds = table.to_lance()

        while offset < total:
            try:
                scanner = lance_ds.scanner(
                    columns=columns,
                    limit=batch_size,
                    offset=offset,
                    order_by=[ColumnOrdering("published", ascending=False)],
                )
                df = scanner.to_table().to_pandas()

                if len(df) == 0:
                    break

                papers = []
                for _, row in df.iterrows():
                    authors = []
                    try:
                        authors_str = row.get("authors", "")
                        if authors_str:
                            authors = json.loads(authors_str)
                            if not isinstance(authors, list):
                                authors = []
                    except (json.JSONDecodeError, TypeError):
                        authors = []

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
