from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import Session, delete

from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink
from app.services.tag_service import TagService


def utc_now():
    return datetime.now(timezone.utc)


class BulkService:

    # ---------- MOVE ----------

    @staticmethod
    def bulk_move_bookmarks(
        db: Session,
        user_id: UUID,
        bookmark_ids: List[UUID],
        target_folder_id: Optional[UUID],
        device_id: UUID,
    ):
        results = []

        with db.begin():
            for bookmark_id in bookmark_ids:
                bookmark = db.get(Bookmark, bookmark_id)

                if not bookmark or bookmark.user_id != user_id:
                    results.append(
                        {"bookmark_id": bookmark_id, "status": "error"}
                    )
                    continue

                bookmark.folder_id = target_folder_id
                bookmark.updated_at = utc_now()
                bookmark.version += 1
                bookmark.last_modified_device = device_id

                results.append(
                    {"bookmark_id": bookmark_id, "status": "success"}
                )

        return results

    # ---------- DELETE ----------

    @staticmethod
    def bulk_delete_bookmarks(
        db: Session,
        user_id: UUID,
        bookmark_ids: List[UUID],
        device_id: UUID,
    ):
        results = []

        with db.begin():
            for bookmark_id in bookmark_ids:
                bookmark = db.get(Bookmark, bookmark_id)

                if not bookmark or bookmark.user_id != user_id:
                    results.append(
                        {"bookmark_id": bookmark_id, "status": "error"}
                    )
                    continue

                bookmark.deleted_at = utc_now()
                bookmark.deleted_by_device = device_id
                bookmark.version += 1
                bookmark.last_modified_device = device_id

                results.append(
                    {"bookmark_id": bookmark_id, "status": "success"}
                )

        return results

    # ---------- TAG EDIT ----------

    @staticmethod
    def bulk_tag_edit_bookmarks(
        db: Session,
        user_id: UUID,
        bookmark_ids: List[UUID],
        add_tag_ids: List[UUID],
        remove_tag_ids: List[UUID],
        device_id: UUID,
    ):
        TagService.validate_ids(db, user_id, add_tag_ids)
        TagService.validate_ids(db, user_id, remove_tag_ids)

        results = []

        with db.begin():
            for bookmark_id in bookmark_ids:
                bookmark = db.get(Bookmark, bookmark_id)

                if not bookmark or bookmark.user_id != user_id:
                    results.append(
                        {"bookmark_id": bookmark_id, "status": "error"}
                    )
                    continue

                # ✅ Correct DELETE
                if remove_tag_ids:
                    db.execute(
                        delete(BookmarkTagLink).where(
                            BookmarkTagLink.bookmark_id == bookmark_id, # type: ignore
                            BookmarkTagLink.tag_id.in_(remove_tag_ids), # type: ignore
                        )
                    )

                # ✅ Add tags
                for tag_id in add_tag_ids or []:
                    db.add(
                        BookmarkTagLink(
                            bookmark_id=bookmark_id,
                            tag_id=tag_id,
                        )
                    )

                bookmark.updated_at = utc_now()
                bookmark.version += 1
                bookmark.last_modified_device = device_id

                results.append(
                    {"bookmark_id": bookmark_id, "status": "success"}
                )

        return results
