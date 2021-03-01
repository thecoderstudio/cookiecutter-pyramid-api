from {{cookiecutter.project_slug}}.handlers import view_config
from {{cookiecutter.project_slug}}.lib.factories.openapi import OpenAPIFactory
from {{cookiecutter.project_slug}}.lib.openapi import APISpec


@view_config(
    path_hints=['/openapi'],
    context=OpenAPIFactory,
    permission='openapi.get',
    request_method='GET',
    tags='openapi',
    public_hint=True
)
def get_spec(request):
    request.response.headers.update({
        'Access-Control-Allow-Origin': '*'
    })
    return APISpec.to_dict()
