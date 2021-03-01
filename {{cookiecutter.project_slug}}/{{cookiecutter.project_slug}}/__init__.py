import pkg_resources
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from {{cookiecutter.project_slug}}.lib.redis import RedisSession
from {{cookiecutter.project_slug}}.lib.security import (DefaultAuthenticationPolicy, get_principals,
                                 get_authenticated_user)
from {{cookiecutter.project_slug}}.lib.settings import init_settings, read_config, settings
from {{cookiecutter.project_slug}}.models import init_sqlalchemy

VERSION = pkg_resources.require('{{cookiecutter.project_slug}}')[0].version


def main(global_config, **main_settings):
    from {{cookiecutter.project_slug}}.lib.factories.root import RootFactory
    init_settings(read_config(global_config['__file__']))
    init_sqlalchemy()

    auth_settings = settings['auth']
    authentication_policy = DefaultAuthenticationPolicy(
        secret=auth_settings['secret'],
        timeout=auth_settings.get('timeout'),
        reissue_time=auth_settings.get('reissue_time'),
        callback=get_principals,
        http_only=True,
        hashalg='sha512'
    )

    config = Configurator(
        authentication_policy=authentication_policy,
        authorization_policy=ACLAuthorizationPolicy(),
        root_factory=RootFactory,
        settings=settings
    )
    config.scan('{{cookiecutter.project_slug}}.handlers')
    config.add_request_method(get_authenticated_user, 'user', reify=True)

    init_cache(settings['app:main'])

    return config.make_wsgi_app()


def init_cache(app_settings):
    redis_session = RedisSession(app_settings['redis.default_ttl_in_seconds'])
    redis_session.configure(host=app_settings['redis.sessions.host'])
