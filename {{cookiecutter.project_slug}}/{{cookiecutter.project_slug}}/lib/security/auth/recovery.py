from {{cookiecutter.project_slug}}.lib.security.auth.manager import AuthManager
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.user import get_user_by_email_address, User


class AuthWithRecoveryTokenManager(AuthManager):
    secret_key_name = 'token'

    @property
    def invalid_credentials_error(self):
        return f"Email address or {self.secret_key_name} incorrect or expired"

    def login(self, login_data: dict):
        response = super().login(login_data)

        recovery_token = get_user_by_email_address(
            login_data['email_address']
        ).active_recovery_token
        recovery_token.used = True
        save(recovery_token)

        return response

    def _get_hash_and_salt_from_user(self, user: User = None):
        return (
            user.active_recovery_token.token_hash,
            user.active_recovery_token.token_salt
        )
