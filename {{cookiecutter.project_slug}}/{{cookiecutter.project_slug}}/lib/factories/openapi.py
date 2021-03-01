from pyramid.security import Allow, Everyone

from {{cookiecutter.project_slug}}.lib.factories import BaseFactory


class OpenAPIFactory(BaseFactory):
    def __acl__(self):
        return ((Allow, Everyone, 'openapi.get'), )
