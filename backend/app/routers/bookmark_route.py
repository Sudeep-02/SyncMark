# app/routes/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException, status,Header
from sqlmodel import Session
from typing import List
from uuid import UUID,uuid4

from app.schemas.bookmark_schema import BookmarkCreate, BookmarkUpdate, BookmarkRead
from app.core.database import get_session
from app.services.bookmark_service import (
    create_bookmark, list_user_bookmarks, get_user_bookmark,
    update_bookmark, soft_delete_bookmark
)
from app.deps.auth import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
def create_bookmark_record(payload: BookmarkCreate, db: Session = Depends(get_session),
                    current_user = Depends(get_current_user),device_id: UUID | None = Header(default=None)):
    
    if device_id is None:
        device_id = uuid4()
        
    bookmark_record = create_bookmark(db, current_user.id, payload, device_id,)
    return bookmark_record

@router.get("/", response_model=List[BookmarkRead])
def read_bookmarks(db: Session = Depends(get_session), current_user = Depends(get_current_user)):
    return list_user_bookmarks(db, current_user.id)

@router.get("/{bookmark_id}", response_model=BookmarkRead)
def read_bookmark(bookmark_id: UUID, db: Session = Depends(get_session), current_user = Depends(get_current_user)):
    record = get_user_bookmark(db, current_user.id, bookmark_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return record

@router.patch("/{bookmark_id}", response_model=BookmarkRead)
def patch_bookmark(bookmark_id: UUID, payload: BookmarkUpdate, db: Session = Depends(get_session), current_user = Depends(get_current_user)):
    device_id = None
    record = update_bookmark(db, current_user.id, bookmark_id, payload,device_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return record

@router.delete("/{bookmark_id}", status_code=status.HTTP_200_OK)
def delete_bookmark(bookmark_id: UUID, db: Session = Depends(get_session), current_user = Depends(get_current_user)):
    device_id = None
    record = soft_delete_bookmark(db, current_user.id, bookmark_id, device_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return {"detail": "Bookmark soft-deleted"}
