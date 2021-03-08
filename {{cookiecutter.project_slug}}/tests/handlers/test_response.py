from {{cookiecutter.project_slug}}.handlers.response import forbidden


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
