"""Add manager role to UserRole enum

Revision ID: add_manager_role
Revises: c975fca00cf8_added_score_to_custom_achievements_table
Create Date: 2026-01-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_manager_role"
down_revision = "c975fca00cf8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE 'MANAGER'")


def downgrade() -> None:
    pass
