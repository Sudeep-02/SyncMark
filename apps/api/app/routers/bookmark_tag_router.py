from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlmodel import Session
from typing import List

from app.core.database import get_session
from app.schemas.tag_schema import TagModifyRequest
from app.services.tag_service import TagService
from app.deps.auth import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks-Tags"])


@router.post("/{bookmark_id}/tags/add", status_code=status.HTTP_200_OK)
def add_tags(bookmark_id: UUID, body: TagModifyRequest, db: Session = Depends(get_session),
             user_id: UUID = Depends(get_current_user)):
    return TagService.add_tags_to_bookmark(db, user_id, bookmark_id, body.tag_ids)


@router.post("/{bookmark_id}/tags/remove", status_code=status.HTTP_200_OK)
def remove_tags(bookmark_id: UUID, body: TagModifyRequest, db: Session = Depends(get_session),
                user_id: UUID = Depends(get_current_user)):
    return TagService.remove_tags_from_bookmark(db, user_id, bookmark_id, body.tag_ids)


@router.post("/{bookmark_id}/tags/clear", status_code=status.HTTP_200_OK)
def clear_tags(bookmark_id: UUID, db: Session = Depends(get_session),
               user_id: UUID = Depends(get_current_user)):
    return TagService.clear_all_tags(db, user_id, bookmark_id)
