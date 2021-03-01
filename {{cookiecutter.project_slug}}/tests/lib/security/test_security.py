import uuid
from unittest.mock import Mock, PropertyMock

from pyramid.security import Authenticated, Everyone

from {{cookiecutter.project_slug}}.lib.security import (
    DefaultAuthenticationPolicy, get_authenticated_user, get_principals)
from {{cookiecutter.project_slug}}.models import save


def test_policy_effective_principals(dummy_request):
    policy = DefaultAuthenticationPolicy("fakesecret")
    principals = policy.effective_principals(dummy_request)

    assert principals == [Everyone]


def test_policy_authenticated_principals():
    user_id = uuid.uuid4()
    policy = DefaultAuthenticationPolicy("fakesecret")
    mock_request = Mock()
    type(mock_request).authenticated_userid = PropertyMock(
        return_value=user_id)

    principals = policy.effective_principals(mock_request)

    assert principals == [
        Everyone,
        f"user:{user_id}",
        Authenticated,
        f"recovering_user:{user_id}"
    ]


def test_get_principals(dummy_request):
    id_ = uuid.uuid4()
    principals = get_principals(id_, dummy_request)

    assert principals == (f"user:{id_}",)


def test_get_authenticated_user(dummy_user):
    _, user_id = save(dummy_user)
    mock_request = Mock()
    type(mock_request).authenticated_userid = PropertyMock(
        return_value=user_id)

    assert get_authenticated_user(mock_request).id == user_id
