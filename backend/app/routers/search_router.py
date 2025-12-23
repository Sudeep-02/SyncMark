from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from sqlmodel import Session
from app.schemas.search_schema import SearchRequest, SearchResponse, BookmarkResult
from app.services.search_service import search_bookmarks

from app.core.database import get_session
from app.deps.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/", response_model=SearchResponse)
def search_endpoint(payload: SearchRequest, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):

    total, bookmarks = search_bookmarks(
        db,
        user_id=user_id,
        query=payload.query,
        tag_ids=payload.tag_ids,
        folder_ids=payload.folder_ids,
        include_deleted=payload.include_deleted,
        limit=payload.limit,
        offset=payload.offset
    )

    return SearchResponse(total=total, bookmarks=bookmarks)
