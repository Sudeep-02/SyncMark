from typing import List
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink
from app.services.tag_service import validate_tag_ids_exist, add_tags_to_bookmark, remove_tags_from_bookmark
# from app.services.bookmark_service import validate_folder

_now = lambda: datetime.now(timezone.utc)

def bulk_move_bookmarks(db: Session, user_id: UUID, bookmark_ids: List[UUID], target_folder_id: UUID, device_id: UUID):
    results = []

    # if target_folder_id:
    #     validate_folder(db, user_id, target_folder_id)

    for bm_id in bookmark_ids:
        bookmark = db.get(Bookmark, bm_id)
        if not bookmark or bookmark.user_id != user_id:
            results.append({"bookmark_id": bm_id, "status": "error", "detail": "Not found or unauthorized"})
            continue
        bookmark.folder_id = target_folder_id
        bookmark.last_modified_at = _now()
        bookmark.last_modified_device = device_id
        bookmark.version = (bookmark.version or 0) + 1
        db.add(bookmark)
        results.append({"bookmark_id": bm_id, "status": "success"})

    db.commit()
    return results


def bulk_delete_bookmarks(db: Session, user_id: UUID, bookmark_ids: List[UUID], device_id: UUID):
    results = []
    now = _now()
    for bm_id in bookmark_ids:
        bookmark = db.get(Bookmark, bm_id)
        if not bookmark or bookmark.user_id != user_id:
            results.append({"bookmark_id": bm_id, "status": "error", "detail": "Not found or unauthorized"})
            continue
        bookmark.deleted_at = now
        bookmark.deleted_by_device = device_id
        bookmark.last_modified_at = now
        bookmark.last_modified_device = device_id
        bookmark.version = (bookmark.version or 0) + 1
        db.add(bookmark)
        results.append({"bookmark_id": bm_id, "status": "success"})

    db.commit()
    return results


def bulk_tag_edit_bookmarks(db: Session, user_id: UUID, bookmark_ids: List[UUID], add_tag_ids: List[UUID], remove_tag_ids: List[UUID], device_id: UUID):
    results = []

    # Validate tags exist
    if add_tag_ids:
        validate_tag_ids_exist(db, user_id, add_tag_ids)
    if remove_tag_ids:
        validate_tag_ids_exist(db, user_id, remove_tag_ids)

    for bm_id in bookmark_ids:
        bookmark = db.get(Bookmark, bm_id)
        if not bookmark or bookmark.user_id != user_id:
            results.append({"bookmark_id": bm_id, "status": "error", "detail": "Not found or unauthorized"})
            continue

        # Remove tags
        if remove_tag_ids:
            for tag_id in remove_tag_ids:
                link = db.exec(select(BookmarkTagLink).where(BookmarkTagLink.bookmark_id == bm_id, BookmarkTagLink.tag_id == tag_id)).first()
                if link:
                    db.delete(link)

        # Add tags
        if add_tag_ids:
            for tag_id in add_tag_ids:
                exists = db.exec(select(BookmarkTagLink).where(BookmarkTagLink.bookmark_id == bm_id, BookmarkTagLink.tag_id == tag_id)).first()
                if not exists:
                    db.add(BookmarkTagLink(bookmark_id=bm_id, tag_id=tag_id))

        bookmark.last_modified_at = _now()
        bookmark.last_modified_device = device_id
        bookmark.version = (bookmark.version or 0) + 1
        db.add(bookmark)
        results.append({"bookmark_id": bm_id, "status": "success"})

    db.commit()
    return results
