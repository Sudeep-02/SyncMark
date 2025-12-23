from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session

from app.core.database import get_session
from app.deps.auth import get_current_user
from app.schemas.folder_schema import FolderCreate, FolderRead, FolderUpdate
from app.services.folder_service import (
    create_folder,
    list_folders,
    get_user_folder,
    update_folder,
    delete_folder,
    list_root_folders,
)

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.post("/", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
def create(payload: FolderCreate, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return create_folder(db, user_id, payload)


@router.get("/", response_model=List[FolderRead])
def get_all(db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return list_folders(db, user_id)


@router.get("/roots", response_model=List[FolderRead])
def get_roots(db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return list_root_folders(db, user_id)


@router.get("/{folder_id}", response_model=FolderRead)
def get_one(folder_id: UUID, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return get_user_folder(db, user_id, folder_id)


@router.patch("/{folder_id}", response_model=FolderRead)
def patch(folder_id: UUID, payload: FolderUpdate, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return update_folder(db, user_id, folder_id, payload)


@router.delete("/{folder_id}")
def remove(folder_id: UUID, mode: str = Query("reject", description="reject|move_children_to_parent|move_to_root|cascade"),
           db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return delete_folder(db, user_id, folder_id, mode)
