"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-08 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def _existing_tables():
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade():
    # Idempotent: the app may already have created these tables (e.g. a database
    # that existed before Alembic was introduced), so only create missing ones.
    existing = _existing_tables()

    if 'users' not in existing:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
            sa.Column('password_hash', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('role', sa.String(), nullable=False, server_default='participant'),
            sa.Column('bio', sa.Text(), nullable=True, server_default=''),
            sa.Column('skills', sa.Text(), nullable=True, server_default='[]'),
            sa.Column('github_url', sa.String(), nullable=True, server_default=''),
            sa.Column('avatar_url', sa.String(), nullable=True, server_default=''),
        )

    if 'challenges' not in existing:
        op.create_table(
            'challenges',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('org_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('category', sa.String(), nullable=True, server_default='web'),
            sa.Column('difficulty', sa.String(), nullable=True, server_default='medium'),
            sa.Column('reward', sa.String(), nullable=True, server_default=''),
            sa.Column('deadline', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(), nullable=True, server_default='open'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'submissions' not in existing:
        op.create_table(
            'submissions',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('challenge_id', sa.Integer(), sa.ForeignKey('challenges.id'), nullable=False),
            sa.Column('participant_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('repo_url', sa.String(), nullable=True, server_default=''),
            sa.Column('description', sa.Text(), nullable=True, server_default=''),
            sa.Column('docs_url', sa.String(), nullable=True, server_default=''),
            sa.Column('demo_url', sa.String(), nullable=True, server_default=''),
            sa.Column('status', sa.String(), nullable=True, server_default='pending'),
            sa.Column('is_winner', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'ai_reports' not in existing:
        op.create_table(
            'ai_reports',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('submission_id', sa.Integer(), sa.ForeignKey('submissions.id'), nullable=False, unique=True),
            sa.Column('overall_score', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('dimension_scores', sa.Text(), nullable=True, server_default='{}'),
            sa.Column('strengths', sa.Text(), nullable=True, server_default='[]'),
            sa.Column('weaknesses', sa.Text(), nullable=True, server_default='[]'),
            sa.Column('recommendations', sa.Text(), nullable=True, server_default='[]'),
            sa.Column('model_used', sa.String(), nullable=True, server_default='mock'),
            sa.Column('summary', sa.Text(), nullable=True, server_default=''),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'portfolio_entries' not in existing:
        op.create_table(
            'portfolio_entries',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('participant_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('challenge_id', sa.Integer(), sa.ForeignKey('challenges.id'), nullable=False),
            sa.Column('submission_id', sa.Integer(), sa.ForeignKey('submissions.id'), nullable=False),
            sa.Column('title', sa.String(), nullable=True, server_default=''),
            sa.Column('description', sa.Text(), nullable=True, server_default=''),
            sa.Column('skills_proven', sa.Text(), nullable=True, server_default='[]'),
            sa.Column('score', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('organization_feedback', sa.Text(), nullable=True, server_default=''),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if 'notifications' not in existing:
        op.create_table(
            'notifications',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('title', sa.String(), nullable=True, server_default=''),
            sa.Column('body', sa.Text(), nullable=True, server_default=''),
            sa.Column('type', sa.String(), nullable=True, server_default='info'),
            sa.Column('read', sa.Boolean(), nullable=True, server_default='false'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )


def downgrade():
    op.drop_table('notifications')
    op.drop_table('portfolio_entries')
    op.drop_table('ai_reports')
    op.drop_table('submissions')
    op.drop_table('challenges')
    op.drop_table('users')
