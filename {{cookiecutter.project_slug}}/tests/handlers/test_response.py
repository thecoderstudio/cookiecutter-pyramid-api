import pytest
from pyramid.httpexceptions import (HTTPCreated, HTTPException,
                                    HTTPInternalServerError, HTTPOk)

from {{cookiecutter.project_slug}}.handlers.response import (
    created, forbidden, internal_server_error, ok, uncaught_exception)


def test_uncaught_exception(dummy_request, mocker):
    log_mock = mocker.patch('{{cookiecutter.project_slug}}.handlers.response.logging')
    exception = Exception()
    with pytest.raises(HTTPInternalServerError):
        uncaught_exception(exception, dummy_request)

    log_mock.error.assert_called_once_with(exception, exc_info=True)


def test_unauthorized(dummy_request):
    dummy_request.user = None
    result = forbidden(dummy_request)
    assert result == {
        'message': 'Unauthorized'
    }


def test_forbidden(dummy_request, dummy_user):
    dummy_request.user = dummy_user
    result = forbidden(dummy_request)
    assert result == {
        'message': 'Forbidden'
    }


def test_created(dummy_request):
    result = created(HTTPCreated(), dummy_request)
    assert_json_content(result, 'Resource created')
    assert isinstance(result, HTTPCreated)


def test_internal_server_error(dummy_request):
    result = internal_server_error(HTTPInternalServerError(), dummy_request)
    assert_json_content(result, 'Something went wrong on our end')
    assert isinstance(result, HTTPInternalServerError)


def test_ok(dummy_request):
    result = ok(HTTPOk(), dummy_request)
    assert_json_content(result, 'Request processed successfully')
    assert isinstance(result, HTTPOk)


def assert_json_content(http_exception: HTTPException, expected_message: str):
    assert http_exception.json == {'message': expected_message}
    assert http_exception.content_type == 'application/json'
