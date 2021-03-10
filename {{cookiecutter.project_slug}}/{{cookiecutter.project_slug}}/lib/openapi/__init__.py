from http import HTTPStatus
from typing import Type, Union

from apispec import APISpec as APISpecBuilder
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema

from {{cookiecutter.project_slug}} import VERSION
from {{cookiecutter.project_slug}}.lib.openapi.operation import OperationSpec

OPENAPI_VERSION = '3.0.2'


def _init_spec():
    return APISpecBuilder(
        title="{{cookiecutter.project_name}}",
        version=VERSION,
        openapi_version=OPENAPI_VERSION,
        info=dict(description="{{cookiecutter.project_description}}"),
        components={
            'securitySchemes': {
                'auth_tkt': {
                    'type': 'apiKey',
                    'name':  'auth_tkt',
                    'in': 'cookie'
                }
            }
        },
        plugins=(MarshmallowPlugin(),)
    )


class APISpec:
    """Responsible for managing the OpenAPI specification for this application.
    """
    spec = _init_spec()

    @staticmethod
    def register_handler(
        paths: list[str],
        request_method: str,
        request_schema_class: Type[Schema] = None,
        response_schema_class: Type[Schema] = None,
        successful_response_code: int = None,
        tags: Union[str, list[str]] = [],
        public: bool = False,
        not_found_possible: bool = False
    ):
        tags = APISpec._parse_tags(tags)
        successful_response_code = APISpec._get_response_code_or_default(
            successful_response_code,
            request_method
        )

        operation_spec = OperationSpec(
            request_schema_class,
            response_schema_class,
            successful_response_code,
            tags,
            public,
            not_found_possible
        )

        for path in paths:
            APISpec.spec.path(
                path=path,
                operations={
                    request_method.lower(): operation_spec.to_dict()
                }
            )

    @staticmethod
    def _parse_tags(tags: Union[str, list[str]]):
        if not isinstance(tags, list):
            tags = [tags]

        return tags

    @staticmethod
    def _get_response_code_or_default(
        response_code: int,
        request_method: str
    ):
        if response_code:
            return response_code

        return APISpec._get_default_response_code_for_request_method(
            request_method)

    @staticmethod
    def _get_default_response_code_for_request_method(request_method: str):
        if request_method == 'POST':
            return HTTPStatus.CREATED
        elif request_method == 'DELETE':
            return HTTPStatus.NO_CONTENT
        else:
            return HTTPStatus.OK

    @staticmethod
    def to_dict():
        return APISpec.spec.to_dict()
