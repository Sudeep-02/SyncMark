from typing import Optional, Sequence
from uuid import UUID
from datetime import datetime, timezone
from app.models.folder_model import Folder
from sqlmodel import Session, select,col
from fastapi import HTTPException, status
from sqlalchemy import delete
from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink,Tag
from app.schemas.bookmark_schema import BookmarkCreate, BookmarkUpdate


def validate_tag_ids_exist(db: Session, tag_ids: Optional[list[UUID]]):
    if not tag_ids:
        return

    # Select column
    stmt = select(Tag.id).where(Tag.id.in_(tag_ids)) # type: ignore
    existing_ids = set(db.exec(stmt).all())  

    missing = set(tag_ids) - existing_ids
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tag IDs: {missing}"
        )


def create_bookmark(
    db: Session,
    user_id: UUID,
    payload: BookmarkCreate,
    device_id: Optional[UUID] = None
) -> Bookmark:
    try:
        # Validate folder
        folder_id = getattr(payload, "folder_id", None)
        if folder_id is not None:
            folder = db.get(Folder, folder_id)
            if not folder:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
            if folder.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Folder does not belong to user")

        # Validate tags
        validate_tag_ids_exist(db, payload.tag_ids)

        # Prepare bookmark data
        data = payload.model_dump(exclude_unset=True)
        data["user_id"] = user_id
        if device_id:
            data["last_modified_device"] = device_id

        # Convert HttpUrl fields to string
        if "url" in data and data["url"] is not None:
            data["url"] = str(data["url"])
        if "favicon_url" in data and data["favicon_url"] is not None:
            data["favicon_url"] = str(data["favicon_url"])

        # Create bookmark
        bookmark = Bookmark(**data)
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)

        # Link tags
        for tag_id in payload.tag_ids or []:
            db.add(BookmarkTagLink(bookmark_id=bookmark.id, tag_id=tag_id))
        if payload.tag_ids:
            db.commit()

        return bookmark

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bookmark: {str(e)}")



def list_user_bookmarks(
    db: Session,
    user_id: UUID,
    include_deleted: bool = False
) -> Sequence[Bookmark]:
    stmt = select(Bookmark).where(Bookmark.user_id == user_id)
    if not include_deleted:
        stmt = stmt.where(Bookmark.deleted_at.is_(None)) # type: ignore
    return db.exec(stmt).all()



def get_user_bookmark(
    db: Session,
    user_id: UUID,
    bookmark_id: UUID
) -> Bookmark:
    bookmark = db.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    if bookmark.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: Not your bookmark")
    if bookmark.deleted_at:
        raise HTTPException(status_code=404, detail="Bookmark was deleted")
    return bookmark


def update_bookmark(
    db: Session,
    user_id: UUID,
    bookmark_id: UUID,
    payload: BookmarkUpdate,
    device_id: Optional[UUID] = None
) -> Bookmark:
    # Fetch bookmark and ensure it belongs to the user
    bookmark = get_user_bookmark(db, user_id, bookmark_id)

    try:
        update_data = payload.model_dump(exclude_unset=True)

        # Inline folder validation
        folder_id = update_data.get("folder_id")
        if folder_id is not None:
            folder = db.get(Folder, folder_id)
            if not folder:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
            if folder.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Folder does not belong to user")

        # Validate tags
        tag_ids = update_data.get("tag_ids")
        if tag_ids is not None:
            validate_tag_ids_exist(db, tag_ids)

        # Update bookmark fields
        for field_name, value in update_data.items():
            if field_name == "tag_ids":
                continue
            setattr(bookmark, field_name, value)

        # Update last_modified_device if provided
        if device_id:
            bookmark.last_modified_device = device_id

        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)

        # Update tags if provided
        if tag_ids is not None:
            # Remove existing tag links
            stmt = delete(BookmarkTagLink).where(col(BookmarkTagLink.bookmark_id) == bookmark.id)
            # Add new tag links
            for tag_id in tag_ids:
                db.add(BookmarkTagLink(bookmark_id=bookmark.id, tag_id=tag_id))
            db.commit()

        return bookmark

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update bookmark: {str(e)}")


def soft_delete_bookmark(
    db: Session,
    user_id: UUID,
    bookmark_id: UUID,
    device_id: Optional[UUID] = None
) -> Bookmark:
    bookmark = get_user_bookmark(db, user_id, bookmark_id)

    try:
        bookmark.deleted_at = datetime.now(timezone.utc)
        if device_id:
            bookmark.last_modified_device = device_id

        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete bookmark: {str(e)}")
