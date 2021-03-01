from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories.openapi import OpenAPIFactory


def test_acl(dummy_request):
    factory = OpenAPIFactory(dummy_request)
    return factory.__acl__() == ((Allow, Everyone, 'openapi.get'), )
