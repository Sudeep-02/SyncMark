from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from uuid import UUID

from app.schemas.sync_schema import SyncRequest, SyncResponse
from app.services.sync_service import SyncService
from app.core.database import get_session
from app.deps.auth import get_current_user

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/", response_model=SyncResponse, status_code=status.HTTP_200_OK)
def sync(
    payload: SyncRequest,
    db: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user),
):
    return SyncService.process_sync(db, user_id, payload)
