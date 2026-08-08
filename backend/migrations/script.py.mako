<%!
from alembic import util
%>
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
"""

from alembic import op
import sqlalchemy as sa

${imports if imports else ""}


def upgrade():
${upgrades if upgrades else "    pass"}


def downgrade():
${downgrades if downgrades else "    pass"}
