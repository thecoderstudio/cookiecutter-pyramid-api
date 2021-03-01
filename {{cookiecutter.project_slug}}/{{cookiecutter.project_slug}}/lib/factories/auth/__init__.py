from pyramid.security import Allow, Authenticated, Everyone

from {{cookiecutter.project_slug}}.lib.factories import BaseFactory
from {{cookiecutter.project_slug}}.lib.factories.auth.recovery import AccountRecoveryFactory


class AuthFactory(BaseFactory):
    def __init__(self, request, parent):
        super().__init__(request, parent)
        self['recover-account'] = AccountRecoveryFactory(request, self)

    def __acl__(self):
        return (
            (Allow, Everyone, 'auth.login'),
            (Allow, Authenticated, 'auth.logout'),
            (Allow, Everyone, 'auth.recover_account')
        )
