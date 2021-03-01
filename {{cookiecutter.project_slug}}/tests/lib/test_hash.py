import pytest

from {{cookiecutter.project_slug}}.lib.hash import hash_plaintext, compare_plaintext_to_hash

PASSWORD_HASH = (
    '$2b$12$50eN8MSIm9KDRpzmGL4JQO9gGy.2MDAafSOtqu9mZwfkb7jh33j26'
)
PASSWORD_SALT = (
    '$2b$12$50eN8MSIm9KDRpzmGL4JQO'
)


def test_hash_plaintext():
    password_hash, _ = hash_plaintext(
        'password', PASSWORD_SALT.encode('utf-8'))

    assert password_hash == PASSWORD_HASH

    password_hash, _ = hash_plaintext('password')

    assert password_hash != PASSWORD_HASH


def test_hash_plaintext_no_salt_different_outcome():
    password_hash, _ = hash_plaintext('password')
    password_hash_2, _ = hash_plaintext('password')

    assert password_hash != password_hash_2


def test_compare_plaintext_to_hash():
    assert compare_plaintext_to_hash(
        'password', PASSWORD_HASH, PASSWORD_SALT) is True
    assert compare_plaintext_to_hash(
        'fakepassword', PASSWORD_HASH, PASSWORD_SALT) is False


def test_compare_plaintext_to_hash_no_password():
    with pytest.raises(AttributeError):
        compare_plaintext_to_hash(None, 'hash', 'salt')


def test_compare_plaintext_to_hash_salt_from_hash():
    assert compare_plaintext_to_hash('password', PASSWORD_HASH) is True
