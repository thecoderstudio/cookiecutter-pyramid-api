import datetime

import pytest

from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.verification_token import (
    get_verification_token_by_id, VerificationToken)


def test_verification_token_active():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    assert verification_token.active


def test_verification_token_inactive():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    )

    assert not verification_token.active


def test_seconds_until_expiry():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    assert verification_token.seconds_until_expiry == pytest.approx((
        verification_token.expires_on - datetime.datetime.utcnow()
    ).total_seconds())


def test_seconds_until_expiry_expired():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    )

    assert verification_token.seconds_until_expiry == 0


def test_invalidate():
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake'
    )

    verification_token.invalidate()

    assert verification_token.invalidated


def test_get_verification_token_by_id(dummy_user):
    verification_token = VerificationToken(
        token_hash='fake',
        token_salt='fake',
        for_user=dummy_user
    )
    _, token_id = save(verification_token)

    assert get_verification_token_by_id(token_id).id == token_id
