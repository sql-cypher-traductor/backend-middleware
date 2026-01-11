"""chore: initialize alembic infrastructure

Revision ID: 45ba80957fff
Revises: 1bbbd0e9e38a
Create Date: 2026-01-11 17:02:53.009601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45ba80957fff'
down_revision: Union[str, Sequence[str], None] = '1bbbd0e9e38a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
