import datetime
from http import HTTPStatus

from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.recovery_token import (
    get_recovery_token_by_id, RecoveryToken)
from tests.lib.schemas import REQUIRED_ERROR

INVALID_CREDENTIALS_ERROR = "Email address or token incorrect or expired"


def test_request_account_recovery_token_success(mocker, test_app, dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    data = {
        'email_address': email_address
    }

    token_hex_mock = mocker.patch(
        '{{cookiecutter.project_slug}}.handlers.auth.recovery.token_hex',
        return_value='123456'
    )

    sendgrid_mock = mocker.MagicMock()
    mocker.patch('{{cookiecutter.project_slug}}.handlers.auth.recovery.SendGridClient',
                 return_value=sendgrid_mock)

    response = test_app.post_json('/auth/recover-account', data)

    assert response.status_code == HTTPStatus.CREATED
    sendgrid_mock.send_account_recovery_email.assert_called_with(
        email_address,
        token_hex_mock()
    )


def test_request_account_recovery_token_user_not_found(mocker, test_app):
    sendgrid_mock = mocker.patch(
        '{{cookiecutter.project_slug}}.handlers.auth.recovery.SendGridClient',
        autospec=True
    )

    data = {
        'email_address': '{{cookiecutter.alternative_test_email_address}}'
    }

    response = test_app.post_json('/auth/recover-account', data)

    assert response.status_code == HTTPStatus.CREATED
    sendgrid_mock.send_account_recovery_email.assert_not_called()


def test_request_account_recovery_token_missing_fields(test_app):
    response = test_app.post_json(
        '/auth/recover-account',
        {},
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'email_address': [REQUIRED_ERROR]
        }
    }


def test_login_success(test_app, dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    token = '123456'
    token_hash, token_salt = hash_plaintext(token)
    recovery_token = RecoveryToken(
        for_user_id=user_id,
        token_hash=token_hash,
        token_salt=token_salt
    )
    _, recovery_token_id = save(recovery_token)

    data = {
        'email_address': email_address,
        'token': token
    }

    response = test_app.post_json('/auth/recover-account/login', data)

    updated_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert response.status_code == HTTPStatus.OK
    assert 'auth_tkt' in response.headers['Set-Cookie']
    assert updated_recovery_token.used


def test_login_missing_fields(test_app):
    response = test_app.post_json(
        '/auth/recover-account/login',
        {},
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'email_address': [REQUIRED_ERROR],
            'token': [REQUIRED_ERROR]
        }
    }


def test_login_user_not_found(test_app):
    data = {
        'email_address': '{{cookiecutter.alternative_test_email_address}}',
        'token': '123456'
    }

    response = test_app.post_json('/auth/recover-account/login', data,
                                  expect_errors=True)
    assert not response.headers.get('Set-Cookie')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'token': [INVALID_CREDENTIALS_ERROR]
        }
    }


def test_login_token_incorrect(test_app, dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    token_hash, token_salt = hash_plaintext('123456')
    recovery_token = RecoveryToken(
        for_user_id=user_id,
        token_hash=token_hash,
        token_salt=token_salt
    )
    _, recovery_token_id = save(recovery_token)

    data = {
        'email_address': email_address,
        'token': 'wrong1'
    }

    response = test_app.post_json('/auth/recover-account/login', data,
                                  expect_errors=True)

    unaltered_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert not response.headers.get('Set-Cookie')
    assert not unaltered_recovery_token.used
    assert response.json == {
        'message': {
            'token': [INVALID_CREDENTIALS_ERROR]
        }
    }


def test_login_token_expired(test_app, dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    token = '123456'
    token_hash, token_salt = hash_plaintext(token)
    recovery_token = RecoveryToken(
        for_user_id=user_id,
        token_hash=token_hash,
        token_salt=token_salt,
        expires_on=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    )
    _, recovery_token_id = save(recovery_token)

    data = {
        'email_address': email_address,
        'token': token
    }

    response = test_app.post_json('/auth/recover-account/login', data,
                                  expect_errors=True)

    unaltered_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert not response.headers.get('Set-Cookie')
    assert not unaltered_recovery_token.used
    assert response.json == {
        'message': {
            'token': [INVALID_CREDENTIALS_ERROR]
        }
    }


def test_locked_after_too_many_attempts(test_app):
    data = {'email_address': '{{cookiecutter.test_email_address}}', 'token': 'wrong1'}
    for _ in range(0, 3):
        test_app.post_json(
            '/auth/recover-account/login',
            data,
            expect_errors=True
        )

    response = test_app.post_json(
        '/auth/recover-account/login',
        data,
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "This account is locked" in response.json.get('message')
