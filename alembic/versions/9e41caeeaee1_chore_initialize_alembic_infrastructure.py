"""chore: initialize alembic infrastructure

Revision ID: 9e41caeeaee1
Revises: 45ba80957fff
Create Date: 2026-01-11 18:17:38.738034

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e41caeeaee1"
down_revision: Union[str, Sequence[str], None] = "45ba80957fff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
