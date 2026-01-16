from uuid import UUID
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TagRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    created_at: datetime

class TagModifyRequest(BaseModel):
    tag_ids: List[UUID]

model_config = {
        "from_attributes": True 
    }

