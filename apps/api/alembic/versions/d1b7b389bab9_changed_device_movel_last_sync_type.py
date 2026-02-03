"""changed device movel last sync type

Revision ID: d1b7b389bab9
Revises: 95b19bfa64d0
Create Date: 2026-01-14 21:22:02.323203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1b7b389bab9'
down_revision: Union[str, Sequence[str], None] = '95b19bfa64d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop the column
    op.drop_column("device", "last_known_revision")

    # 2. Recreate it as DateTime
    op.add_column(
        "device",
        sa.Column("last_known_revision", sa.DateTime(), nullable=True)
    )
def downgrade() -> None:
    op.drop_column("device", "last_known_revision")
    op.add_column(
        "device",
        sa.Column("last_known_revision", sa.Integer(), nullable=True)
    )

