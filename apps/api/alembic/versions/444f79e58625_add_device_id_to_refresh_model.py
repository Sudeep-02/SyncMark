"""add device_id to refresh model

Revision ID: 444f79e58625
Revises: 10b73149cfed
Create Date: 2026-01-23 11:53:42.370116
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '444f79e58625'
down_revision: Union[str, Sequence[str], None] = '10b73149cfed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add device_id column as nullable
    op.add_column(
        'refreshtoken',
        sa.Column('device_id', sa.Uuid(), nullable=True)
    )

    # 2. Backfill existing rows
    op.execute(
        sa.text("UPDATE refreshtoken SET device_id = gen_random_uuid()")
    )

    # 3. Enforce NOT NULL constraint
    op.alter_column(
        'refreshtoken',
        'device_id',
        nullable=False
    )

    # 4. Create index on device_id
    op.create_index(
        op.f('ix_refreshtoken_device_id'),
        'refreshtoken',
        ['device_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_refreshtoken_device_id'),
        table_name='refreshtoken'
    )
    op.drop_column('refreshtoken', 'device_id')
