import random
import time
from secrets import token_hex

from pyramid.httpexceptions import HTTPCreated
from pyramid.view import view_defaults
from sqlalchemy.orm.exc import NoResultFound

from {{cookiecutter.project_slug}}.handlers import view_config
from {{cookiecutter.project_slug}}.handlers.auth import LoginHandler
from {{cookiecutter.project_slug}}.lib.decorators import validate
from {{cookiecutter.project_slug}}.lib.factories.auth.recovery import AccountRecoveryFactory
from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.lib.middleware.sendgrid import SendGridClient
from {{cookiecutter.project_slug}}.lib.schemas.auth import (AccountRecoveryLoginSchema,
                                     AccountRecoverySchema)
from {{cookiecutter.project_slug}}.lib.security.auth import AuthWithRecoveryTokenManager
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.recovery_token import RecoveryToken
from {{cookiecutter.project_slug}}.models.user import get_one_user_by_email_address, User

NUMBER_OF_TOKEN_BYTES = 3
TOKEN_TTL_IN_SECONDS = 7200

MIN_TIME_PADDING_IN_DECISECONDS = 2
MAX_TIME_PADDING_IN_DECISECONDS = 8


@view_defaults(
    containment=AccountRecoveryFactory,
    context=AccountRecoveryFactory,
    renderer='json'
)
class AccountRecoveryHandler(LoginHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_manager = AuthWithRecoveryTokenManager(self.request)

    @validate(AccountRecoverySchema())
    @view_config(
        path_hints=['/auth/recover-account'],
        request_schema_class=AccountRecoverySchema,
        permission='recovery.request_token',
        tags=['authentication', 'account recovery'],
        request_method='POST',
        public_hint=True
    )
    def request_account_recovery_token(self, request_data):
        response = HTTPCreated()
        token = token_hex(NUMBER_OF_TOKEN_BYTES)
        email_address = request_data['email_address']
        self._prevent_user_enumeration()

        try:
            recipient = get_one_user_by_email_address(email_address)
            self._invalidate_any_current_recovery_token(recipient)
            self._save_recovery_token(recipient, token)
            SendGridClient().send_account_recovery_email(email_address, token)
        except NoResultFound:
            # To avoid user enumeration we don't indicate failure.
            pass

        raise response

    @staticmethod
    def _prevent_user_enumeration():
        time.sleep(random.randint(
            MIN_TIME_PADDING_IN_DECISECONDS,
            MAX_TIME_PADDING_IN_DECISECONDS
        ) / 10)

    @staticmethod
    def _invalidate_any_current_recovery_token(user):
        try:
            user.active_recovery_token.invalidate()
        except AttributeError:
            pass

    @staticmethod
    def _save_recovery_token(for_user: User, token: str):
        token_hash, token_salt = hash_plaintext(token)
        recovery_token = RecoveryToken(
            token_hash=token_hash,
            token_salt=token_salt,
            for_user=for_user
        )
        save(recovery_token)

    @validate(AccountRecoveryLoginSchema())
    @view_config(
        path_hints=['/auth/recover-account/login'],
        request_schema_class=AccountRecoveryLoginSchema,
        permission='recovery.login',
        request_method='POST',
        successful_response_code=200,
        tags=['authentication', 'account recovery'],
        name='login',
        public_hint=True
    )
    def login(self, login_data):
        self.auth_manager.login(login_data)
        raise self.request.response
