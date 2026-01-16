from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


# ---------- CLIENT → SERVER ----------

class BookmarkDelta(BaseModel):
    local_id: Optional[str] = None
    id: Optional[UUID] = None

    version: Optional[int] = None
    deleted: bool = False

    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    favicon_url: Optional[str] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None


class SyncRequest(BaseModel):
    device_id: UUID
    last_sync_at: Optional[datetime]
    deltas: List[BookmarkDelta]


# ---------- SHARED RESPONSE MODELS ----------

class BookmarkResponse(BaseModel):
    id: UUID
    url: str
    title: Optional[str]
    description: Optional[str]
    favicon_url: Optional[str]
    folder_id: Optional[UUID]
    version: int
    deleted_at: Optional[datetime]
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------- SERVER → CLIENT ----------

class AcceptedItem(BaseModel):
    local_id: Optional[str]
    bookmark: BookmarkResponse


class ConflictItem(BaseModel):
    bookmark_id: UUID
    server_bookmark: BookmarkResponse


class SyncResponse(BaseModel):
    accepted: List[AcceptedItem]
    conflicts: List[ConflictItem]
    server_changes: List[BookmarkResponse]
    server_time: datetime
