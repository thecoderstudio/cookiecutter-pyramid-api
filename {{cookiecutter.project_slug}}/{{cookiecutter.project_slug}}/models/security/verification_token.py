import datetime

from sqlalchemy import Column, DateTime

from {{cookiecutter.project_slug}}.models import Base, session
from {{cookiecutter.project_slug}}.models.functions import utcnow
from {{cookiecutter.project_slug}}.models.security.secure_token import SecureUserTokenMixin

NUMBER_OF_HOURS_VALID = 24


class VerificationToken(Base, SecureUserTokenMixin):
    __tablename__ = 'verification_token'

    expires_on = Column(
        DateTime,
        default=utcnow() + datetime.timedelta(
            hours=NUMBER_OF_HOURS_VALID
        ),
        nullable=False
    )


def get_verification_token_by_id(id_):
    return session.query(VerificationToken).get(id_)
