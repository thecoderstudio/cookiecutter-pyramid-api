import uuid

from pyramid.security import Allow

from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.verification_token import VerificationToken
from {{cookiecutter.project_slug}}.models.user import (get_user_by_email_address, get_one_user_by_id,
                                get_user_by_id, User)


def test_get_user_by_email_address(dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    assert get_user_by_email_address(email_address).id == user_id


def test_get_user_by_email_address_not_found():
    assert get_user_by_email_address('{{cookiecutter.alternative_test_email_address}}') is None


def test_get_one_user_by_id(dummy_user):
    _, user_id = save(dummy_user)
    user = get_one_user_by_id(user_id)

    assert user.id == user_id


def test_get_user_by_id(dummy_user):
    _, user_id = save(dummy_user)
    user = get_user_by_id(user_id)

    assert user.id == user_id


def test_user_eq_instance():
    assert (User() == object()) is False


def test_user_eq():
    user_1 = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake"
    )
    user_2 = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake"
    )

    assert user_1 == user_1
    assert (user_1 == user_2) is False


def test_user_ne_instance():
    assert User() != object()


def test_user_ne():
    user_1 = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake"
    )
    user_2 = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake"
    )

    assert (user_1 != user_1) is False
    assert user_1 != user_2


def test_user_acl():
    user = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake"
    )

    assert user.__acl__() == (
        (Allow, f"user:{user.id}", 'user.get'),
        (Allow, f"user:{user.id}", 'user.patch'),
        (Allow, f"user:{user.id}", 'user.request_verification_token'),
        (Allow, f"recovering_user:{user.id}", 'user.reset_password')
    )


def test_user_set_fields():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake'
    )
    user = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake",
        active_verification_token=verification_token
    )
    new_email_address = 'fake@robinsiep.dev'

    user.set_fields(email_address=new_email_address, verified=True)

    assert user.email_address == new_email_address
    assert user.verified
    assert verification_token.invalidated


def test_user_set_verified():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake'
    )
    user = User(
        id=uuid.uuid4(),
        email_address="{{cookiecutter.test_email_address}}",
        password_hash="fake",
        password_salt="fake",
        active_verification_token=verification_token
    )

    user.set_verified()

    assert user.verified
    assert verification_token.invalidated
