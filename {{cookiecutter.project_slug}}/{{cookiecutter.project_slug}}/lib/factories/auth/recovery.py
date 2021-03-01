from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories import BaseFactory


class AccountRecoveryFactory(BaseFactory):
    def __acl__(self):
        return (
            (Allow, Everyone, 'recovery.request_token'),
            (Allow, Everyone, 'recovery.login')
        )
