# from fastapi import APIRouter, Depends, status
# from sqlmodel import Session
# from app.schemas.sync_schema import SyncRequest, SyncResponse
# from app.services.sync_service import process_sync
# from app.core.database import get_session
# from app.deps.auth import get_current_user
# from uuid import UUID

# router = APIRouter(prefix="/sync", tags=["Sync"])


# @router.post("/", response_model=SyncResponse, status_code=status.HTTP_200_OK)
# def sync_endpoint(
#     payload: SyncRequest,
#     db: Session = Depends(get_session),
#     user_id: UUID = Depends(get_current_user)
# ):
#     return process_sync(db, user_id, payload)
