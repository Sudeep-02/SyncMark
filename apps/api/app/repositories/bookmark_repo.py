from uuid import UUID
from sqlmodel import Session, select, delete
from app.models.bookmark_model import Bookmark
from app.models.tag_model import BookmarkTagLink

class BookmarkRepository:

    @staticmethod
    def get_by_id(db: Session, bookmark_id: UUID):
        return db.get(Bookmark, bookmark_id)

    @staticmethod
    def list_by_user(db: Session, user_id: UUID, *, folder_id=None, featured=None):
        stmt = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.deleted_at == None
        )

        if folder_id:
            stmt = stmt.where(Bookmark.folder_id == folder_id)
        if featured is not None:
            stmt = stmt.where(Bookmark.is_featured == featured)

        return db.exec(stmt).all()

    @staticmethod
    def create(db: Session, bookmark: Bookmark):
        db.add(bookmark)
        db.flush()
        return bookmark

    @staticmethod
    def delete_tags(db: Session, bookmark_id: UUID):
        stmt = delete(BookmarkTagLink).where(
            BookmarkTagLink.bookmark_id == bookmark_id # type: ignore
        )
        db.execute(stmt)
