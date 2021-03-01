import pytest
from marshmallow import ValidationError

from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext
from {{cookiecutter.project_slug}}.lib.schemas.user import (CreateUserSchema, UpdateUserSchema,
                                     UserSchema)
from {{cookiecutter.project_slug}}.models import save
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
        'email_address': dummy_user.email_address
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
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'newpassword'
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
