from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List,TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.bookmark_model import Bookmark


class Device(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    device_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    last_known_revision: Optional[datetime] = None
    device_id: UUID = Field(index=True, unique=True, nullable=False)
    os: Optional[str] = None
    android_version : Optional[str] = None
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    

    owner: "User" = Relationship(back_populates="devices")
    bookmarks_modified: List["Bookmark"] = Relationship(back_populates="last_modified_device_rel")
