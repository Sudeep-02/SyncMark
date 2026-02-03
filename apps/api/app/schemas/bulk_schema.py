from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class BulkMoveRequest(BaseModel):
    bookmark_ids: List[UUID]
    target_folder_id: Optional[UUID]
    device_id: UUID


class BulkDeleteRequest(BaseModel):
    bookmark_ids: List[UUID]
    device_id: UUID


class BulkTagEditRequest(BaseModel):
    bookmark_ids: List[UUID]
    add_tag_ids: Optional[List[UUID]] = []
    remove_tag_ids: Optional[List[UUID]] = []
    device_id: UUID


class BulkResultItem(BaseModel):
    bookmark_id: UUID
    status: str
    detail: Optional[str] = None


class BulkResponse(BaseModel):
    results: List[BulkResultItem]

model_config = {
        "from_attributes": True 
    }
