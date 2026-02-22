from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import func,Column
from uuid import UUID, uuid4
from typing import Optional, List,TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.tag_model import BookmarkTagLink
    from app.models.folder_model import Folder
    from app.models.device_model import Device


def created_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now()})

def updated_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})


class Bookmark(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    favicon_url: Optional[str] = None
    cover_image_url: Optional[str] = None

    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    folder_id: Optional[UUID] = Field(default=None, foreign_key="folder.id")
    last_modified_device: Optional[UUID] = Field(default=None, foreign_key="device.device_id")

    created_at: Optional[datetime] = created_at_field()
    updated_at: Optional[datetime] = updated_at_field()
    deleted_at: Optional[datetime] = None
    deleted_by_device: Optional[UUID] = Field(default=None, nullable=True)
    version: int = Field(default=1, nullable=False)
    is_featured: bool = Field(default=False, nullable=False, index=True)



    user: "User" = Relationship(back_populates="bookmarks")
    folder: "Folder" = Relationship(back_populates="bookmarks")
    last_modified_device_rel: "Device" = Relationship(back_populates="bookmarks_modified")
    tags: List["BookmarkTagLink"] = Relationship(back_populates="bookmark")
