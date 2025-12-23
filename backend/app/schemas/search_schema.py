from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

class SearchRequest(BaseModel):
    query: str = Field(description="Text search query")
    tag_ids: List[UUID] = Field(description="Filter by tag IDs")
    folder_ids: List[UUID] = Field(description="Filter by folder IDs")
    include_deleted: bool = Field(False, description="Include deleted bookmarks")
    limit: int = Field(50, description="Number of results to return")
    offset: int = Field(0, description="Pagination offset")

class BookmarkResult(BaseModel):
    id: UUID
    title: str
    url: str
    description: Optional[str]
    favicon_url: Optional[str]
    folder_id: Optional[UUID]
    tag_ids: List[UUID]

class SearchResponse(BaseModel):
    total: int
    bookmarks: List[BookmarkResult]

    
model_config = {
        "from_attributes": True 
    }
