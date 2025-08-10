"""Add price field to campus sessions

Revision ID: 757b2f9f21e6
Revises: 7fa588579ec7
Create Date: 2025-08-08 23:40:44.803456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "757b2f9f21e6"
down_revision: Union[str, None] = "7fa588579ec7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add price column to campus_sessions table
    op.add_column(
        "campus_sessions",
        sa.Column(
            "price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove price column from campus_sessions table
    op.drop_column("campus_sessions", "price")
