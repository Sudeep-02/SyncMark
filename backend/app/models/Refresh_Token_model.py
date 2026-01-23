from sqlmodel import Field, SQLModel, Column
from uuid import UUID
from datetime import datetime,timezone
from sqlalchemy import DateTime

class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)   # UUID (match user id type)
    device_id: UUID = Field(index=True,nullable=False)
    jti: str = Field(index=True, nullable=False, unique=True)
    token_hash: str = Field(nullable=False)
    user_agent: str | None = None
    ip_address: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    expires_at: datetime | None  = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True))
    revoked: bool = Field(default=False)
