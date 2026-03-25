from app.db.base import PdfAnnotationRepository
from app.db.milvus.client import milvus_client, Collection
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json


class MilvusPdfAnnotationRepository(PdfAnnotationRepository):
    def __init__(self):
        self._annotations_collection: Optional[Collection] = None
        self._progress_collection: Optional[Collection] = None

    def _get_annotations_collection(self) -> Collection:
        if not self._annotations_collection:
            self._annotations_collection = milvus_client.get_collection("pdf_annotations")
        return self._annotations_collection

    def _get_progress_collection(self) -> Collection:
        if not self._progress_collection:
            self._progress_collection = milvus_client.get_collection("pdf_reading_progress")
        return self._progress_collection

    def _entity_to_annotation(self, entity: Dict) -> Dict[str, Any]:
        position_str = entity.get("position")
        position = json.loads(position_str) if position_str else {}
        result = {
            "id": entity.get("id", ""),
            "paper_id": entity.get("paper_id", ""),
            "type": entity.get("type", ""),
            "page_number": entity.get("page_number", 0),
            "position": position,
            "content": entity.get("content"),
            "color": entity.get("color", ""),
            "created_at": entity.get("created_at", ""),
            "updated_at": entity.get("updated_at", ""),
        }
        stroke_width = entity.get("stroke_width")
        if stroke_width is not None:
            result["stroke_width"] = stroke_width
        return result

    def get_annotations(self, paper_id: str) -> List[Dict[str, Any]]:
        collection = self._get_annotations_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=[
                "id", "paper_id", "type", "page_number", "position",
                "content", "color", "stroke_width", "created_at", "updated_at"
            ],
        )
        sorted_results = sorted(
            results,
            key=lambda x: (x.get("page_number", 0), x.get("created_at", ""))
        )
        return [self._entity_to_annotation(r) for r in sorted_results]

    def create_annotation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_annotations_collection()
        annotation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        insert_data = [
            [annotation_id],
            [data["paper_id"]],
            [data["type"]],
            [data["page_number"]],
            [json.dumps(data["position"])],
            [data.get("content") or ""],
            [data["color"]],
            [data.get("stroke_width")],
            [now],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)
        collection.flush()

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
        collection = self._get_annotations_collection()
        collection.load()
        results = collection.query(
            expr=f'id == "{annotation_id}"',
            output_fields=[
                "id", "paper_id", "type", "page_number", "position",
                "content", "color", "stroke_width", "created_at", "updated_at"
            ]
        )
        if results:
            return self._entity_to_annotation(results[0])
        return None

    def update_annotation(self, annotation_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return None

        now = datetime.utcnow().isoformat()
        position = data.get("position") or annotation["position"]
        content = data.get("content") if data.get("content") is not None else annotation.get("content")
        color = data.get("color") or annotation["color"]
        stroke_width = data.get("stroke_width") if data.get("stroke_width") is not None else annotation.get("stroke_width")

        collection = self._get_annotations_collection()
        collection.load()
        collection.delete(f'id == "{annotation_id}"')
        collection.flush()

        insert_data = [
            [annotation_id],
            [annotation["paper_id"]],
            [annotation["type"]],
            [annotation["page_number"]],
            [json.dumps(position)],
            [content or ""],
            [color],
            [stroke_width],
            [annotation["created_at"]],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)
        collection.flush()

        result = {
            "id": annotation_id,
            "paper_id": annotation["paper_id"],
            "type": annotation["type"],
            "page_number": annotation["page_number"],
            "position": position,
            "content": content,
            "color": color,
            "created_at": annotation["created_at"],
            "updated_at": now,
        }
        if stroke_width is not None:
            result["stroke_width"] = stroke_width
        return result

    def delete_annotation(self, annotation_id: str) -> bool:
        collection = self._get_annotations_collection()
        collection.load()
        annotation = self.get_annotation(annotation_id)
        if not annotation:
            return False
        collection.delete(f'id == "{annotation_id}"')
        collection.flush()
        return True

    def get_reading_progress(self, paper_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_progress_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=[
                "paper_id", "current_page", "total_pages",
                "zoom_level", "view_mode", "last_read_at"
            ]
        )
        if results:
            r = results[0]
            return {
                "paper_id": r.get("paper_id", ""),
                "current_page": r.get("current_page", 1),
                "total_pages": r.get("total_pages"),
                "zoom_level": r.get("zoom_level", 1.0),
                "view_mode": r.get("view_mode", "continuous"),
                "last_read_at": r.get("last_read_at", ""),
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
        collection = self._get_progress_collection()
        now = datetime.utcnow().isoformat()

        collection.load()
        collection.delete(f'paper_id == "{paper_id}"')
        collection.flush()

        insert_data = [
            [paper_id],
            [current_page],
            [total_pages],
            [zoom_level],
            [view_mode],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)
        collection.flush()

        return {
            "paper_id": paper_id,
            "current_page": current_page,
            "total_pages": total_pages,
            "zoom_level": zoom_level,
            "view_mode": view_mode,
            "last_read_at": now,
        }
