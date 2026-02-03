"""device model changed device_id to UUID

Revision ID: 6c90abe92fcf
Revises: 3c3ccbc8bc41
Create Date: 2025-12-12 12:09:36.996113
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6c90abe92fcf'
down_revision = '3c3ccbc8bc41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert device_id to UUID using PostgreSQL cast
    op.execute("""
        ALTER TABLE device
        ALTER COLUMN device_id
        TYPE UUID
        USING device_id::uuid
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Convert device_id back to string
    op.execute("""
        ALTER TABLE device
        ALTER COLUMN device_id
        TYPE VARCHAR
        USING device_id::text
    """)
