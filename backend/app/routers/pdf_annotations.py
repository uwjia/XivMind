from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os

from app.models.pdf_annotation import (
    PdfAnnotationCreate,
    PdfAnnotationUpdate,
    PdfAnnotationResponse,
    PdfReadingProgressCreate,
    PdfReadingProgressResponse,
    PdfOutlineItemResponse,
)
from app.models import MessageResponse
from app.services.pdf_annotation_service import pdf_annotation_service
from app.services import download_service

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/{paper_id}/annotations", response_model=List[PdfAnnotationResponse])
def get_annotations(paper_id: str):
    try:
        annotations = pdf_annotation_service.get_annotations(paper_id)
        return annotations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{paper_id}/annotations", response_model=PdfAnnotationResponse)
def create_annotation(paper_id: str, data: PdfAnnotationCreate):
    try:
        if data.paper_id != paper_id:
            raise HTTPException(status_code=400, detail="Paper ID mismatch")
        
        annotation = pdf_annotation_service.create_annotation(data)
        return annotation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/annotations/{annotation_id}", response_model=PdfAnnotationResponse)
def update_annotation(annotation_id: str, data: PdfAnnotationUpdate):
    try:
        annotation = pdf_annotation_service.update_annotation(annotation_id, data)
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")
        return annotation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/annotations/{annotation_id}", response_model=MessageResponse)
def delete_annotation(annotation_id: str):
    try:
        success = pdf_annotation_service.delete_annotation(annotation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Annotation not found")
        return MessageResponse(message="Annotation deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{paper_id}/progress", response_model=PdfReadingProgressResponse)
def get_reading_progress(paper_id: str):
    try:
        progress = pdf_annotation_service.get_reading_progress(paper_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        return progress
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{paper_id}/progress", response_model=PdfReadingProgressResponse)
def save_reading_progress(paper_id: str, data: PdfReadingProgressCreate):
    try:
        progress = pdf_annotation_service.save_reading_progress(
            paper_id,
            data.current_page,
            data.total_pages,
            data.zoom_level,
            data.view_mode,
        )
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{paper_id}/file")
def get_pdf_file(paper_id: str):
    try:
        task = download_service.get_task_by_paper_id(paper_id)
        if not task:
            raise HTTPException(status_code=404, detail="Download task not found")
        
        if task.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Download not completed")
        
        file_path = task.get("file_path")
        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File does not exist")
        
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=os.path.basename(file_path),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{paper_id}/outline", response_model=List[PdfOutlineItemResponse])
def get_pdf_outline(paper_id: str):
    try:
        task = download_service.get_task_by_paper_id(paper_id)
        if not task:
            raise HTTPException(status_code=404, detail="Download task not found")
        
        if task.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Download not completed")
        
        file_path = task.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            outline = reader.outline
            
            def parse_outline(items, level=0):
                result = []
                for item in items:
                    if isinstance(item, list):
                        result.extend(parse_outline(item, level + 1))
                    elif hasattr(item, 'title'):
                        dest_page = None
                        if hasattr(item, 'dest') and item.dest:
                            try:
                                if isinstance(item.dest, dict) and '/D' in item.dest:
                                    dest_array = item.dest['/D']
                                    if dest_array and len(dest_array) > 0:
                                        dest_page = reader.get_destination_page_number(item)
                                elif isinstance(item.dest, list) and len(item.dest) > 0:
                                    dest_page = reader.get_destination_page_number(item)
                            except:
                                pass
                        
                        outline_item = {
                            "title": item.title,
                            "dest": dest_page,
                            "items": [],
                        }
                        
                        if hasattr(item, 'children') and item.children:
                            outline_item["items"] = parse_outline(item.children, level + 1)
                        
                        result.append(outline_item)
                return result
            
            return parse_outline(outline) if outline else []
        except ImportError:
            return []
        except Exception as e:
            print(f"Error parsing PDF outline: {e}")
            return []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
