from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TagRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str

class TagModifyRequest(BaseModel):
    tag_ids: List[UUID]

model_config = {
        "from_attributes": True 
    }

