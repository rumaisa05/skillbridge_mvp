"""add portfolio is_winner

Revision ID: 0002_add_portfolio_is_winner
Revises: 0001_initial_schema
Create Date: 2026-08-09 16:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_portfolio_is_winner'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def _has_column(table, column):
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return False
    return column in {c['name'] for c in inspector.get_columns(table)}


def upgrade():
    # Idempotent: skip if the column already exists.
    if not _has_column('portfolio_entries', 'is_winner'):
        op.add_column(
            'portfolio_entries',
            sa.Column('is_winner', sa.Integer(), nullable=True, server_default='0'),
        )


def downgrade():
    op.drop_column('portfolio_entries', 'is_winner')
