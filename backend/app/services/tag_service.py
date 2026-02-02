from typing import List, Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, select, delete, col

from app.models.tag_model import Tag, BookmarkTagLink
from app.models.bookmark_model import Bookmark


class TagService:
    # ---------- TAG CRUD ----------

    @staticmethod
    def create_tag(
        db: Session,
        user_id: UUID,
        name: str,
    ) -> Tag:
        
        # print("CREATE TAG CALLED:", name)
        normalized_name = name.strip()

        query = select(Tag).where(
            Tag.user_id == user_id,
            Tag.name == normalized_name,
        )
        existing_tag = db.exec(query).first()
        if existing_tag:
            return existing_tag

        new_tag = Tag(
            user_id=user_id,
            name=normalized_name,
        )
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)

        return new_tag

    @staticmethod
    def list_tags(
        db: Session,
        user_id: UUID,
    ) -> Sequence[Tag]:
        query = select(Tag).where(Tag.user_id == user_id)
        return db.exec(query).all()

    @staticmethod
    def get_tag(
        db: Session,
        user_id: UUID,
        tag_id: UUID,
    ) -> Tag:
        tag = db.get(Tag, tag_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found",
            )

        if tag.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your tag",
            )

        return tag

    # ---------- VALIDATION ----------

    @staticmethod
    def validate_ids(
        db: Session,
        user_id: UUID,
        tag_ids: Optional[List[UUID]],
    ) -> None:
        if not tag_ids:
            return

        query = select(Tag.id, Tag.user_id).where(
            col(Tag.id).in_(tag_ids)  # type: ignore[attr-defined]
        )
        rows = db.exec(query).all()

        found_tag_ids = {row[0] for row in rows}
        missing_tag_ids = set(tag_ids) - found_tag_ids
        if missing_tag_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag IDs: {missing_tag_ids}",
            )

        foreign_tag_ids = {row[0] for row in rows if row[1] != user_id}
        if foreign_tag_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tags not owned by user: {foreign_tag_ids}",
            )

    # ---------- BOOKMARK ↔ TAG OPERATIONS ----------

    @staticmethod
    def add_tags_to_bookmark(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
        tag_ids: List[UUID],
    ) -> None:
        bookmark = db.get(Bookmark, bookmark_id)
        if not bookmark or bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found",
            )

        TagService.validate_ids(db, user_id, tag_ids)

        query = select(BookmarkTagLink.tag_id).where(
            BookmarkTagLink.bookmark_id == bookmark_id
        )
        existing_tag_ids = set(db.exec(query).all())

        for tag_id in tag_ids:
            if tag_id not in existing_tag_ids:
                db.add(
                    BookmarkTagLink(
                        bookmark_id=bookmark_id,
                        tag_id=tag_id,
                    )
                )

        db.commit()

    @staticmethod
    def remove_tags_from_bookmark(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
        tag_ids: List[UUID],
    ) -> None:
        bookmark = db.get(Bookmark, bookmark_id)
        if not bookmark or bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found",
            )

        query = delete(BookmarkTagLink).where(
            BookmarkTagLink.bookmark_id == bookmark_id, # type: ignore
            BookmarkTagLink.tag_id.in_(tag_ids),  # type: ignore[attr-defined]
        )
        db.execute(query)
        db.commit()

    @staticmethod
    def clear_all_tags(
        db: Session,
        user_id: UUID,
        bookmark_id: UUID,
    ) -> None:
        bookmark = db.get(Bookmark, bookmark_id)
        if not bookmark or bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found",
            )

        query = delete(BookmarkTagLink).where(
            BookmarkTagLink.bookmark_id == bookmark_id  # type: ignore[arg-type]
        )
        db.execute(query)
        db.commit()
