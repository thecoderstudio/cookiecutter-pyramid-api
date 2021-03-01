from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request
from pyramid.security import forget, remember

from {{cookiecutter.project_slug}}.lib.hash import compare_plaintext_to_hash
from {{cookiecutter.project_slug}}.lib.security.shield import RequestShield
from {{cookiecutter.project_slug}}.lib.settings import settings
from {{cookiecutter.project_slug}}.models.user import get_user_by_email_address, User

FAKE_HASH = "$2b$12$TEfhqmu/6mXaYqMZUkTAZuP51uAJH2qN0lPenzFtwnvcSWPKsCFyS"
FAKE_SALT = "$2b$12$TEfhqmu/6mXaYqMZUkTAZu"


class AuthManager:
    secret_key_name: str

    @property
    def invalid_credentials_error(self):
        return f"Email address or {self.secret_key_name} incorrect"

    def __init__(self, request: Request):
        security_settings = settings['security']
        self.shield_args = {
            'max_attempts': int(security_settings['max_login_attempts']),
            'lockout_interval_in_seconds': int(
                security_settings['login_lockout_interval_in_seconds']
            ),
            'max_lockout_time_in_seconds': int(
                security_settings['max_login_lockout_in_seconds']
            )
        }
        self.request = request

    def login(self, login_data: dict):
        shield = RequestShield(
            login_data['email_address'],
            **self.shield_args
        )
        shield.raise_if_locked(resource='account')
        shield.increment_attempts()

        user = get_user_by_email_address(login_data['email_address'])
        self._validate_credentials(login_data, user)

        shield.clear()
        headers = remember(self.request, str(user.id))
        self.request.response.headerlist.extend(headers)

    def _validate_credentials(self, login_data: dict, user: User):
        if not self._check_credentials(login_data, user):
            raise HTTPBadRequest(json={
                'message': {
                    self.secret_key_name: [self.invalid_credentials_error]
                }
            })

    def _check_credentials(self, login_data: dict, user: User):
        try:
            hash_, salt = self._get_hash_and_salt_from_user(user)
        except AttributeError:
            hash_, salt = FAKE_HASH, FAKE_SALT

        return compare_plaintext_to_hash(
            login_data[self.secret_key_name],
            hash_,
            salt
        )

    def _get_hash_and_salt_from_user(self, user: User = None):
        """Gets the hash and salt from the user to compare credentials.

        Raises an AttributeError when the hash or salt is not found.
        """
        raise NotImplementedError

    def logout(self):
        headers = forget(self.request)
        self.request.response.headerlist.extend(headers)
