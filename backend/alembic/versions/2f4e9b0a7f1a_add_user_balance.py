"""add user balance

Revision ID: 2f4e9b0a7f1a
Revises: 8da2d054d53f
Create Date: 2025-12-24 02:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "2f4e9b0a7f1a"
down_revision: Union[str, Sequence[str], None] = "8da2d054d53f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("balance", sa.BigInteger(), nullable=False, server_default="5000"))


def downgrade() -> None:
    op.drop_column("users", "balance")

