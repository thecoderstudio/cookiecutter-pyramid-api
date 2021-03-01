from http import HTTPStatus

import pytest
from pyramid.httpexceptions import HTTPBadRequest

from {{cookiecutter.project_slug}}.lib.security.auth import AuthWithPasswordManager
from {{cookiecutter.project_slug}}.models import save


def test_login_success(dummy_request, dummy_user):
    user, _ = save(dummy_user)

    AuthWithPasswordManager(dummy_request).login({
        'email_address': user.email_address,
        'password': 'testing123'
    })

    assert dummy_request.response.status_code == HTTPStatus.OK
    assert 'auth_tkt' in dummy_request.response.headers['Set-Cookie']


@pytest.mark.parametrize("email_address, password", [
    ['{{cookiecutter.test_email_address}}', 'wrongpassword1'],
    ['{{cookiecutter.alternative_test_email_address}}', 'testing123']
])
def test_login_wrong_credentials(dummy_request, dummy_user, email_address,
                                 password):
    user, _ = save(dummy_user)
    auth_manager = AuthWithPasswordManager(dummy_request)

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login({
            'email_address': email_address,
            'password': password
        })

    assert bad_request.value.json == {
        'message': {
            'password': ["Email address or password incorrect"]
        }
    }


def test_locked_after_too_many_attempts(dummy_request):
    data = {'email_address': '{{cookiecutter.test_email_address}}', 'password': 'fake123'}
    auth_manager = AuthWithPasswordManager(dummy_request)

    for _ in range(0, 3):
        try:
            auth_manager.login(data)
        except HTTPBadRequest:
            pass

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login(data)

    assert "This account is locked" in bad_request.value.json.get('message')


def test_logout_success(dummy_request, dummy_user):
    user, _ = save(dummy_user)
    auth_manager = AuthWithPasswordManager(dummy_request)
    auth_manager.login({
        'email_address': user.email_address,
        'password': 'testing123'
    })

    auth_manager.logout()

    assert 'auth_tkt=;' in dummy_request.response.headers['Set-Cookie']
