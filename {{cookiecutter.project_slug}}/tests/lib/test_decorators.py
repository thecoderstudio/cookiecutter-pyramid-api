import pytest
from marshmallow import fields, Schema
from pyramid.httpexceptions import HTTPBadRequest

from {{cookiecutter.project_slug}}.lib.decorators import validate


class SampleSchema(Schema):
    test = fields.Str(required=True)


class Fake:
    def __init__(self, request):
        self.request = request

    @validate(SampleSchema())
    def fake(self, data):
        return data


def test_validate_success(dummy_request):
    data = {'test': 'test'}
    dummy_request.json_body = data

    result = Fake(dummy_request).fake()

    assert result == data


def test_validate_invalid(dummy_request, mocker):
    dummy_request.json_body = {}
    log_mock = mocker.patch('{{cookiecutter.project_slug}}.lib.schemas.logging.debug')
    expected_message = {
        'test': ["Missing data for required field."]
    }

    with pytest.raises(HTTPBadRequest) as bad_request:
        Fake(dummy_request).fake()

    log_mock.assert_called_once_with(expected_message)
    assert bad_request.value.json == {
        'message': expected_message
    }
