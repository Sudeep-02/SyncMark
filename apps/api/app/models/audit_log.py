from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime, timezone


class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: UUID
    action: str
    entity: str
    entity_id: UUID | None = None
    device_id: UUID | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
