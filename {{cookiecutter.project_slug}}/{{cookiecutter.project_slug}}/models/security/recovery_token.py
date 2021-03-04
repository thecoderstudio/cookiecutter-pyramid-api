from {{cookiecutter.project_slug}}.models import Base, session
from {{cookiecutter.project_slug}}.models.security.secure_token import SecureUserTokenMixin


class RecoveryToken(Base, SecureUserTokenMixin):
    __tablename__ = 'recovery_token'


def get_recovery_token_by_id(id_):
    return session.query(RecoveryToken).get(id_)
