"""init

Revision ID: cb21ea9567ea
Revises:
Create Date: 2025-12-18 19:33:38.120398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cb21ea9567ea"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass