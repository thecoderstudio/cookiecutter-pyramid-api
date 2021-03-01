import pytest
from marshmallow import ValidationError

from {{cookiecutter.project_slug}}.lib.schemas.auth import LoginSchema
from tests.lib.schemas import REQUIRED_ERROR


def test_load_login_success():
    data = {
        'email_address': '{{cookiecutter.test_email_address}}',
        'password': 'testing123'
    }

    credentials = LoginSchema().load(data)

    assert credentials['email_address'] == data['email_address']
    assert credentials['password'] == data['password']


def test_load_login_missing_fields():
    with pytest.raises(ValidationError) as validation_error:
        LoginSchema().load({})

    assert validation_error.value.messages == {
        'email_address': [REQUIRED_ERROR],
        'password': [REQUIRED_ERROR]
    }
