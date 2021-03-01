from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories.root import RootFactory


def test_constructor(dummy_request):
    factory = RootFactory(dummy_request)
    assert factory.request == dummy_request


def test_acl(dummy_request):
    factory = RootFactory(dummy_request)
    assert factory.__acl__() == ((Allow, Everyone, 'index'),)
