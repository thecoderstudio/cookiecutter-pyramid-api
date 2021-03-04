from secrets import token_hex

from pyramid.httpexceptions import HTTPCreated
from pyramid.view import view_defaults

from {{cookiecutter.project_slug}}.handlers import Handler, view_config
from {{cookiecutter.project_slug}}.lib.decorators import validate as validate_decorator
from {{cookiecutter.project_slug}}.lib.factories.user import UserFactory
from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.lib.middleware.sendgrid import SendGridClient
from {{cookiecutter.project_slug}}.lib.schemas import validate
from {{cookiecutter.project_slug}}.lib.schemas.user import (CreateUserSchema, UpdateUserSchema,
                                     UserSchema, VerifyUserSchema)
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.verification_token import VerificationToken
from {{cookiecutter.project_slug}}.models.user import User

NUMBER_OF_TOKEN_BYTES = 3


@view_defaults(containment=UserFactory, context=UserFactory, renderer='json')
class UserHandler(Handler):
    @validate_decorator(CreateUserSchema())
    @view_config(
        request_schema_class=CreateUserSchema,
        path_hints=['/user'],
        permission='user.post',
        request_method='POST',
        tags='user'
    )
    def post(self, user):
        user.active_verification_token = self._send_verification_token(user)
        _, id_ = save(user)
        response = HTTPCreated()
        response.location = f"{self.request.url}/{id_}"
        raise response

    def _send_verification_token(self, recipient):
        token = token_hex(NUMBER_OF_TOKEN_BYTES)
        token_hash, token_salt = hash_plaintext(token)
        verification_token = VerificationToken(
            token_hash=token_hash,
            token_salt=token_salt,
            for_user=recipient
        )
        SendGridClient().send_account_verification_email(
            recipient.email_address,
            token
        )
        return verification_token

    @view_config(
        request_schema_class=UpdateUserSchema,
        path_hints=['/user/me'],
        permission='user.patch',
        request_method='PATCH',
        tags='user',
        context=User
    )
    def patch(self):
        user = self.request.context
        password_reset_allowed = self.request.has_permission(
                'user.reset_password'
        )

        schema = UpdateUserSchema(
            user,
            requires_current_password=not password_reset_allowed,
            partial=True,
            exclude=('email_address', )
        )

        user_data = validate(self.request.json_body, schema)
        if not user_data:
            return

        user.set_fields(**user_data)

        if password_reset_allowed and user_data.get('password_hash'):
            user.active_recovery_token.invalidate()

        save(user)

    @view_config(
        response_schema_class=UserSchema,
        path_hints=['/user/me'],
        permission='user.get',
        request_method='GET',
        tags='user',
        context=User
    )
    def get(self):
        return UserSchema().dump(self.context)

    @view_config(
        path_hints=['/user/me/request-verification-token'],
        permission='user.request_verification_token',
        request_schema_class=VerifyUserSchema,
        request_method='POST',
        tags='user',
        context=User,
        name='request-verification-token'
    )
    def request_verification_token(self):
        validate({}, VerifyUserSchema(self.context))
        self._invalidate_any_current_verification_token(self.context)

        self.context.active_verification_token = self._send_verification_token(
            self.context)
        save(self.context)

    @staticmethod
    def _invalidate_any_current_verification_token(user):
        try:
            user.active_verification_token.invalidate()
        except AttributeError:
            pass
