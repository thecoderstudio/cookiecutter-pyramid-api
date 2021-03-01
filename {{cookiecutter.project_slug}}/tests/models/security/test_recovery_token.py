import datetime

import pytest

from {{cookiecutter.project_slug}}.models import save
from {{cookiecutter.project_slug}}.models.security.recovery_token import (get_recovery_token_by_id,
                                                   RecoveryToken)


def test_recovery_token_active():
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    assert recovery_token.active


def test_recovery_token_inactive():
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    )

    assert not recovery_token.active


def test_seconds_until_expiry():
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )

    assert recovery_token.seconds_until_expiry == pytest.approx((
        recovery_token.expires_on - datetime.datetime.utcnow()
    ).total_seconds())


def test_seconds_until_expiry_expired():
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake',
        expires_on=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    )

    assert recovery_token.seconds_until_expiry == 0


def test_invalidate():
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake'
    )

    recovery_token.invalidate()

    assert recovery_token.invalidated


def test_get_recovery_token_by_id(dummy_user):
    recovery_token = RecoveryToken(
        token_hash='fake',
        token_salt='fake',
        for_user=dummy_user
    )
    _, recovery_token_id = save(recovery_token)

    assert get_recovery_token_by_id(recovery_token_id).id == recovery_token_id
