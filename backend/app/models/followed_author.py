from pydantic import BaseModel
from typing import Optional, List


class FollowedAuthorCreate(BaseModel):
    author_name: str
    notes: Optional[str] = None


class FollowedAuthorUpdate(BaseModel):
    notes: Optional[str] = None


class FollowedAuthorResponse(BaseModel):
    id: str
    author_name: str
    paper_count: int
    latest_published: Optional[str]
    notes: Optional[str]
    followed_at: str


class FollowedAuthorListResponse(BaseModel):
    total: int
    items: List[FollowedAuthorResponse]


class FollowedAuthorCheckResponse(BaseModel):
    author_name: str
    is_followed: bool
