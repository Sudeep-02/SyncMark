from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import func
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING

# Avoid circular imports for type hints
if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.bookmark_model import Bookmark

def created_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now()})

def updated_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})

class Folder(SQLModel, table=True):

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    parent_id: Optional[UUID] = Field(default=None, foreign_key="folder.id", index=True)

    created_at: Optional[datetime] = created_at_field()
    updated_at: Optional[datetime] = updated_at_field()
    deleted_at: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="folders")
    bookmarks: List["Bookmark"] = Relationship(back_populates="folder")

    # Self-referential relationship
    parent: Optional["Folder"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Folder.id"}
    )
    children: List["Folder"] = Relationship(back_populates="parent")
