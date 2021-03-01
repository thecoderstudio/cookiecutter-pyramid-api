from http import HTTPStatus

import pytest

from {{cookiecutter.project_slug}}.models import save
from tests.lib.schemas import REQUIRED_ERROR


def test_login_success(test_app, dummy_user):
    user, _ = save(dummy_user)

    response = test_app.post_json('/auth/login', {
        'email_address': user.email_address,
        'password': 'testing123'
    })

    assert response.status_code == HTTPStatus.OK
    assert 'auth_tkt' in response.headers['Set-Cookie']


def test_login_missing_fields(test_app):
    response = test_app.post_json('/auth/login', {}, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'email_address': [REQUIRED_ERROR],
            'password': [REQUIRED_ERROR]
        }
    }


@pytest.mark.parametrize("email_address, password", [
    ['{{cookiecutter.test_email_address}}', 'wrongpassword1'],
    ['{{cookiecutter.alternative_test_email_address}}', 'testing123']
])
def test_login_wrong_credentials(test_app, dummy_user, email_address,
                                 password):
    user, _ = save(dummy_user)

    response = test_app.post_json(
        '/auth/login',
        {
            'email_address': email_address,
            'password': password
        },
        expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'password': ["Email address or password incorrect"]
        }
    }


def test_locked_after_too_many_attempts(test_app):
    data = {'email_address': '{{cookiecutter.test_email_address}}', 'password': 'fake123'}
    test_app.post_json('/auth/login', data, expect_errors=True)
    test_app.post_json('/auth/login', data, expect_errors=True)
    test_app.post_json('/auth/login', data, expect_errors=True)
    response = test_app.post_json('/auth/login', data, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "This account is locked" in response.json.get('message')


def test_logout_success(test_app_with_authenticated_user_id):
    test_app, _ = test_app_with_authenticated_user_id

    response = test_app.post('/auth/logout')

    assert response.status_code == HTTPStatus.OK
    assert 'auth_tkt=;' in response.headers['Set-Cookie']


def test_logout_forbidden(test_app):
    response = test_app.post('/auth/logout', expect_errors=True)

    assert response.status_code == HTTPStatus.FORBIDDEN
