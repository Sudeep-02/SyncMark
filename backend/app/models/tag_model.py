
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import func
from uuid import UUID, uuid4
from typing import Optional, List,TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column

if TYPE_CHECKING:
    from app.models.bookmark_model import Bookmark
    
def created_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now()})

def updated_at_field():
    return Field(default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})

class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    name: str = Field(index=True)
    created_at: Optional[datetime] = created_at_field()
    updated_at: Optional[datetime] = updated_at_field()

    bookmarks: List["BookmarkTagLink"] = Relationship(back_populates="tag")


class BookmarkTagLink(SQLModel, table=True):
    bookmark_id: UUID = Field(foreign_key="bookmark.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)

    tag: "Tag" = Relationship(back_populates="bookmarks")
    bookmark: "Bookmark" = Relationship(back_populates="tags")