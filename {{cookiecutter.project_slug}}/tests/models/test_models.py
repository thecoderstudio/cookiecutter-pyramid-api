from unittest.mock import Mock

import pytest
import transaction
from sqlalchemy import Column, String

from {{cookiecutter.project_slug}}.models import (commit, delete, get_connection_url, Base,
                           persist, rollback, rollback_on_failure, save)
from {{cookiecutter.project_slug}}.models.user import User


def test_set_fields():
    class Sample(Base):
        __tablename__ = 'sample'

        a = Column(String, primary_key=True)
        b = Column(String)

    sample = Sample(a='1', b='2')
    sample.set_fields(b='3')

    assert sample.a == '1'
    assert sample.b == '3'


def test_get_connection_url():
    connection_url = get_connection_url({
        'SQLAlchemy': {
            'driver': 'postgresql',
            'user': 'test',
            'password': 'test',
            'host': 'localhost',
            'database': 'test'
        }
    })

    assert connection_url == "postgresql://test:test@localhost/test"


def test_persist(db_session, dummy_user):
    persist(dummy_user)
    user = db_session.query(User).get(dummy_user.id)
    assert user is not None


def test_rollback(db_session, dummy_user):
    dummy_user_id = dummy_user.id
    persist(dummy_user)
    rollback()

    with transaction.manager:
        user = db_session.query(User).get(dummy_user_id)
        assert user is None


def test_commit(db_session, dummy_user):
    dummy_user_id = dummy_user.id
    db_session.add(dummy_user)
    commit()
    user = db_session.query(User).get(dummy_user_id)
    assert user is not None


def test_rollback_on_failure_without_failure(db_session, dummy_user):
    dummy_user_id = dummy_user.id
    persist(dummy_user)

    @rollback_on_failure('testing')
    def test(obj, message):
        return message

    result = test(dummy_user, "test message")
    assert result == "test message"
    user = db_session.query(User).get(dummy_user_id)
    assert user is not None


def test_rollback_on_failure_with_failure(mocker, db_session, dummy_user):
    dummy_user_id = dummy_user.id
    persist(dummy_user)
    log_mock = mocker.patch('{{cookiecutter.project_slug}}.models.logging.critical')

    @rollback_on_failure('testing')
    def test(obj):
        raise Exception

    with pytest.raises(Exception):
        test(dummy_user)

    log_mock.assert_called_once_with(
        "Something went wrong testing the User",
        exc_info=True
    )
    with transaction.manager:
        user = db_session.query(User).get(dummy_user_id)
        assert user is None


def test_save_success(db_session, dummy_user):
    dummy_user_id = dummy_user.id
    user_copy, user_id = save(dummy_user)
    user = db_session.query(User).get(dummy_user_id)
    assert user_copy == user
    assert user_id == dummy_user_id


def test_save_success_no_id(mocker, dummy_user):
    mocker.patch('{{cookiecutter.project_slug}}.models.persist', return_value=Mock(spec=[]))
    _, user_id = save(dummy_user)
    assert user_id is None


def test_save_rollback(mocker, db_session, dummy_user):
    mocker.patch('{{cookiecutter.project_slug}}.models.persist', side_effect=Exception('test'))

    with pytest.raises(Exception):
        save(dummy_user)

    user = db_session.query(User).get(dummy_user.id)
    assert user is None


def test_delete(db_session, dummy_user):
    _, dummy_user_id = save(dummy_user)

    def get_user():
        return db_session.query(User).get(dummy_user_id)

    delete(get_user())
    assert get_user() is None


def test_delete_rollback(mocker, db_session, dummy_user):
    mocker.patch('{{cookiecutter.project_slug}}.models._delete', side_effect=Exception('test'))
    _, dummy_user_id = save(dummy_user)

    def get_user():
        return db_session.query(User).get(dummy_user_id)

    with pytest.raises(Exception):
        delete(get_user())

    assert get_user() is not None
