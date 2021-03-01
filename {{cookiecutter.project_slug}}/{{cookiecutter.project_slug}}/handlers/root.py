from {{cookiecutter.project_slug}} import VERSION
from {{cookiecutter.project_slug}}.handlers import view_config
from {{cookiecutter.project_slug}}.lib.factories.root import RootFactory
from {{cookiecutter.project_slug}}.lib.schemas.version import VersionSchema


@view_config(
    path_hints=['/'],
    response_schema_class=VersionSchema,
    context=RootFactory,
    permission='index',
    request_method='GET',
    public_hint=True
)
def root(request):
    return VersionSchema().dump({
        'version': VERSION
    })
