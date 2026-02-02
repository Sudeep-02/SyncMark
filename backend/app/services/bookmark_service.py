from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import HTTPException
from sqlmodel import Session, select, delete

from app.models.bookmark_model import Bookmark
from app.models.folder_model import Folder
from app.models.device_model import Device
from app.models.tag_model import BookmarkTagLink
from app.services.tag_service import TagService
from app.tasks.bookmark_tasks import fetch_metadata
from app.services.folder_service import validate_user_folder

def utc_now():
    return datetime.now(timezone.utc)


class BookmarkService:

    # ---------- READ ----------

    @staticmethod
    def list_user_bookmarks(
        db: Session,
        user_id: UUID,
        include_deleted: bool = False,
        featured: Optional[bool] = None,
        folder_id: Optional[UUID] = None,
    ) -> Sequence[Bookmark]:
        print(user_id)
        statement = select(Bookmark).where(Bookmark.user_id == user_id)

        if not include_deleted:
            statement = statement.where(Bookmark.deleted_at.is_(None)) # type: ignore

        if featured is not None:
            statement = statement.where(Bookmark.is_featured == featured)

        if folder_id is not None:
            statement = statement.where(Bookmark.folder_id == folder_id)

        return db.exec(statement).all()

    @staticmethod
    def get_user_bookmark(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
    ) -> Bookmark:

        bookmark = db.get(Bookmark, bookmark_id)

        if (
            not bookmark
            or bookmark.user_id != user_id
            or bookmark.deleted_at is not None
        ):
            raise HTTPException(status_code=404, detail="Bookmark not found")

        return bookmark

    # ---------- CREATE ----------

    @staticmethod
    def create_bookmark(
        db: Session,
        user_id: UUID,
        payload,
        device_id: UUID,
    ) -> Bookmark:
      
            
        device = db.exec(
            select(Device).where(
                Device.device_id == device_id,
                Device.user_id == user_id
            )
        ).first()
        
        
        if device is None:
            print(device)
            raise HTTPException(status_code=401, detail="Invalid device")

        validate_user_folder(db, user_id, payload.folder_id)

        TagService.validate_ids(db, user_id, payload.tag_ids)

        bookmark = Bookmark(
            user_id=user_id,
            url=str(payload.url),
            title=payload.title,
            description=payload.description,
            favicon_url=str(payload.favicon_url) if payload.favicon_url else None,
            folder_id=payload.folder_id,
            is_featured=payload.is_featured or False,
            version=1,
            last_modified_device=device_id,
            updated_at=utc_now(),
        )

        # Atomic DB write
        db.add(bookmark)
        # print("validated device.device_id:", device.device_id)
        # print("used last_modified_device:", device_id)

        db.flush() # temporary commit for getting bookmark.id
        

        for tag_id in payload.tag_ids or []:
            db.add(
                BookmarkTagLink(
                    bookmark_id=bookmark.id,
                    tag_id=tag_id,
                )
            )
        db.commit() 
        db.refresh(bookmark)

        # Post-commit async task
        fetch_metadata.delay(str(bookmark.id))

        return bookmark

    # ---------- UPDATE ----------

    @staticmethod
    def update_bookmark(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
        payload,
        device_id: UUID,
    ) -> Bookmark:

        bookmark = BookmarkService.get_user_bookmark(db, user_id, bookmark_id)
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        device = db.exec(
            select(Device).where(
                Device.device_id == device_id,
                Device.user_id == user_id
            )
        ).first()

        if not device:
            raise HTTPException(status_code=401, detail="Invalid device")

        update_data = payload.model_dump(exclude_unset=True)

        if "folder_id" in update_data and update_data["folder_id"] is not None:
            folder = db.get(Folder, update_data["folder_id"])
            if not folder or folder.user_id != user_id:
                raise HTTPException(status_code=403, detail="Invalid folder")

        if "tag_ids" in update_data:
            TagService.validate_ids(db, user_id, update_data["tag_ids"])

        for field, value in update_data.items():
            if field != "tag_ids":
                setattr(bookmark, field, value)

        bookmark.version += 1
        bookmark.updated_at = utc_now()
        bookmark.last_modified_device = device.device_id

        if "tag_ids" in update_data:
            db.execute(
                delete(BookmarkTagLink).where(
                    BookmarkTagLink.bookmark_id == bookmark.id # type: ignore
                )
            )
            for tag_id in update_data["tag_ids"]:
                db.add(
                    BookmarkTagLink(
                        bookmark_id=bookmark.id,
                        tag_id=tag_id
                    )
                )

        db.commit()
        db.refresh(bookmark)

        if "url" in update_data:
            fetch_metadata.delay(str(bookmark.id))

        return bookmark

    # ---------- DELETE ----------

    @staticmethod
    def soft_delete_bookmark(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
        device_id: UUID,
    ) -> Bookmark:

        bookmark = BookmarkService.get_user_bookmark(db, user_id, bookmark_id)
        
        device = db.exec(
            select(Device).where(
                Device.device_id == device_id,
                Device.user_id == user_id
            )
        ).first()

        if not device:
            raise HTTPException(status_code=401, detail="Invalid device")

        bookmark.deleted_at = utc_now()
        bookmark.deleted_by_device = device_id
        bookmark.version += 1
        bookmark.last_modified_device = device_id
        bookmark.updated_at = utc_now()

        db.commit()
        db.refresh(bookmark)

        return bookmark
