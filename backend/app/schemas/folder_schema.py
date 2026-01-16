from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class FolderBase(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class FolderCreate(FolderBase):
    pass


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class FolderRead(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
