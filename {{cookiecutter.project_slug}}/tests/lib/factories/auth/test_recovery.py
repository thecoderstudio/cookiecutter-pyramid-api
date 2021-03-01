from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories.auth.recovery import AccountRecoveryFactory


def test_acl(dummy_request):
    factory = AccountRecoveryFactory(dummy_request)

    assert factory.__acl__() == (
        (Allow, Everyone, 'recovery.request_token'),
        (Allow, Everyone, 'recovery.login')
    )
