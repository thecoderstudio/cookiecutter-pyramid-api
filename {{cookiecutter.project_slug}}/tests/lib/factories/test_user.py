import uuid

import pytest
from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories.user import UserFactory
from {{cookiecutter.project_slug}}.models import save


def test_acl(dummy_request):
    factory = UserFactory(dummy_request)
    assert factory.__acl__() == ((Allow, Everyone, 'user.post'),)


def test_get_item_current_user(dummy_request, dummy_user):
    dummy_request.user = dummy_user

    result_user = UserFactory(dummy_request).__getitem__('me')

    assert result_user == dummy_user


def test_get_item_user_by_id(dummy_request, dummy_user):
    _, user_id = save(dummy_user)

    result_user = UserFactory(dummy_request).__getitem__(str(user_id))

    assert result_user.id == user_id


def test_get_item_not_found(dummy_request):
    with pytest.raises(KeyError):
        UserFactory(dummy_request).__getitem__(str(uuid.uuid4()))
