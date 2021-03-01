import datetime
from http import HTTPStatus

import pytest
from pyramid.httpexceptions import HTTPBadRequest

from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.lib.security.auth import AuthWithRecoveryTokenManager
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.recovery_token import (
    get_recovery_token_by_id, RecoveryToken)


def test_login_success(dummy_request, dummy_user):
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

    AuthWithRecoveryTokenManager(dummy_request).login(data)

    updated_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert dummy_request.response.status_code == HTTPStatus.OK
    assert 'auth_tkt' in dummy_request.response.headers['Set-Cookie']
    assert updated_recovery_token.used


def test_login_user_not_found(dummy_request):
    data = {
        'email_address': '{{cookiecutter.alternative_test_email_address}}',
        'token': '123456'
    }
    auth_manager = AuthWithRecoveryTokenManager(dummy_request)

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login(data)

    assert bad_request.value.json == {
        'message': {
            'token': [auth_manager.invalid_credentials_error]
        }
    }


def test_login_token_incorrect(dummy_request, dummy_user):
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
    auth_manager = AuthWithRecoveryTokenManager(dummy_request)

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login(data)

    unaltered_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert not unaltered_recovery_token.used
    assert bad_request.value.json == {
        'message': {
            'token': [auth_manager.invalid_credentials_error]
        }
    }


def test_login_token_expired(dummy_request, dummy_user):
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
    auth_manager = AuthWithRecoveryTokenManager(dummy_request)

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login(data)

    unaltered_recovery_token = get_recovery_token_by_id(recovery_token_id)
    assert not unaltered_recovery_token.used
    assert bad_request.value.json == {
        'message': {
            'token': [auth_manager.invalid_credentials_error]
        }
    }


def test_locked_after_too_many_attempts(dummy_request):
    data = {'email_address': '{{cookiecutter.test_email_address}}', 'token': 'wrong1'}
    auth_manager = AuthWithRecoveryTokenManager(dummy_request)

    for _ in range(0, 3):
        try:
            auth_manager.login(data)
        except HTTPBadRequest:
            pass

    with pytest.raises(HTTPBadRequest) as bad_request:
        auth_manager.login(data)

    assert "This account is locked" in bad_request.value.json.get('message')


def test_logout_success(dummy_request, dummy_user):
    user, user_id = save(dummy_user)
    token = '123456'
    token_hash, token_salt = hash_plaintext(token)
    recovery_token = RecoveryToken(
        for_user_id=user_id,
        token_hash=token_hash,
        token_salt=token_salt
    )
    _, recovery_token_id = save(recovery_token)

    auth_manager = AuthWithRecoveryTokenManager(dummy_request)
    auth_manager.login({
        'email_address': user.email_address,
        'token': token
    })

    auth_manager.logout()

    assert 'auth_tkt=;' in dummy_request.response.headers['Set-Cookie']
