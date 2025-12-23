from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

# Minimal bookmark payload for sync (client -> server)
class BookmarkDelta(BaseModel):
    id: Optional[UUID] = None  # null for create
    local_id: Optional[str] = None  # client's temporary id for created items
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    description: Optional[str] = None
    favicon_url: Optional[HttpUrl] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None

    # sync metadata from client
    version: Optional[int] = None
    last_modified_at: Optional[datetime] = None
    device_id: Optional[UUID] = None
    deleted: Optional[bool] = False

class SyncRequest(BaseModel):
    device_id: UUID
    last_sync_at: Optional[datetime] = None  # server timestamp of last sync known to client
    deltas: List[BookmarkDelta] = []

class FieldConflict(BaseModel):
    field: str
    client_value: Optional[Any]
    server_value: Optional[Any]
    server_last_modified_at: Optional[datetime]
    server_last_modified_device: Optional[UUID]

class ConflictItem(BaseModel):
    bookmark_id: Optional[UUID]  # null for newly-created client item mapped server-side
    local_id: Optional[str]
    conflicts: List[FieldConflict]

class ServerChange(BaseModel):
    bookmark_id: UUID
    bookmark: Dict[str, Any]  # full server-side bookmark as dict

class SyncResponse(BaseModel):
    accepted: List[Dict[str, Any]] = []    # e.g. [{"bookmark_id":..., "local_id":..., "bookmark": {...}}]
    conflicts: List[ConflictItem] = []
    server_changes: List[ServerChange] = []  # changes client needs to apply
    server_time: datetime

    
model_config = {
        "from_attributes": True 
    }
