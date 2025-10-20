"""add_images_column_to_products

Revision ID: ae1dd165060f
Revises: 6a3269ced195
Create Date: 2025-10-18 10:31:11.594264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'ae1dd165060f'
down_revision: Union[str, None] = '6a3269ced195'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add images column as an array of strings
    op.add_column('products', sa.Column('images', ARRAY(sa.String()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove images column
    op.drop_column('products', 'images')
