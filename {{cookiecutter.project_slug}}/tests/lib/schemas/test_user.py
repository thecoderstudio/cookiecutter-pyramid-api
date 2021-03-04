import pytest
from marshmallow import ValidationError

from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.lib.schemas.user import (CreateUserSchema, UpdateUserSchema,
                                     UserSchema, VerifyUserSchema)
from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.verification_token import VerificationToken
from tests.lib.schemas import REQUIRED_ERROR


def test_invalid_password_length():
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing'
    }

    with pytest.raises(ValidationError) as validation_error:
        UserSchema().load(data)

    assert validation_error.value.messages == {
        'password': ["Shorter than minimum length 8."]
    }


def test_load_user_email_already_exists(dummy_user):
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing123'
    }
    save(dummy_user)

    with pytest.raises(ValidationError) as validation_error:
        UserSchema().load(data)

    assert validation_error.value.messages == {
        'email_address': ['A user with this email address already exists.']
    }


def test_dump_user(dummy_user):
    data = UserSchema().dump(dummy_user)

    assert data == {
        'id': str(dummy_user.id),
        'email_address': dummy_user.email_address,
        'verified': False
    }


def test_load_create_user_success():
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing123'
    }

    user = CreateUserSchema().load(data)
    expected_hash, _ = hash_plaintext(data['password'],
                                      user.password_salt.encode('utf-8'))

    assert user.email_address == data['email_address']
    assert user.password_hash == expected_hash


def test_load_create_user_missing_fields():
    with pytest.raises(ValidationError) as validation_error:
        CreateUserSchema().load({})

    assert validation_error.value.messages == {
        'email_address': [REQUIRED_ERROR],
        'password': [REQUIRED_ERROR]
    }


@pytest.mark.parametrize('requires_current_password', (True, False))
def test_load_update_user_success(dummy_user, requires_current_password):
    token = '123456'
    token_hash, token_salt = hash_plaintext(token)
    verification_token = VerificationToken(
        token_hash=token_hash,
        token_salt=token_salt,
        for_user=dummy_user
    )
    dummy_user.active_verification_token = verification_token

    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'newpassword',
        'verification_token': token
    }

    if requires_current_password:
        data['current_password'] = 'testing123'

    user_data = UpdateUserSchema(
        user=dummy_user,
        requires_current_password=requires_current_password
    ).load(data)

    expected_hash, _ = hash_plaintext(
        data['password'],
        user_data['password_salt'].encode('utf-8')
    )

    assert user_data['email_address'] == data['email_address']
    assert user_data['password_hash'] == expected_hash
    assert user_data['verified']
    assert verification_token.used


def test_load_update_user_missing_fields(dummy_user):
    with pytest.raises(ValidationError) as validation_error:
        UpdateUserSchema(
            user=dummy_user,
            requires_current_password=False
        ).load({})

    assert validation_error.value.messages == {
        'email_address': [REQUIRED_ERROR],
        'password': [REQUIRED_ERROR]
    }


def test_load_update_user_current_password_required(dummy_user):
    with pytest.raises(ValidationError) as validation_error:
        UpdateUserSchema(user=dummy_user).load({
            'email_address': '{{cookiecutter.test_email_address}}',
            'password': 'newpassword'
        })

    assert validation_error.value.messages == {
        'current_password': [
            "This field is required when setting a new password"
        ]
    }


def test_load_update_user_incorrect_current_password(dummy_user):
    with pytest.raises(ValidationError) as validation_error:
        UpdateUserSchema(user=dummy_user).load({
            'email_address': '{{cookiecutter.test_email_address}}',
            'password': 'newpassword',
            'current_password': 'wrongpassword'
        })

    assert validation_error.value.messages == {
        'current_password': [
            "Given password is incorrect"
        ]
    }


def test_load_update_user_already_verified(dummy_user):
    dummy_user.verified = True

    data = {
        'verification_token': '123456'
    }

    with pytest.raises(ValidationError) as validation_error:
        UpdateUserSchema(user=dummy_user, partial=True).load(data)

    assert validation_error.value.messages == {
        'verification_token': ["This user is already verified."]
    }


def test_load_update_user_invalid_verification_token(dummy_user):
    data = {
        'verification_token': '123456'
    }

    with pytest.raises(ValidationError) as validation_error:
        UpdateUserSchema(user=dummy_user, partial=True).load(data)

    assert validation_error.value.messages == {
        'verification_token': ["The given token is incorrect or expired."]
    }


def test_load_verify_user_schema_success(dummy_user):
    result_data = VerifyUserSchema(user=dummy_user).load({})
    assert not result_data


def test_load_verify_user_already_verified(dummy_user):
    dummy_user.verified = True

    with pytest.raises(ValidationError) as validation_error:
        VerifyUserSchema(user=dummy_user, partial=True).load({})

    assert validation_error.value.messages == {
        '_schema': ["This user is already verified."]
    }
