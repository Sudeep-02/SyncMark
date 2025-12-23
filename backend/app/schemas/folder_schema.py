from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: Optional[UUID] = None

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[UUID] | None = None  # None means explicit set to top-level

class FolderRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    parent_id: Optional[UUID]

   
    
model_config = {
        "from_attributes": True 
    }
