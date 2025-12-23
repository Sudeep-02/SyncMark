from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
from datetime import datetime
import bleach

# Your original limits
MAX_TITLE = 255
MAX_DESC = 2048

# Whitelist for update security (mass assignment protection)
ALLOWED_UPDATE_FIELDS = {
    "title",
    "url",
    "description",
    "favicon_url",
    "folder_id",
    "tag_ids",
}


# ---------------------------------------------------------
# Base (shared fields)
# ---------------------------------------------------------
class BookmarkBase(BaseModel):
    title: Optional[str] = Field(None, max_length=MAX_TITLE)
    url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, max_length=MAX_DESC)
    favicon_url: Optional[HttpUrl] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------
class BookmarkCreate(BookmarkBase):
    model_config = ConfigDict(extra="forbid")

    @field_validator("title")
    def validate_title(cls, v):
        if v is None:
            raise ValueError("Title is required")
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
# UPDATE
# ---------------------------------------------------------
class BookmarkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=MAX_TITLE)
    url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, max_length=MAX_DESC)
    favicon_url: Optional[HttpUrl] = None
    folder_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None

    model_config = ConfigDict(extra="forbid")  # mass assignment protection

    @field_validator("title")
    def validate_title(cls, v):
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

    @field_validator("*")
    def enforce_whitelist(cls, v, field):
        if field.field_name not in ALLOWED_UPDATE_FIELDS:
            raise ValueError(f"Field '{field.field_name}' cannot be updated")
        return v


# ---------------------------------------------------------
# READ (response to client)
# ---------------------------------------------------------
class BookmarkRead(BaseModel):
    id: UUID
    user_id: UUID

    title: Optional[str]
    url: Optional[HttpUrl]
    description: Optional[str]
    favicon_url: Optional[HttpUrl]
    folder_id: Optional[UUID]

    tags: Optional[List[UUID]]

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    last_modified_device: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
