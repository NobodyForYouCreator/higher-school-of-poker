"""init

Revision ID: cb21ea9567ea
Revises: bceeb1b0e54a
Create Date: 2025-12-18 19:33:38.120398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb21ea9567ea'
down_revision: Union[str, Sequence[str], None] = 'bceeb1b0e54a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
