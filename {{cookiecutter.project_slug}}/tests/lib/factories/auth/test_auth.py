from pyramid.security import Allow, Authenticated, Everyone

from {{cookiecutter.project_slug}}.lib.factories.auth import AuthFactory
from {{cookiecutter.project_slug}}.lib.factories.root import RootFactory


def test_acl(dummy_request):
    factory = AuthFactory(dummy_request, RootFactory(dummy_request))
    assert factory.__acl__() == (
        (Allow, Everyone, 'auth.login'),
        (Allow, Authenticated, 'auth.logout'),
        (Allow, Everyone, 'auth.recover_account')
    )


def test_get_recovery_factory(dummy_request):
    factory = AuthFactory(dummy_request, RootFactory(dummy_request))

    recovery_factory = factory['recover-account']

    assert recovery_factory.__parent__ == factory
    assert recovery_factory.request == dummy_request
