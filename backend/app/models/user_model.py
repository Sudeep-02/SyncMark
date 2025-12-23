from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import func,Column
from uuid import UUID, uuid4
from typing import Optional, List,TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.bookmark_model import Bookmark
    from app.models.folder_model import Folder
    from app.models.device_model import Device
    


def created_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now()})

def updated_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: Optional[str] = None
    email: str = Field(index=True, unique=True)
    password_hash: str
    avatar_url: Optional[str] = None
    
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    
    reset_token: Optional[str] = Field(default=None, index=True)
    reset_token_expires_at: Optional[datetime] = None
    
    
    created_at: Optional[datetime] = created_at_field()
    updated_at: Optional[datetime] = updated_at_field()
    deleted_at: Optional[datetime] = None

    bookmarks: List["Bookmark"] = Relationship(back_populates="user")
    folders: List["Folder"] = Relationship(back_populates="user")
    devices: List["Device"] = Relationship(back_populates="owner")






