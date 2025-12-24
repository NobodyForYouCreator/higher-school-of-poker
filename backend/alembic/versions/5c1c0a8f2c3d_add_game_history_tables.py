"""add game history tables

Revision ID: 5c1c0a8f2c3d
Revises: 2f4e9b0a7f1a
Create Date: 2025-12-24 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "5c1c0a8f2c3d"
down_revision: Union[str, Sequence[str], None] = "2f4e9b0a7f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "finished_games",
        sa.Column("uuid", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("table_id", sa.Integer(), nullable=False),
        sa.Column("pot", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("board", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("winners", postgresql.ARRAY(sa.Integer()), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )

    op.create_table(
        "player_games",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("finished_game_uuid", sa.Integer(), nullable=False),
        sa.Column("table_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hole_cards", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("bet", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("net_stack_delta", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("resulting_balance", sa.BigInteger(), nullable=True),
        sa.Column("won_hand", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(["finished_game_uuid"], ["finished_games.uuid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_player_games_user_id"), "player_games", ["user_id"], unique=False)
    op.create_index(op.f("ix_player_games_finished_game_uuid"), "player_games", ["finished_game_uuid"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_player_games_finished_game_uuid"), table_name="player_games")
    op.drop_index(op.f("ix_player_games_user_id"), table_name="player_games")
    op.drop_table("player_games")
    op.drop_table("finished_games")

