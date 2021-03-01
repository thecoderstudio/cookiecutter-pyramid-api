from {{cookiecutter.project_slug}}.lib.openapi.operation import OperationSpec
from tests.lib.openapi import SampleSchema


def test_build_minimal_operation_spec():
    spec = OperationSpec(
        request_schema_class=None,
        response_schema_class=None,
        successful_response_code=200,
        tags=[],
        public=True
    )

    assert spec.to_dict() == {
        'responses': {
            200: {}
        },
        'tags': [],
        'security': []
    }


def test_build_full_operation_spec():
    schema_class = SampleSchema
    spec = OperationSpec(
        request_schema_class=schema_class,
        response_schema_class=schema_class,
        successful_response_code=201,
        tags=['sample'],
        public=False
    )

    assert spec.to_dict() == {
        'tags': ['sample'],
        'security': {'auth_tkt': []},
        'responses': {
            201: {
                'content': {
                    'application/json': {
                        'schema': schema_class
                    }
                }
            },
            400: {},
            403: {}
        },
        'requestBody': {
            'content': {
                'application/json': {
                    'schema': schema_class
                }
            }
        }
    }
