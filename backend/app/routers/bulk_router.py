from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID

from app.schemas.bulk_schema import BulkMoveRequest, BulkDeleteRequest, BulkTagEditRequest, BulkResponse
from app.services.bulk_service import bulk_move_bookmarks, bulk_delete_bookmarks, bulk_tag_edit_bookmarks

from app.core.database import get_session
from app.deps.auth import get_current_user

router = APIRouter(prefix="/bulk", tags=["Bulk"])


@router.post("/move", response_model=BulkResponse)
def bulk_move(payload: BulkMoveRequest, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    results = bulk_move_bookmarks(db, user_id, payload.bookmark_ids, payload.target_folder_id, payload.device_id)
    return {"results": results}


@router.post("/delete", response_model=BulkResponse)
def bulk_delete(payload: BulkDeleteRequest, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    results = bulk_delete_bookmarks(db, user_id, payload.bookmark_ids, payload.device_id)
    return {"results": results}


@router.post("/tag-edit", response_model=BulkResponse)
def bulk_tag_edit(payload: BulkTagEditRequest, db: Session = Depends(get_session), user_id: UUID = Depends(get_current_user)):
    results = bulk_tag_edit_bookmarks(db, user_id, payload.bookmark_ids, payload.add_tag_ids or [], payload.remove_tag_ids or [], payload.device_id)
    return {"results": results}
