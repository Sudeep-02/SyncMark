from fastapi import APIRouter, Depends, HTTPException,status
from uuid import UUID
from sqlmodel import Session

from app.schemas.bulk_schema import (
    BulkMoveRequest,
    BulkDeleteRequest,
    BulkTagEditRequest,
    BulkResponse
)
from app.services.bulk_service import BulkService
from app.core.database import get_session
from app.deps.auth import get_current_user

router = APIRouter(prefix="/bulk", tags=["Bulk"])


@router.post("/move", response_model=BulkResponse)
def bulk_move(
    payload: BulkMoveRequest,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    # if payload.target_folder_id is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="target_folder_id is required for bulk move",
    #     )
    
    return {
        "results": BulkService.bulk_move_bookmarks(
            db,
            user_id,
            payload.bookmark_ids,
            payload.target_folder_id,
            payload.device_id,
        )
    }


@router.post("/delete", response_model=BulkResponse)
def bulk_delete(
    payload: BulkDeleteRequest,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    return {
        "results": BulkService.bulk_delete_bookmarks(
            db,
            user_id,
            payload.bookmark_ids,
            payload.device_id,
        )
    }


@router.post("/tag-edit", response_model=BulkResponse)
def bulk_tag_edit(
    payload: BulkTagEditRequest,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    return {
        "results": BulkService.bulk_tag_edit_bookmarks(
            db,
            user_id,
            payload.bookmark_ids,
            payload.add_tag_ids or [],
            payload.remove_tag_ids or [],
            payload.device_id,
        )
    }
