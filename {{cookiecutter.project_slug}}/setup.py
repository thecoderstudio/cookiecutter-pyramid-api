import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'VERSION')) as f:
    VERSION = f.read().strip()

requires = [
    'alembic~=1.5',
    'apispec[validation]~=4.3',
    'bcrypt~=3.2',
    'marshmallow~=3.10',
    'psycopg2~=2.8',
    'pyramid~=1.10',
    'pyramid_session_redis~=1.5',
    'pyramid_tm~=2.4',
    'sendgrid~=6.6',
    'sqlalchemy~=1.3',
    'waitress~=1.4',
    'zope.sqlalchemy~=1.3'
]

tests_require = [
    'pytest~=6.2',
    'pytest-mock~=3.5',
    'webtest~=2.0',
    'sqlalchemy_utils~=0.36'
]

extras = {
    'tests': tests_require
}

setup(
    name='{{cookiecutter.project_slug}}',
    version=VERSION,
    description='{{cookiecutter.project_description}}',
    author="{{cookiecutter.author}}",
    author_email='{{cookiecutter.author_email}}',
    packages=find_packages(),
    tests_require=tests_require,
    install_requires=requires,
    extras_require=extras,
    entry_points="""\
    [paste.app_factory]
    main = {{cookiecutter.project_slug}}:main
    """
)
