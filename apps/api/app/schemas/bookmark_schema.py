from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
import bleach

MAX_TITLE = 255
MAX_DESC = 2048


# ---------------------------------------------------------
# BASE
# ---------------------------------------------------------
class BookmarkBase(BaseModel):
    title: Optional[str] = Field(None, max_length=MAX_TITLE)
    description: Optional[str] = Field(None, max_length=MAX_DESC)
    favicon_url: Optional[str] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    is_featured: Optional[bool] = False

    @field_validator("description")
    def sanitize_description(cls, v):
        return bleach.clean(v) if v else v

    @field_validator("tag_ids")
    def validate_tag_ids(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Duplicate tag IDs are not allowed")
        return v


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------
class BookmarkCreate(BookmarkBase):
    url: str  

    model_config = ConfigDict(extra="forbid")

    @field_validator("title")
    def clean_title(cls, v):
        if v is None:
            return v
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------
class BookmarkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=MAX_TITLE)
    url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=MAX_DESC)
    favicon_url: Optional[str] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    is_featured: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("title")
    def clean_title(cls, v):
        if v is None:
            return v
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("description")
    def sanitize_description(cls, v):
        return bleach.clean(v) if v else v

    @field_validator("tag_ids")
    def validate_tag_ids(cls, v):
        if v and len(v) != len(set(v)):
            raise ValueError("Duplicate tag IDs are not allowed")
        return v


# ---------------------------------------------------------
# READ
# ---------------------------------------------------------
class BookmarkRead(BaseModel):
    id: UUID
    user_id: UUID

    url: str
    title: Optional[str]
    description: Optional[str]
    favicon_url: Optional[str]

    folder_id: Optional[UUID]
    tag_ids: List[UUID] = []

    version: int
    is_featured: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    last_modified_device: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
