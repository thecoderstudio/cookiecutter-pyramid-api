import copy
import logging
import transaction
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register

from {{cookiecutter.project_slug}}.lib.settings import settings


session = scoped_session(sessionmaker())
register(session)


class Base:
    def set_fields(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


Base = declarative_base(cls=Base)


def init_sqlalchemy(settings_=settings):
    engine = create_engine(get_connection_url(settings_))
    session.configure(bind=engine)
    Base.metadata.bind = engine
    return engine


def get_connection_url(settings_):
    return "{driver}://{user}:{password}@{host}/{database}".format(
        **settings_['SQLAlchemy']
    )


def persist(obj):
    logging.debug("persisting object %r", obj)
    session.add(obj)
    session.flush()
    return obj


def _delete(obj):
    logging.debug(f"deleting object {obj}")
    session.delete(obj)


def rollback():
    logging.debug("Rolling back session: %r", session.dirty)
    return session.rollback()


def commit():
    logging.debug("Committing session: %r", session.dirty)
    transaction.commit()


def rollback_on_failure(action):
    def decorate(func):
        @wraps(func)
        def wrapped(obj, *args, **kwargs):
            try:
                return func(obj, *args, **kwargs)
            except Exception as e:
                logging.critical(
                    "Something went wrong {} the {}".format(
                        action, obj.__class__.__name__),
                    exc_info=True
                )
                rollback()
                raise e
            finally:
                commit()
        return wrapped
    return decorate


@rollback_on_failure('saving')
def save(obj):
    obj = persist(obj)
    try:
        id_ = obj.id
    except AttributeError:
        id_ = None
    # Shallow copy to be able to return generated data without having
    # to request the object again to get it in session.
    obj_copy = copy.copy(obj)

    return obj_copy, id_


@rollback_on_failure('deleting')
def delete(obj):
    _delete(obj)
