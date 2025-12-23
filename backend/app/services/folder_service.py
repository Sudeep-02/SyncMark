from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.folder_model import Folder
from app.models.bookmark_model import Bookmark  # existing bookmark model
from app.schemas.folder_schema import FolderCreate, FolderUpdate


# Helper: fetch folder + validate ownership
def get_user_folder(db: Session, user_id: UUID, folder_id: UUID) -> Folder:
    folder = db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    if folder.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Not your folder")
    return folder


# Create folder
def create_folder(db: Session, user_id: UUID, payload: FolderCreate) -> Folder:
    # If parent_id provided, validate it belongs to user
    if payload.parent_id is not None:
        parent = db.get(Folder, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent folder not found")
        if parent.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent folder does not belong to you")

    folder = Folder(user_id=user_id, name=payload.name.strip(), parent_id=payload.parent_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


# List folders for user (flat)
def list_folders(db: Session, user_id: UUID) -> List[Folder]:
    stmt = select(Folder).where(Folder.user_id == user_id)
    return list(db.exec(stmt).all())


# Optional: list top-level folders (parent_id is null)
def list_root_folders(db: Session, user_id: UUID) -> List[Folder]:
    stmt = select(Folder).where(
    Folder.user_id == user_id,
    Folder.parent_id == None,
)
    return list(db.exec(stmt).all())


# Update folder (may move parent)
def update_folder(db: Session, user_id: UUID, folder_id: UUID, payload: FolderUpdate) -> Folder:
    folder = get_user_folder(db, user_id, folder_id)

    update_data = payload.model_dump(exclude_unset=True)

    # If changing parent, must validate new parent and prevent cycles
    if "parent_id" in update_data:
        new_parent_id = update_data["parent_id"]
        if new_parent_id == folder.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder cannot be its own parent")
        if new_parent_id is not None:
            new_parent = db.get(Folder, new_parent_id)
            if not new_parent:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New parent not found")
            if new_parent.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="New parent does not belong to you")

            # Prevent cycles: ensure new_parent is not a descendant of folder
            # Walk up from new_parent to root and check we do not see folder.id
            curr = new_parent
            while curr is not None:
                if curr.id == folder.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot move folder into its own descendant")
                if curr.parent_id is None:
                    break
                curr = db.get(Folder, curr.parent_id)

    if "name" in update_data:
        folder.name = update_data["name"].strip()

    # apply parent_id (explicitly set or cleared)
    if "parent_id" in update_data:
        folder.parent_id = update_data["parent_id"]

    folder.updated_at = datetime.now(timezone.utc)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


# Delete folder
def delete_folder(db: Session, user_id: UUID, folder_id: UUID, mode: str = "reject") -> dict:
    """
    mode:
      - "reject" (default) -> if folder contains bookmarks or children, raise 400
      - "move_children_to_parent" -> move child folders and bookmarks to parent_id
      - "move_to_root" -> move children/bookmarks to root (parent_id = None)
      - "cascade" -> delete children and optionally bookmarks (DANGEROUS)
    """
    folder = get_user_folder(db, user_id, folder_id)

    # check children folders
    children_stmt = select(Folder).where(Folder.parent_id == folder_id)
    children = db.exec(children_stmt).all()

    # check bookmarks inside folder
    bookmarks_stmt = select(Bookmark).where(Bookmark.folder_id == folder_id, Bookmark.user_id == user_id)
    bookmarks = db.exec(bookmarks_stmt).all()

    if mode == "reject":
        if children or bookmarks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Folder not empty. Use another mode to move or cascade.")
        db.delete(folder)
        db.commit()
        return {"deleted": True}

    elif mode == "move_children_to_parent":
        # move children folders to this folder's parent
        for child in children:
            child.parent_id = folder.parent_id
            db.add(child)

        # move bookmarks to this folder's parent (could be None)
        for bm in bookmarks:
            bm.folder_id = folder.parent_id
            db.add(bm)

        db.delete(folder)
        db.commit()
        return {"deleted": True, "moved_children_to_parent": True}

    elif mode == "move_to_root":
        for child in children:
            child.parent_id = None
            db.add(child)
        for bm in bookmarks:
            bm.folder_id = None
            db.add(bm)
        db.delete(folder)
        db.commit()
        return {"deleted": True, "moved_to_root": True}

    elif mode == "cascade":
        # recursively delete children (dangerous). We'll implement a simple recursion
        def delete_recursive(fold: Folder):
            # delete bookmarks in this folder
            bms_stmt = select(Bookmark).where(Bookmark.folder_id == fold.id, Bookmark.user_id == user_id)
            bms = db.exec(bms_stmt).all()
            for bm in bms:
                db.delete(bm)
            # children
            child_stmt = select(Folder).where(Folder.parent_id == fold.id)
            kids = db.exec(child_stmt).all()
            for kid in kids:
                delete_recursive(kid)
            db.delete(fold)

        delete_recursive(folder)
        db.commit()
        return {"deleted": True, "cascaded": True}

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown mode")
