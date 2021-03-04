from http import HTTPStatus

from {{cookiecutter.project_slug}}.lib.hash import compare_plaintext_to_hash, hash_plaintext
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.recovery_token import RecoveryToken
from {{cookiecutter.project_slug}}.models.security.verification_token import (
    get_verification_token_by_id, VerificationToken)
from {{cookiecutter.project_slug}}.models.user import get_user_by_email_address, get_user_by_id
from tests.lib.schemas import REQUIRED_ERROR


def test_post_success(test_app, mocker):
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing123'
    }
    token_hex_mock = mocker.patch(
        '{{cookiecutter.project_slug}}.handlers.user.token_hex',
        return_value='123456'
    )
    sendgrid_mock = mocker.MagicMock()
    mocker.patch('{{cookiecutter.project_slug}}.handlers.user.SendGridClient',
                 return_value=sendgrid_mock)

    response = test_app.post_json('/user', data)

    created_user_id = get_user_by_email_address(data['email_address']).id
    assert response.location == f"http://localhost/user/{created_user_id}"
    assert response.status_code == HTTPStatus.CREATED
    sendgrid_mock.send_account_verification_email.assert_called_with(
        data['email_address'],
        token_hex_mock()
    )


def test_post_user_missing_fields(test_app):
    response = test_app.post_json('/user', {}, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'email_address': [REQUIRED_ERROR],
            'password': [REQUIRED_ERROR]
        }
    }


def test_post_user_invalid_password_length(test_app):
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing'
    }

    response = test_app.post_json('/user', data, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'password': ["Shorter than minimum length 8."]
        }
    }


def test_post_user_email_already_exists(test_app, dummy_user):
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing123'
    }
    save(dummy_user)

    response = test_app.post_json('/user', data, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'email_address': ['A user with this email address already exists.']
        }
    }


def test_patch_user_success(test_app_with_authenticated_user_id):
    test_app, user_id = test_app_with_authenticated_user_id
    token = '123456'
    token_hash, token_salt = hash_plaintext(token)
    verification_token = VerificationToken(
        token_hash=token_hash,
        token_salt=token_salt,
        for_user_id=user_id
    )
    _, token_id = save(verification_token)

    data = {
        'password': 'newpassword',
        'current_password': 'testing123',
        'verification_token': token
    }

    response = test_app.patch_json('/user/me', data)

    updated_user = get_user_by_id(user_id)
    updated_verification_token = get_verification_token_by_id(token_id)
    assert response.status_code == HTTPStatus.OK
    assert not compare_plaintext_to_hash(
        'testing123',
        updated_user.password_hash,
        updated_user.password_salt
    )
    assert updated_user.verified
    assert updated_verification_token.invalidated
    assert updated_verification_token.used


def test_patch_user_empty(test_app_with_authenticated_user_id):
    test_app, user_id = test_app_with_authenticated_user_id

    response = test_app.patch_json('/user/me', {})

    unaltered_user = get_user_by_id(user_id)
    assert response.status_code == HTTPStatus.OK
    assert compare_plaintext_to_hash(
        'testing123',
        unaltered_user.password_hash,
        unaltered_user.password_salt
    )


def test_patch_user_invalid_password_length(
    test_app_with_authenticated_user_id
):
    test_app, user_id = test_app_with_authenticated_user_id

    data = {
        'password': 'new',
        'current_password': 'testing123'
    }

    response = test_app.patch_json('/user/me', data, expect_errors=True)

    updated_user = get_user_by_id(user_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'password': ["Shorter than minimum length 8."]
        }
    }
    assert compare_plaintext_to_hash(
        'testing123',
        updated_user.password_hash,
        updated_user.password_salt
    )


def test_patch_user_current_password_required(
    test_app_with_authenticated_user_id
):
    test_app, user_id = test_app_with_authenticated_user_id

    data = {
        'password': 'newpassword'
    }

    response = test_app.patch_json('/user/me', data, expect_errors=True)

    updated_user = get_user_by_id(user_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'current_password': [
                "This field is required when setting a new password"
            ]
        }
    }
    assert compare_plaintext_to_hash(
        'testing123',
        updated_user.password_hash,
        updated_user.password_salt
    )


def test_patch_user_current_password_incorrect(
    test_app_with_authenticated_user_id
):
    test_app, user_id = test_app_with_authenticated_user_id

    data = {
        'password': 'newpassword',
        'current_password': 'wrongpassword'
    }

    response = test_app.patch_json('/user/me', data, expect_errors=True)

    updated_user = get_user_by_id(user_id)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'current_password': [
                "Given password is incorrect"
            ]
        }
    }
    assert compare_plaintext_to_hash(
        'testing123',
        updated_user.password_hash,
        updated_user.password_salt
    )


def test_patch_user_reset_password(test_app_with_authenticated_user_id):
    test_app, user_id = test_app_with_authenticated_user_id

    recovery_token = RecoveryToken(
        for_user_id=user_id,
        token_hash='fake',
        token_salt='fake',
        used=True
    )
    save(recovery_token)

    data = {
        'password': 'newpassword'
    }

    response = test_app.patch_json('/user/me', data)

    updated_user = get_user_by_id(user_id)
    assert response.status_code == HTTPStatus.OK
    assert updated_user.active_recovery_token is None
    assert not compare_plaintext_to_hash(
        'testing123',
        updated_user.password_hash,
        updated_user.password_salt
    )


def test_patch_user_already_verified(test_app_with_authenticated_user_id):
    test_app, user_id = test_app_with_authenticated_user_id
    user = get_user_by_id(user_id)
    user.verified = True
    save(user)

    data = {
        'verification_token': '123456'
    }

    response = test_app.patch_json('/user/me', data, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'verification_token': ["This user is already verified."]
        }
    }


def test_patch_user_invalid_verification_token(
    test_app_with_authenticated_user_id
):
    test_app, user_id = test_app_with_authenticated_user_id
    data = {
        'verification_token': '123456'
    }

    response = test_app.patch_json('/user/me', data, expect_errors=True)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            'verification_token': ["The given token is incorrect or expired."]
        }
    }


def test_patch_user_unauthenticated(test_app):
    response = test_app.patch_json('/user/me', {}, expect_errors=True)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_user(test_app_with_authenticated_user_id):
    test_app, user_id = test_app_with_authenticated_user_id
    user = get_user_by_id(user_id)

    response = test_app.get('/user/me', expect_errors=True)

    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        'id': str(user_id),
        'email_address': user.email_address,
        'verified': False
    }


def test_get_user_unauthenticated(test_app):
    response = test_app.get('/user/me', expect_errors=True)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_request_verification_token_success(
    test_app_with_authenticated_user_id,
    mocker
):
    test_app, user_id = test_app_with_authenticated_user_id
    email_address = get_user_by_id(user_id).email_address
    token_hex_mock = mocker.patch(
        '{{cookiecutter.project_slug}}.handlers.user.token_hex',
        return_value='123456'
    )
    sendgrid_mock = mocker.MagicMock()
    mocker.patch('{{cookiecutter.project_slug}}.handlers.user.SendGridClient',
                 return_value=sendgrid_mock)

    response = test_app.post_json(
        '/user/me/request-verification-token',
        {},
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.OK
    sendgrid_mock.send_account_verification_email.assert_called_with(
        email_address,
        token_hex_mock()
    )


def test_request_verification_token_already_verified(
    test_app_with_authenticated_user_id
):
    test_app, user_id = test_app_with_authenticated_user_id
    user = get_user_by_id(user_id)
    user.verified = True
    save(user)

    response = test_app.post_json(
        '/user/me/request-verification-token',
        {},
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {
        'message': {
            '_schema': ["This user is already verified."]
        }
    }


def test_request_verification_token_unauthenticated(test_app):
    response = test_app.post_json(
        '/user/me/request-verification-token',
        {},
        expect_errors=True
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
