from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import Session, select
from sqlalchemy import func, text, cast
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink
from app.schemas.search_schema import BookmarkResult


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

    stmt = select(Bookmark).where(Bookmark.user_id == user_id)

    if not include_deleted:
        stmt = stmt.where(Bookmark.deleted_at.is_(None)) # type: ignore

    if query:
        stmt = stmt.where(
            text(
                "to_tsvector('english', "
                "coalesce(title,'') || ' ' || "
                "coalesce(description,'') || ' ' || "
                "coalesce(url,'')) @@ plainto_tsquery(:q)"
            )
        ).params(q=query)

    if folder_ids:
        stmt = stmt.where(
            cast(Bookmark.folder_id, PG_UUID).in_(folder_ids)
        )

    if tag_ids:
        stmt = (
            stmt.join(
                BookmarkTagLink,
                Bookmark.id == BookmarkTagLink.bookmark_id # type: ignore
            )
            .where(BookmarkTagLink.tag_id.in_(tag_ids)) # type: ignore
            .group_by(Bookmark.id) # type: ignore
            .having(func.count() == len(tag_ids))
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.exec(count_stmt).one()

    stmt = stmt.offset(offset).limit(limit)
    bookmarks = db.exec(stmt).all()

    results = []
    for b in bookmarks:
        tag_stmt = select(BookmarkTagLink.tag_id).where(
            BookmarkTagLink.bookmark_id == b.id
        )
        tags = list(db.exec(tag_stmt).all())

        results.append(
            BookmarkResult(
                id=b.id,
                url=b.url,
                title=b.title or "",
                description=b.description,
                favicon_url=b.favicon_url,
                folder_id=b.folder_id,
                tag_ids=tags,
            )
        )

    return total, results
