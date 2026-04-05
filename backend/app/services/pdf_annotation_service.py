from app.db.base import PdfAnnotationRepository
from app.db.factory import get_pdf_annotation_repository
from typing import Optional, List, Dict, Any

from app.models.pdf_annotation import (
    PdfAnnotationCreate,
    PdfAnnotationUpdate,
    AnnotationPosition,
)


class PdfAnnotationService:
    def __init__(self, repository: Optional[PdfAnnotationRepository] = None):
        self._repository = repository or get_pdf_annotation_repository()

    def get_annotations(self, paper_id: str) -> List[Dict[str, Any]]:
        return self._repository.get_annotations(paper_id)

    def create_annotation(self, data: PdfAnnotationCreate) -> Dict[str, Any]:
        annotation_data = {
            "paper_id": data.paper_id,
            "type": data.type.value,
            "page_number": data.page_number,
            "position": data.position.model_dump(),
            "content": data.content,
            "color": data.color,
            "stroke_width": data.stroke_width,
        }
        return self._repository.create_annotation(annotation_data)

    def get_annotation(self, annotation_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get_annotation(annotation_id)

    def update_annotation(self, annotation_id: str, data: PdfAnnotationUpdate) -> Optional[Dict[str, Any]]:
        update_data: Dict[str, Any] = {}
        if data.position is not None:
            update_data["position"] = data.position.model_dump()
        if data.content is not None:
            update_data["content"] = data.content
        if data.color is not None:
            update_data["color"] = data.color
        if data.stroke_width is not None:
            update_data["stroke_width"] = data.stroke_width
        return self._repository.update_annotation(annotation_id, update_data)

    def delete_annotation(self, annotation_id: str) -> bool:
        return self._repository.delete_annotation(annotation_id)

    def get_reading_progress(self, paper_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get_reading_progress(paper_id)

    def save_reading_progress(
        self,
        paper_id: str,
        current_page: int,
        total_pages: int,
        zoom_level: float,
        view_mode: str,
    ) -> Dict[str, Any]:
        return self._repository.save_reading_progress(
            paper_id, current_page, total_pages, zoom_level, view_mode
        )

    def get_all_reading_progress_with_papers(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._repository.get_all_reading_progress_with_papers(limit)


pdf_annotation_service = PdfAnnotationService()
