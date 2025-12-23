from typing import List, Optional,Sequence
from uuid import UUID
from sqlmodel import Session, col, select, delete
from fastapi import HTTPException, status
from sqlalchemy import cast, delete
from sqlalchemy.types import Uuid
from app.models.tag_model import Tag, BookmarkTagLink
from app.models.bookmark_model import Bookmark  # your existing Bookmark model
from app.services.bookmark_service import get_user_bookmark  # helper from bookmark crud

# ---- Tag CRUD ----

def create_tag(db: Session, user_id: UUID, name: str) -> Tag:
    # Optionally dedupe by user + lowercase name
    normalized = name.strip()
    stmt = select(Tag).where(Tag.user_id == user_id, Tag.name == normalized)
    existing = db.exec(stmt).first()
    if existing:
        # return existing rather than error: helpful UX
        return existing

    tag = Tag(user_id=user_id, name=normalized)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def list_tags(db: Session, user_id: UUID) -> Sequence[Tag]:
    stmt = select(Tag).where(Tag.user_id == user_id)
    return db.exec(stmt).all()


def get_tag(db: Session, user_id: UUID, tag_id: UUID) -> Tag:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    if tag.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your tag")
    return tag


# ---- Validation helper ----
def validate_tag_ids_exist(db: Session, user_id: UUID, tag_ids: Optional[List[UUID]]):
    """
    Ensures provided tag_ids exist and belong to the user.
    Raises HTTPException 400 if any are missing or 403 if any belong to other user.
    """
    if not tag_ids:
        return

    stmt = select(Tag.id, Tag.user_id).where(col(Tag.id).in_(tag_ids))
    rows = db.exec(stmt).all()  # list of (id, user_id) tuples OR Tag objects depending on SQLModel version

    # convert to set of ids found
    found_ids = {r[0] if isinstance(r, tuple) else r.id for r in rows}
    missing = set(tag_ids) - found_ids
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid tag IDs: {missing}")

    # verify ownership
    # fetch user_ids for found tags to check ownership
    # simpler: select Tag where id in tag_ids and user_id == user_id must match count
    stmt2 = select(Tag).where(col(Tag.id).in_(tag_ids), col(Tag.user_id) == user_id)
    owned = db.exec(stmt2).all()
    owned_ids = {t.id for t in owned}
    not_owned = set(tag_ids) - owned_ids
    if not_owned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Tag(s) do not belong to user: {not_owned}")


# ---- Bookmark tag operations ----

def add_tags_to_bookmark(db: Session, user_id: UUID, bookmark_id: UUID, tag_ids: List[UUID]):
    """
    Append tags to bookmark (no-op for tags already present).
    """
    bookmark = get_user_bookmark(db, user_id, bookmark_id)

    # validate tag existence & ownership
    validate_tag_ids_exist(db, user_id, tag_ids)

    # fetch existing tag ids
    stmt = select(BookmarkTagLink.tag_id).where(BookmarkTagLink.bookmark_id == bookmark_id)
    existing_rows = db.exec(stmt).all()
    existing_ids = {row for row in existing_rows}

    # add links for new tags
    added = []
    for tag_id in tag_ids:
        if tag_id not in existing_ids:
            link = BookmarkTagLink(bookmark_id=bookmark_id, tag_id=tag_id)
            db.add(link)
            added.append(tag_id)

    if added:
        db.commit()
    # return some useful info
    return {"added": added, "bookmark_id": bookmark_id}


def remove_tags_from_bookmark(db: Session, user_id: UUID, bookmark_id: UUID, tag_ids: List[UUID]):
    """
    Remove specified tags from a bookmark. Safe if some tags were not linked.
    """
    bookmark = get_user_bookmark(db, user_id, bookmark_id)

    removed = []
    for tag_id in tag_ids:
        stmt = select(BookmarkTagLink).where(
            BookmarkTagLink.bookmark_id == bookmark_id,
            BookmarkTagLink.tag_id == tag_id
        )
        link = db.exec(stmt).first()
        if link:
            db.delete(link)
            removed.append(tag_id)

    if removed:
        db.commit()
    return {"removed": removed, "bookmark_id": bookmark_id}


def clear_all_tags(db: Session, user_id: UUID, bookmark_id: UUID):
    """
    Remove all tag links for this bookmark.
    """
    bookmark = get_user_bookmark(db, user_id, bookmark_id)

    stmt = delete(BookmarkTagLink).where(
        cast(BookmarkTagLink.bookmark_id, Uuid) == bookmark_id
    )

    db.execute(stmt)
    db.commit()

    return {"cleared": True, "bookmark_id": bookmark_id}
