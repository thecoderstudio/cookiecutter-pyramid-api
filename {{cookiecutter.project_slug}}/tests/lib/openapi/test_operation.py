from http import HTTPStatus

from {{cookiecutter.project_slug}}.lib.openapi.operation import OperationSpec
from {{cookiecutter.project_slug}}.lib.schemas.response import (
    ForbiddenSchema, InternalServerErrorSchema, NotFoundSchema, OKSchema,
    UnauthorizedSchema
)
from tests.lib.openapi import SampleSchema


def test_build_minimal_operation_spec():
    spec = OperationSpec(
        request_schema_class=None,
        response_schema_class=None,
        successful_response_code=HTTPStatus.OK,
        tags=[],
        public=True,
        not_found_possible=False
    )

    assert spec.to_dict() == {
        'responses': {
            HTTPStatus.OK: {
                'content': {'application/json': {
                    'schema': OKSchema
                }}
            },
            HTTPStatus.INTERNAL_SERVER_ERROR: {
                'content': {'application/json': {
                    'schema': InternalServerErrorSchema
                }}
            }
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
        public=False,
        not_found_possible=True
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
            },
            HTTPStatus.INTERNAL_SERVER_ERROR: {
                'content': {'application/json': {
                    'schema': InternalServerErrorSchema
                }}
            },
            HTTPStatus.NOT_FOUND: {
                'content': {'application/json': {
                    'schema': NotFoundSchema
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
