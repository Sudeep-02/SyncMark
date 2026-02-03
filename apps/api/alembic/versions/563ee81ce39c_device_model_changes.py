"""device model changes

Revision ID: 563ee81ce39c
Revises: c17186e7ce59
Create Date: 2025-12-12 11:48:31.744749
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '563ee81ce39c'
down_revision: Union[str, Sequence[str], None] = 'c17186e7ce59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Add columns using standard SQLAlchemy types
    op.add_column('device', sa.Column('device_id', sa.String(), nullable=False))
    op.add_column('device', sa.Column('os', sa.String(), nullable=True))
    op.add_column('device', sa.Column('user_agent', sa.String(), nullable=True))
    op.add_column('device', sa.Column('ip', sa.String(), nullable=True))
    # Create unique index
    op.create_index(op.f('ix_device_device_id'), 'device', ['device_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_device_device_id'), table_name='device')
    op.drop_column('device', 'ip')
    op.drop_column('device', 'user_agent')
    op.drop_column('device', 'os')
    op.drop_column('device', 'device_id')
