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


def _has_column(table, column):
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return False
    return column in {c['name'] for c in inspector.get_columns(table)}


def upgrade():
    # Idempotent: skip columns that already exist.
    if not _has_column('users', 'org_type'):
        op.add_column(
            'users',
            sa.Column('org_type', sa.String(), nullable=True, server_default=''),
        )
    if not _has_column('users', 'website'):
        op.add_column(
            'users',
            sa.Column('website', sa.String(), nullable=True, server_default=''),
        )


def downgrade():
    op.drop_column('users', 'website')
    op.drop_column('users', 'org_type')
