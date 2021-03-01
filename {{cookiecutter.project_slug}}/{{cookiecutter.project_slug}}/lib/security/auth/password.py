from {{cookiecutter.project_slug}}.lib.security.auth.manager import AuthManager
from {{cookiecutter.project_slug}}.models.user import User


class AuthWithPasswordManager(AuthManager):
    secret_key_name = 'password'

    def _get_hash_and_salt_from_user(self, user: User = None):
        return (user.password_hash, user.password_salt)
