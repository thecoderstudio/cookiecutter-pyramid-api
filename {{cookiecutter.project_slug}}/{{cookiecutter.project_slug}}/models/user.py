import uuid

from pyramid.security import Allow
from sqlalchemy import Boolean, Column, String
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
    verified = Column(Boolean, nullable=False, default=False)

    active_recovery_token = relationship(
        'RecoveryToken',
        uselist=False,
        primaryjoin="and_(User.id==RecoveryToken.for_user_id, "
        "RecoveryToken.active==True)"
    )
    active_verification_token = relationship(
        'VerificationToken',
        uselist=False,
        primaryjoin="and_(User.id==VerificationToken.for_user_id, "
        "VerificationToken.active==True)"
    )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __acl__(self):
        user_principal = f"user:{self.id}"
        return (
            (Allow, user_principal, 'user.patch'),
            (Allow, user_principal, 'user.get'),
            (Allow, user_principal, 'user.request_verification_token'),
            (Allow, f"recovering_user:{self.id}", 'user.reset_password')
        )

    def set_fields(self, **kwargs):
        if kwargs.get('verified'):
            kwargs.pop('verified')
            self.set_verified()

        super().set_fields(**kwargs)

    def set_verified(self):
        try:
            self.verified = True
            self.active_verification_token.invalidate()
        except AttributeError:
            pass


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
