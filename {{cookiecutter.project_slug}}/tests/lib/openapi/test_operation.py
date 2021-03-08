from http import HTTPStatus

from {{cookiecutter.project_slug}}.lib.openapi.operation import OperationSpec
from {{cookiecutter.project_slug}}.lib.schemas.response import ForbiddenSchema, UnauthorizedSchema
from tests.lib.openapi import SampleSchema


def test_build_minimal_operation_spec():
    spec = OperationSpec(
        request_schema_class=None,
        response_schema_class=None,
        successful_response_code=HTTPStatus.OK,
        tags=[],
        public=True
    )

    assert spec.to_dict() == {
        'responses': {
            HTTPStatus.OK: {}
        },
        'tags': [],
        'security': []
    }


def test_build_full_operation_spec():
    schema_class = SampleSchema
    spec = OperationSpec(
        request_schema_class=schema_class,
        response_schema_class=schema_class,
        successful_response_code=HTTPStatus.CREATED,
        tags=['sample'],
        public=False
    )

    assert spec.to_dict() == {
        'tags': ['sample'],
        'security': {'auth_tkt': []},
        'responses': {
            HTTPStatus.BAD_REQUEST: {},
            HTTPStatus.CREATED: {
                'content': {'application/json': {
                    'schema': schema_class
                }}
            },
            HTTPStatus.UNAUTHORIZED: {
                'content': {'application/json': {
                    'schema': UnauthorizedSchema
                }}
            },
            HTTPStatus.FORBIDDEN: {
                'content': {'application/json': {
                    'schema': ForbiddenSchema
                }}
            }
        },
        'requestBody': {
            'content': {
                'application/json': {
                    'schema': schema_class
                }
            }
        }
    }
