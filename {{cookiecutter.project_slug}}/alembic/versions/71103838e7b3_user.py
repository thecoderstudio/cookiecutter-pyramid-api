import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '71103838e7b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('email_address', sa.String(320), unique=True,
                  nullable=False),
        sa.Column('password_hash', sa.String(119), nullable=False),
        sa.Column('password_salt', sa.String(29), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user')
