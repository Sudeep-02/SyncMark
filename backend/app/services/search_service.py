from typing import List, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy import func, text
from sqlalchemy import cast, func
from sqlalchemy.types import Uuid
from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink
from app.schemas.search_schema import BookmarkResult
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

def search_bookmarks(
    db: Session,
    user_id: UUID,
    query: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = None,
    folder_ids: Optional[List[UUID]] = None,
    include_deleted: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, List[BookmarkResult]]:

    # Base query
    stmt = select(Bookmark).where(Bookmark.user_id == user_id)

    if not include_deleted:
        stmt = stmt.where(Bookmark.deleted_at == None) 

    # Full-text search (PostgreSQL)
    if query:
        stmt = stmt.where(
            text(
                "to_tsvector('english', "
                "coalesce(title,'') || ' ' || "
                "coalesce(description,'') || ' ' || "
                "coalesce(url,'')) @@ plainto_tsquery(:q)"
            )
        ).params(q=query)

    # Folder filter
    
    if folder_ids:
        stmt = stmt.where(
            cast(Bookmark.folder_id, PG_UUID).in_(folder_ids)
        )


    # Tag filter (bookmarks must have ALL tags)
    if tag_ids:
        stmt = (
            stmt.join(
                BookmarkTagLink,
                cast(Bookmark.id, Uuid) == cast(BookmarkTagLink.bookmark_id, Uuid),
            )
            .where(cast(BookmarkTagLink.tag_id, Uuid).in_(tag_ids))
            .group_by(cast(Bookmark.id, Uuid))
            .having(
                func.count(func.distinct(cast(BookmarkTagLink.tag_id, Uuid)))
                == len(tag_ids)
            )
        )

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.exec(count_stmt).one()

    # Pagination
    stmt = stmt.offset(offset).limit(limit)
    bookmarks = db.exec(stmt).all()

    results: List[BookmarkResult] = []

    for b in bookmarks:
        tag_stmt = select(BookmarkTagLink.tag_id).where(
            BookmarkTagLink.bookmark_id == b.id
        )
        tag_ids_list = list(db.exec(tag_stmt).all())

        results.append(
            BookmarkResult(
                id=b.id,
                title=b.title or "",
                url=b.url or "",
                description=b.description,
                favicon_url=b.favicon_url,
                folder_id=b.folder_id,
                tag_ids=list(tag_ids_list),
            )
        )

    return total, results
