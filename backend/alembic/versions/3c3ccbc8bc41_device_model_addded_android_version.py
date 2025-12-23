"""device model added android version

Revision ID: 3c3ccbc8bc41
Revises: 563ee81ce39c
Create Date: 2025-12-12 12:04:49.795416
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3c3ccbc8bc41'
down_revision: Union[str, Sequence[str], None] = '563ee81ce39c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add android_version column using standard SQLAlchemy type
    op.add_column('device', sa.Column('android_version', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('device', 'android_version')
