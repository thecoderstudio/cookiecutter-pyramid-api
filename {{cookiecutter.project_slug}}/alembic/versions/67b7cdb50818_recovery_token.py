import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from {{cookiecutter.project_slug}}.models.functions import utcnow


# revision identifiers, used by Alembic.
revision = '67b7cdb50818'
down_revision = '71103838e7b3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'recovery_token',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(119), nullable=False),
        sa.Column('token_salt', sa.String(29), nullable=False),
        sa.Column('used', sa.Boolean(), default=False, nullable=True),
        sa.Column('invalidated', sa.Boolean, default=False, nullable=False),
        sa.Column(
            'expires_on',
            sa.DateTime,
            default=utcnow() + datetime.timedelta(
                hours=1
            ),
            nullable=False
        ),
        sa.Column(
            'for_user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('user.id'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('recovery_token')
