import os


from {{cookiecutter.project_slug}} import main
from {{cookiecutter.project_slug}}.lib.factories.root import RootFactory


def test_init(app_settings):
    router = main(
        {'__file__': os.path.abspath('test.ini')},
        **app_settings
    )
    assert router.root_factory == RootFactory
