from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.folder_model import Folder
from app.models.bookmark_model import Bookmark  # existing bookmark model
from app.schemas.folder_schema import FolderCreate, FolderUpdate


# Helper: fetch folder + validate ownership
def get_user_folder(session: Session, user_id: UUID, folder_id: UUID) -> Folder:
    folder = session.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    if folder.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Not your folder")
    return folder


# Create folder
def create_folder(session: Session, user_id: UUID, folder_in: FolderCreate) -> Folder:
    # If parent_id provided, validate it belongs to user
    if folder_in.parent_id is not None:
        parent = session.get(Folder, folder_in.parent_id)
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent folder not found")
        if parent.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent folder does not belong to you")

    folder = Folder(user_id=user_id, name=folder_in.name.strip(), parent_id=folder_in.parent_id)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


# List folders for user (flat)
def list_folders(session: Session, user_id: UUID) -> List[Folder]:
    stmt = select(Folder).where(Folder.user_id == user_id)
    return list(session.exec(stmt).all())


# Optional: list top-level folders (parent_id is null)
def list_root_folders(session: Session, user_id: UUID) -> List[Folder]:
    stmt = select(Folder).where(
        Folder.user_id == user_id,
        Folder.parent_id == None,
    )
    return list(session.exec(stmt).all())


# Update folder (may move parent)
def update_folder(session: Session, user_id: UUID, folder_id: UUID, payload: FolderUpdate) -> Folder:
    folder = get_user_folder(session, user_id, folder_id)

    update_data = payload.model_dump(exclude_unset=True)

    # If changing parent, must validate new parent and prevent cycles
    if "parent_id" in update_data:
        new_parent_id = update_data["parent_id"]
        if new_parent_id == folder.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder cannot be its own parent")
        if new_parent_id is not None:
            new_parent = session.get(Folder, new_parent_id)
            if not new_parent:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New parent not found")
            if new_parent.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="New parent does not belong to you")

            current = new_parent
            while current is not None:
                if current.id == folder.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move folder into its own descendant")
                if current.parent_id is None:
                    break
                current = session.get(Folder, current.parent_id)

    if "name" in update_data:
        folder.name = update_data["name"].strip()

    if "parent_id" in update_data:
        folder.parent_id = update_data["parent_id"]

    folder.updated_at = datetime.now(timezone.utc)
    session.add(folder)
    session.commit()
    session.refresh(folder)
    return folder


# Delete folder
def delete_folder(session: Session, user_id: UUID, folder_id: UUID, mode: str = "reject") -> dict:
    folder = get_user_folder(session, user_id, folder_id)

    children_stmt = select(Folder).where(Folder.parent_id == folder_id)
    children = session.exec(children_stmt).all()

    bookmarks_stmt = select(Bookmark).where(Bookmark.folder_id == folder_id, Bookmark.user_id == user_id)
    bookmarks = session.exec(bookmarks_stmt).all()

    if mode == "reject":
        if children or bookmarks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Folder not empty. Use another mode to move or cascade.")
        session.delete(folder)
        session.commit()
        return {"deleted": True}

    elif mode == "move_children_to_parent":
        for child in children:
            child.parent_id = folder.parent_id
            session.add(child)

        for bookmark in bookmarks:
            bookmark.folder_id = folder.parent_id
            session.add(bookmark)

        session.delete(folder)
        session.commit()
        return {"deleted": True, "moved_children_to_parent": True}

    elif mode == "move_to_root":
        for child in children:
            child.parent_id = None
            session.add(child)
        for bookmark in bookmarks:
            bookmark.folder_id = None
            session.add(bookmark)
        session.delete(folder)
        session.commit()
        return {"deleted": True, "moved_to_root": True}

    elif mode == "cascade":
        try:
            def delete_recursive(folder_node: Folder):
                bookmarks = session.exec(
                    select(Bookmark).where(
                        Bookmark.folder_id == folder_node.id,
                        Bookmark.user_id == user_id,
                    )
                ).all()
                for bookmark in bookmarks:
                    session.delete(bookmark)

                children = session.exec(
                    select(Folder).where(Folder.parent_id == folder_node.id)
                ).all()
                for child in children:
                    delete_recursive(child)

                session.delete(folder_node)

            delete_recursive(folder)
            session.commit()
            return {"deleted": True, "cascaded": True}

        except Exception:
            session.rollback()
            raise

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown mode")


def validate_user_folder(
    session: Session,
    user_id: UUID,
    folder_id: Optional[UUID],
) -> None:
    if folder_id is None:
        return

    folder = session.get(Folder, folder_id)
    if not folder or folder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid folder",
        )
