from sqlmodel import SQLModel
from pydantic import BaseModel
from typing import Optional


class ForbidExtraBase(SQLModel):
    class Config:
        extra = "forbid"    
          
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id: int
    
model_config = {
        "from_attributes": True 
    }

    



