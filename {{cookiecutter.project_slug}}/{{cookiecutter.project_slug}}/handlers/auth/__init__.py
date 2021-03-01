from pyramid.view import view_defaults

from {{cookiecutter.project_slug}}.handlers import Handler, view_config
from {{cookiecutter.project_slug}}.lib.decorators import validate
from {{cookiecutter.project_slug}}.lib.factories.auth import AuthFactory
from {{cookiecutter.project_slug}}.lib.schemas.auth import LoginSchema
from {{cookiecutter.project_slug}}.lib.security.auth import AuthManager, AuthWithPasswordManager


class LoginHandler(Handler):
    auth_manager: AuthManager


@view_defaults(containment=AuthFactory, context=AuthFactory, renderer='json')
class AuthHandler(LoginHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_manager = AuthWithPasswordManager(self.request)

    @validate(LoginSchema())
    @view_config(
        path_hints=['/auth/login'],
        request_schema_class=LoginSchema,
        successful_response_code=200,
        permission='auth.login',
        request_method='POST',
        tags='authentication',
        name='login',
        public_hint=True
    )
    def login(self, login_data):
        return self.auth_manager.login(login_data)

    @view_config(
        path_hints=['/auth/logout'],
        successful_response_code=200,
        permission='auth.logout',
        request_method='POST',
        tags='authentication',
        name='logout'
    )
    def logout(self):
        return self.auth_manager.logout()
