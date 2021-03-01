import pytest

from {{cookiecutter.project_slug}}.lib.security.auth import AuthManager


def test_get_hash_and_salt_from_user_not_implemented(dummy_request):
    with pytest.raises(NotImplementedError):
        AuthManager(dummy_request)._get_hash_and_salt_from_user(None)
