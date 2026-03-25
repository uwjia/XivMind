import logging
from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query

from app.models.followed_author import (
    FollowedAuthorCreate,
    FollowedAuthorUpdate,
    FollowedAuthorResponse,
    FollowedAuthorListResponse,
    FollowedAuthorCheckResponse,
)
from app.services.followed_author_service import FollowedAuthorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/followed-authors", tags=["followed-authors"])

_followed_author_service = FollowedAuthorService()


@router.post("", response_model=FollowedAuthorResponse)
def follow_author(data: FollowedAuthorCreate):
    try:
        result = _followed_author_service.follow_author(
            author_name=data.author_name,
            notes=data.notes,
        )
        return result
    except Exception as e:
        logger.error(f"Error following author: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{author_name:path}", response_model=dict)
def unfollow_author(author_name: str):
    author_name = unquote(author_name)
    try:
        success = _followed_author_service.unfollow_author(author_name)
        if not success:
            raise HTTPException(status_code=404, detail="Author not found in followed list")
        return {"success": True, "message": f"Unfollowed {author_name}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unfollowing author: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=FollowedAuthorListResponse)
def get_followed_authors(
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
):
    try:
        items, total = _followed_author_service.get_all_followed(limit, offset)
        return {"total": total, "items": items}
    except Exception as e:
        logger.error(f"Error getting followed authors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{author_name:path}", response_model=FollowedAuthorCheckResponse)
def check_if_followed(author_name: str):
    author_name = unquote(author_name)
    try:
        is_followed = _followed_author_service.is_followed(author_name)
        return {"author_name": author_name, "is_followed": is_followed}
    except Exception as e:
        logger.error(f"Error checking if author is followed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{author_name:path}", response_model=FollowedAuthorResponse)
def update_author_notes(author_name: str, data: FollowedAuthorUpdate):
    author_name = unquote(author_name)
    try:
        success = _followed_author_service.update_notes(author_name, data.notes or "")
        if not success:
            raise HTTPException(status_code=404, detail="Author not found in followed list")
        
        updated = _followed_author_service.get_by_author_name(author_name)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating author notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
