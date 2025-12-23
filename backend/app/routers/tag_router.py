from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from sqlmodel import Session

from app.schemas.tag_schema import TagCreate, TagRead
from app.services.tag_service import create_tag, list_tags, get_tag

from app.core.database import get_session
from app.deps.auth import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create(payload: TagCreate, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    tag = create_tag(db, user_id, payload.name)
    return tag


@router.get("/", response_model=List[TagRead])
def get_all(db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return list_tags(db, user_id)


@router.get("/{tag_id}", response_model=TagRead)
def get_one(tag_id: UUID, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    return get_tag(db, user_id, tag_id)
