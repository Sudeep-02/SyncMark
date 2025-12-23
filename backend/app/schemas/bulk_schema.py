from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class BulkMoveRequest(BaseModel):
    bookmark_ids: List[UUID]
    target_folder_id: Optional[UUID] = None  # None = move to root
    device_id: UUID

class BulkDeleteRequest(BaseModel):
    bookmark_ids: List[UUID]
    device_id: UUID

class BulkTagEditRequest(BaseModel):
    bookmark_ids: List[UUID]
    add_tag_ids: Optional[List[UUID]] = None
    remove_tag_ids: Optional[List[UUID]] = None
    device_id: UUID

class BulkResponseItem(BaseModel):
    bookmark_id: UUID
    status: str  # "success" or "error"
    detail: Optional[str] = None

class BulkResponse(BaseModel):
    results: List[BulkResponseItem]

    
model_config = {
        "from_attributes": True 
    }
