from uuid import UUID
from datetime import datetime, timezone
from typing import List

from sqlmodel import Session, select

from app.models.bookmark_model import Bookmark
from app.schemas.sync_schema import (
    SyncRequest,
    SyncResponse,
    AcceptedItem,
    ConflictItem,
    BookmarkResponse,
)
from app.services.bookmark_service import BookmarkService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SyncService:

    @staticmethod
    def process_sync(
        db: Session,
        user_id: UUID,
        sync_request: SyncRequest,
    ) -> SyncResponse:

        accepted_changes: List[AcceptedItem] = []
        conflict_changes: List[ConflictItem] = []
        server_side_changes: List[BookmarkResponse] = []

        server_time = utc_now()

        # 1️⃣ Apply client-side deltas
        for client_delta in sync_request.deltas:

            # --- Create ---
            if client_delta.id is None:
                bookmark = BookmarkService.create_bookmark(
                    db=db,
                    user_id=user_id,
                    payload=client_delta,
                    device_id=sync_request.device_id,
                )

                accepted_changes.append(
                    AcceptedItem(
                        local_id=client_delta.local_id,
                        bookmark=BookmarkResponse.from_orm(bookmark),
                    )
                )
                continue

            bookmark = db.get(Bookmark, client_delta.id)
            if not bookmark or bookmark.user_id != user_id:
                continue

            # --- Delete ---
            if client_delta.deleted:
                BookmarkService.soft_delete_bookmark(
                    db=db,
                    user_id=user_id,
                    bookmark_id=bookmark.id,
                    device_id=sync_request.device_id,
                )

                accepted_changes.append(
                    AcceptedItem(
                        local_id=client_delta.local_id,
                        bookmark=BookmarkResponse.from_orm(bookmark),
                    )
                )
                continue

            # --- Conflict detection ---
            if client_delta.version != bookmark.version:
                conflict_changes.append(
                    ConflictItem(
                        bookmark_id=bookmark.id,
                        server_bookmark=BookmarkResponse.from_orm(bookmark),
                    )
                )
                continue

            # --- Update ---
            bookmark = BookmarkService.update_bookmark(
                db=db,
                user_id=user_id,
                bookmark_id=bookmark.id,
                payload=client_delta,
                device_id=sync_request.device_id,
            )

            accepted_changes.append(
                AcceptedItem(
                    local_id=client_delta.local_id,
                    bookmark=BookmarkResponse.from_orm(bookmark),
                )
            )

        # 2️⃣ Server-side changes
        last_sync_time = sync_request.last_sync_at
        if last_sync_time is not None:
            query = select(Bookmark).where(
                Bookmark.user_id == user_id,
                Bookmark.updated_at > last_sync_time,  # type: ignore[arg-type]
            )

            server_side_changes = [
                BookmarkResponse.from_orm(bookmark)
                for bookmark in db.exec(query).all()
            ]

        return SyncResponse(
            accepted=accepted_changes,
            conflicts=conflict_changes,
            server_changes=server_side_changes,
            server_time=server_time,
        )
