import os
import uuid
from configparser import ConfigParser

import redis
from pyramid.paster import get_appsettings
from pyramid.scripting import prepare
from pyramid.testing import DummyRequest
from pytest import fixture
from webtest import TestApp

import {{cookiecutter.project_slug}}.lib.settings
from {{cookiecutter.project_slug}} import main
from {{cookiecutter.project_slug}}.lib.openapi import APISpec, _init_spec
from {{cookiecutter.project_slug}}.lib.redis import RedisSession
from {{cookiecutter.project_slug}}.models import Base, save
from {{cookiecutter.project_slug}}.models.user import User

user_id = uuid.UUID('838c3768-768a-434a-b6e5-a77ba27d0ef7')


@fixture(scope='session')
def ini_file(request):
    return os.path.abspath('test.ini')


@fixture(scope='session')
def app_settings(ini_file):
    return get_appsettings(ini_file)


@fixture(scope='session')
def router(app_settings, ini_file):
    return main({'__file__': ini_file}, **app_settings)


@fixture
def test_app(router):
    return TestApp(router)


@fixture
def test_app_with_authenticated_user_id(test_app, dummy_user):
    email_address = dummy_user.email_address
    _, user_id = save(dummy_user)

    test_app.post_json('/auth/login', {
        'email_address': email_address,
        'password': 'testing123'
    })

    yield (test_app, user_id)


@fixture
def app_request(router, tm, dbsession):
    """
    A real request.

    This request is almost identical to a real request but it has some
    drawbacks in tests as it's harder to mock data and is heavier.
    """
    env = prepare(registry=router.registry)
    request = env['request']

    yield request
    env['closer']()


@fixture
def dummy_request(router):
    """
    A lightweight dummy request.

    This request is ultra-lightweight and should be used only when the
    request itself is not a large focus in the call-stack.

    It is way easier to mock and control side-effects using this object.

    - It does not have request extensions applied.
    - Threadlocals are not properly pushed.
    """
    request = DummyRequest()
    request.registry = router.registry

    return request


@fixture
def dummy_user():
    return User(
        id=user_id,
        email_address='{{cookiecutter.test_email_address}}',
        password_hash=(
            '$2b$12$FdTnxaL.NlRdEHREzbU3k.Nt1Gpii9vrKU.1h/MnZYdlMHPUW8/k.'),
        password_salt='$2b$12$FdTnxaL.NlRdEHREzbU3k.'
    )


@fixture(autouse=True)
def db_session(router, dummy_user):
    import transaction
    from {{cookiecutter.project_slug}}.models import session

    try:
        Base.metadata.create_all()
        session.configure(bind=Base.metadata.bind)
        with transaction.manager:
            yield session
    finally:
        session.remove()
        Base.metadata.drop_all()


@fixture(autouse=True, scope='function')
def redis_session(ini_file):
    try:
        config = ConfigParser()
        config.read(ini_file)
        settings = config['app:main']
        lifetime = settings['redis.default_ttl_in_seconds']

        redis_session = RedisSession(lifetime)
        redis_session.configure(settings['redis.sessions.host'])

        yield redis_session
    finally:
        redis_session.session = None
        redis.StrictRedis(
            host=settings['redis.sessions.host'],
            port=6379,
            db=0,
            password=None
        ).flushall()


@fixture
def patched_settings(mocker):
    mocker.patch('{{cookiecutter.project_slug}}.lib.settings.settings', {})
    yield {{cookiecutter.project_slug}}.lib.settings.settings
    {{cookiecutter.project_slug}}.lib.settings.settings = {}


@fixture
def clean_api_spec():
    APISpec.spec = _init_spec()
    return APISpec
