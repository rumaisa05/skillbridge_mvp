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


def upgrade():
    op.add_column(
        'portfolio_entries',
        sa.Column('is_winner', sa.Integer(), nullable=True, server_default='0'),
    )


def downgrade():
    op.drop_column('portfolio_entries', 'is_winner')
