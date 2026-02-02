from fastapi import APIRouter, Depends, HTTPException, status,Header
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID,uuid4
from app.deps.device import get_device_id
from app.schemas.bookmark_schema import BookmarkCreate, BookmarkUpdate, BookmarkRead
from app.core.database import get_session
from app.services.bookmark_service import BookmarkService

from app.deps.auth import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])

@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_session),
                    user_id = Depends(get_current_user),device_id: UUID = Depends(get_device_id)):
    
   
    return BookmarkService.create_bookmark(
        db, user_id, payload, device_id
    )


@router.get("/", response_model=List[BookmarkRead])
def list_bookmarks(
    featured: Optional[bool] = None,
    folder_id: Optional[UUID] = None,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    return BookmarkService.list_user_bookmarks(
        db=db,
        user_id=user_id,
        featured=featured,
        folder_id=folder_id,
    )

@router.get("/{bookmark_id}", response_model=BookmarkRead)
def get_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    record = BookmarkService.get_user_bookmark(
        db, user_id, bookmark_id
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return record



@router.patch("/{bookmark_id}", response_model=BookmarkRead)
def update_bookmark(
    bookmark_id: UUID,
    payload: BookmarkUpdate,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
    device_id: UUID = Depends(get_device_id)
):
  
    record = BookmarkService.update_bookmark(
        db, user_id, bookmark_id, payload, device_id
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return record

@router.delete("/{bookmark_id}", status_code=status.HTTP_200_OK)
def delete_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
    device_id: UUID = Depends(get_device_id)
):

    record = BookmarkService.soft_delete_bookmark(
        db, user_id, bookmark_id, device_id
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    return {"detail": "Bookmark soft-deleted"}
