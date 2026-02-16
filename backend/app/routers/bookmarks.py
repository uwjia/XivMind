from fastapi import APIRouter, HTTPException, Query
from app.models import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkListResponse,
    MessageResponse,
)
from app.services import bookmark_service

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("", response_model=BookmarkResponse)
async def add_bookmark(bookmark: BookmarkCreate):
    try:
        result = bookmark_service.add_bookmark(bookmark.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{paper_id}", response_model=MessageResponse)
async def remove_bookmark(paper_id: str):
    try:
        bookmark_service.remove_bookmark(paper_id)
        return MessageResponse(message="Bookmark removed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{paper_id}", response_model=dict)
async def check_bookmark(paper_id: str):
    try:
        is_bookmarked = bookmark_service.is_bookmarked(paper_id)
        return {"paper_id": paper_id, "is_bookmarked": is_bookmarked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=BookmarkListResponse)
async def get_bookmarks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    try:
        items, total = bookmark_service.get_all_bookmarks(limit=limit, offset=offset)
        return BookmarkListResponse(total=total, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=BookmarkListResponse)
async def search_bookmarks(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=100, ge=1, le=1000),
):
    try:
        items = bookmark_service.search_bookmarks(query=query, limit=limit)
        return BookmarkListResponse(total=len(items), items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
