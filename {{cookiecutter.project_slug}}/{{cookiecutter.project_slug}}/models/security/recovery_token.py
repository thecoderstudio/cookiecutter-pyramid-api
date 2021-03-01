from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from {{cookiecutter.project_slug}}.models import Base, session
from {{cookiecutter.project_slug}}.models.security.secure_token import SecureTokenMixin


class RecoveryToken(Base, SecureTokenMixin):
    __tablename__ = 'recovery_token'

    for_user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'),
                         nullable=False)

    for_user = relationship('User')


def get_recovery_token_by_id(id_):
    return session.query(RecoveryToken).get(id_)
