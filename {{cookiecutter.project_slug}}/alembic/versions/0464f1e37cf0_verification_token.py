import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from {{cookiecutter.project_slug}}.models.functions import utcnow


# revision identifiers, used by Alembic.
revision = '0464f1e37cf0'
down_revision = '67b7cdb50818'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'verification_token',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(119), nullable=False),
        sa.Column('token_salt', sa.String(29), nullable=False),
        sa.Column('used', sa.Boolean(), default=False, nullable=False),
        sa.Column('invalidated', sa.Boolean, default=False, nullable=False),
        sa.Column(
            'expires_on',
            sa.DateTime,
            default=utcnow() + datetime.timedelta(
                hours=24
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
    op.drop_table('verification_token')
