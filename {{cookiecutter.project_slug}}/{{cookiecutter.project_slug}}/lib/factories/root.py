from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories import BaseFactory
from {{cookiecutter.project_slug}}.lib.factories.auth import AuthFactory
from {{cookiecutter.project_slug}}.lib.factories.openapi import OpenAPIFactory
from {{cookiecutter.project_slug}}.lib.factories.user import UserFactory


class RootFactory(BaseFactory):
    def __init__(self, request):
        super().__init__(request)
        self['auth'] = AuthFactory(request, self)
        self['openapi'] = OpenAPIFactory(request, self)
        self['user'] = UserFactory(request, self)

    def __acl__(self):
        return ((Allow, Everyone, 'index'),)
