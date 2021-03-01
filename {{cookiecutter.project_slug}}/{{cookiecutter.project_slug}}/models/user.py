import uuid

from pyramid.security import Allow
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from {{cookiecutter.project_slug}}.lib.resources import LocationAwareResource
from {{cookiecutter.project_slug}}.models import Base, session


class User(Base, LocationAwareResource):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_address = Column(String(320), unique=True, nullable=False)
    password_hash = Column(String(119), nullable=False)
    password_salt = Column(String(29), nullable=False)

    active_recovery_token = relationship(
        'RecoveryToken',
        uselist=False,
        primaryjoin="and_(User.id==RecoveryToken.for_user_id, "
        "RecoveryToken.active==True)"
    )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __acl__(self):
        return (
            (Allow, f"user:{self.id}", 'user.patch'),
            (Allow, f"user:{self.id}", 'user.get'),
            (Allow, f"recovering_user:{self.id}", 'user.reset_password')
        )


def _get_user_by_email_address(email_address):
    return session.query(User).filter(
        User.email_address == email_address
    )


def get_user_by_email_address(email_address):
    return _get_user_by_email_address(email_address).one_or_none()


def get_one_user_by_email_address(email_address):
    return _get_user_by_email_address(email_address).one()


def get_one_user_by_id(id_):
    return session.query(User).filter(User.id == id_).one()


def get_user_by_id(id_):
    return session.query(User).get(id_)
