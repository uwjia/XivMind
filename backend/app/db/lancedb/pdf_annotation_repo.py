import json
import logging
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import PdfAnnotationRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBPdfAnnotationRepository(PdfAnnotationRepository):
    """LanceDB implementation for PDF annotation storage."""
    
    def __init__(self):
        self._annotations_table = None
        self._progress_table = None
    
    def _get_annotations_table(self):
        if self._annotations_table is None:
            self._annotations_table = lancedb_client.get_table("pdf_annotations")
        return self._annotations_table
    
    def _get_progress_table(self):
        if self._progress_table is None:
            self._progress_table = lancedb_client.get_table("pdf_reading_progress")
        return self._progress_table
    
    def _entity_to_annotation(self, row) -> Dict[str, Any]:
        result = {
            "id": row.get("id", ""),
            "paper_id": row.get("paper_id", ""),
            "type": row.get("type", ""),
            "page_number": row.get("page_number", 0),
            "position": json.loads(row.get("position", "{}")) if row.get("position") else {},
            "content": row.get("content"),
            "color": row.get("color", ""),
            "created_at": row.get("created_at", ""),
            "updated_at": row.get("updated_at", ""),
        }
        stroke_width = row.get("stroke_width")
        if stroke_width is not None and not (isinstance(stroke_width, float) and math.isnan(stroke_width)):
            result["stroke_width"] = stroke_width
        return result
    
    def get_annotations(self, paper_id: str) -> List[Dict[str, Any]]:
        table = self._get_annotations_table()
        
        if table.count_rows() == 0:
            return []
        
        try:
            import lance
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=[
                    "id", "paper_id", "type", "page_number", "position",
                    "content", "color", "stroke_width", "created_at", "updated_at"
                ],
                filter=f"paper_id = '{paper_id}'",
            )
            df = scanner.to_table().to_pandas()
            df_sorted = df.sort_values(by=["page_number", "created_at"])
            return [self._entity_to_annotation(row) for _, row in df_sorted.iterrows()]
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner, falling back to pandas: {e}")
            df = table.to_pandas()
            if df.empty:
                return []
            filtered = df[df["paper_id"] == paper_id]
            filtered_sorted = filtered.sort_values(by=["page_number", "created_at"])
            return [self._entity_to_annotation(row) for _, row in filtered_sorted.iterrows()]
    
    def create_annotation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        table = self._get_annotations_table()
        annotation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        record = {
            "id": annotation_id,
            "paper_id": data["paper_id"],
            "type": data["type"],
            "page_number": data["page_number"],
            "position": json.dumps(data["position"]),
            "content": data.get("content") or "",
            "color": data["color"],
            "stroke_width": data.get("stroke_width"),
            "created_at": now,
            "updated_at": now,
            "embedding": [0.0] * 1536,
        }
        
        table.add([record])
        
        result = {
            "id": annotation_id,
            "paper_id": data["paper_id"],
            "type": data["type"],
            "page_number": data["page_number"],
            "position": data["position"],
            "content": data.get("content"),
            "color": data["color"],
            "created_at": now,
            "updated_at": now,
        }
        if data.get("stroke_width") is not None:
            result["stroke_width"] = data["stroke_width"]
        return result
    
    def get_annotation(self, annotation_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_annotations_table()
        results = table.search().where(f"id = '{annotation_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_annotation(results.iloc[0])
    
    def update_annotation(self, annotation_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return None
        
        now = datetime.utcnow().isoformat()
        position = data.get("position") or annotation["position"]
        content = data.get("content") if data.get("content") is not None else annotation.get("content")
        color = data.get("color") or annotation["color"]
        stroke_width = data.get("stroke_width") if data.get("stroke_width") is not None else annotation.get("stroke_width")
        
        table = self._get_annotations_table()
        
        record = {
            "id": annotation_id,
            "paper_id": annotation["paper_id"],
            "type": annotation["type"],
            "page_number": annotation["page_number"],
            "position": json.dumps(position),
            "content": content or "",
            "color": color,
            "stroke_width": stroke_width,
            "created_at": annotation["created_at"],
            "updated_at": now,
            "embedding": [0.0] * 1536,
        }
        
        table.merge_insert("id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute([record])
        
        return {
            "id": annotation_id,
            "paper_id": annotation["paper_id"],
            "type": annotation["type"],
            "page_number": annotation["page_number"],
            "position": position,
            "content": content,
            "color": color,
            "stroke_width": stroke_width,
            "created_at": annotation["created_at"],
            "updated_at": now,
        }
    
    def delete_annotation(self, annotation_id: str) -> bool:
        table = self._get_annotations_table()
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return False
        table.delete(f"id = '{annotation_id}'")
        return True
    
    def get_reading_progress(self, paper_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_progress_table()
        results = table.search().where(f"paper_id = '{paper_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        row = results.iloc[0]
        return {
            "paper_id": row.get("paper_id", ""),
            "current_page": row.get("current_page", 1),
            "total_pages": row.get("total_pages"),
            "zoom_level": row.get("zoom_level", 1.0),
            "view_mode": row.get("view_mode", "continuous"),
            "last_read_at": row.get("last_read_at", ""),
        }
    
    def save_reading_progress(
        self,
        paper_id: str,
        current_page: int,
        total_pages: int,
        zoom_level: float,
        view_mode: str,
    ) -> Dict[str, Any]:
        table = self._get_progress_table()
        now = datetime.utcnow().isoformat()
        
        record = {
            "paper_id": paper_id,
            "current_page": current_page,
            "total_pages": total_pages,
            "zoom_level": zoom_level,
            "view_mode": view_mode,
            "last_read_at": now,
            "embedding": [0.0] * 1536,
        }
        
        table.merge_insert("paper_id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute([record])
        
        return {
            "paper_id": paper_id,
            "current_page": current_page,
            "total_pages": total_pages,
            "zoom_level": zoom_level,
            "view_mode": view_mode,
            "last_read_at": now,
        }
