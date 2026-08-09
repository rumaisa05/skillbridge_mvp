"""add org profile fields

Revision ID: 0003_add_org_profile_fields
Revises: 0002_add_portfolio_is_winner
Create Date: 2026-08-09 17:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_org_profile_fields'
down_revision = '0002_add_portfolio_is_winner'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('org_type', sa.String(), nullable=True, server_default=''),
    )
    op.add_column(
        'users',
        sa.Column('website', sa.String(), nullable=True, server_default=''),
    )


def downgrade():
    op.drop_column('users', 'website')
    op.drop_column('users', 'org_type')
