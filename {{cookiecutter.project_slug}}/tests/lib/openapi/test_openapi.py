from http import HTTPStatus

import pytest

from {{cookiecutter.project_slug}} import VERSION
from {{cookiecutter.project_slug}}.lib.openapi import OPENAPI_VERSION
from tests.lib.openapi import SampleSchema


def _build_openapi_response_schema(error_message: str):
    return {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'enum': [error_message],
                'readOnly': True
            }
        }
    }


security_schemas = {
    'Unauthorized': _build_openapi_response_schema('Unauthorized'),
    'Forbidden': _build_openapi_response_schema('Forbidden')
}

error_schemas = {
    'InternalServerError': _build_openapi_response_schema(
        "Something went wrong on our end")
}


@pytest.mark.parametrize('request_method', ('GET', 'POST', 'PUT', 'PATCH',
                                            'DELETE'))
def test_register_minimal_handler(clean_api_spec, request_method):
    clean_api_spec.register_handler(
        paths=['/sample'],
        request_method=request_method
    )
    schemas = security_schemas | error_schemas

    if request_method == 'POST':
        expected_status_code = HTTPStatus.CREATED
        expected_success_response = _build_expected_response('Created')
        schemas['Created'] = _build_openapi_response_schema("Resource created")
    elif request_method == 'DELETE':
        expected_status_code = HTTPStatus.NO_CONTENT
        expected_success_response = {}
    else:
        expected_status_code = HTTPStatus.OK
        expected_success_response = _build_expected_response('OK')
        schemas['OK'] = _build_openapi_response_schema(
            "Request processed successfully")

    assert clean_api_spec.to_dict() == get_expected_spec({
        '/sample': {
            request_method.lower(): {
                'tags': [],
                'responses': {
                    str(int(expected_status_code)): expected_success_response,
                    str(int(HTTPStatus.UNAUTHORIZED)): (
                        _build_expected_response('Unauthorized')),
                    str(int(HTTPStatus.FORBIDDEN)): (
                        _build_expected_response('Forbidden')),
                    str(int(HTTPStatus.INTERNAL_SERVER_ERROR)): (
                        _build_expected_response('InternalServerError'))
                },
                'security': {
                    'auth_tkt': []
                }
            }
        }
    }, schemas=schemas)


def _build_expected_response(openapi_schema_name: str):
    return {
        'content': {
            'application/json': {
                'schema': {
                    '$ref': f"#/components/schemas/{openapi_schema_name}"
                }
            }
        }
    }


def test_register_full_handler(clean_api_spec):
    clean_api_spec.register_handler(
        paths=['/sample', '/alias'],
        request_method='POST',
        request_schema_class=SampleSchema,
        response_schema_class=SampleSchema,
        successful_response_code=int(HTTPStatus.ACCEPTED),
        tags=['sample', 'alias'],
        public=True,
        not_found_possible=True
    )

    schemas = {
        'Sample': {
            'type': 'object',
            'properties': {
                'test': {'type': 'string'}
            },
            'required': ['test']
        },
        'NotFound': _build_openapi_response_schema(
            "The resource could not be found")
    }

    expected_path_spec = {
        'post': {
            'tags': ['sample', 'alias'],
            'responses': {
                str(int(HTTPStatus.BAD_REQUEST)): {},
                str(int(HTTPStatus.ACCEPTED)): (
                    _build_expected_response('Sample')),
                str(int(HTTPStatus.INTERNAL_SERVER_ERROR)): (
                    _build_expected_response('InternalServerError')),
                str(int(HTTPStatus.NOT_FOUND)): (
                    _build_expected_response('NotFound'))
            },
            'requestBody': {
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/Sample'
                        }
                    }
                }
            },
            'security': []
        }
    }

    assert clean_api_spec.to_dict() == get_expected_spec(
        {
            '/sample': expected_path_spec,
            '/alias': expected_path_spec
        },
        schemas | error_schemas
    )


def test_api_spec_to_dict(clean_api_spec):
    assert clean_api_spec.to_dict() == get_expected_spec()


def get_expected_spec(paths={}, schemas=None):
    spec = {
        'openapi': OPENAPI_VERSION,
        'paths': paths,
        'info': {
            'description': '{{cookiecutter.project_description}}',
            'title': '{{cookiecutter.project_name}}',
            'version': VERSION
        },
        'components': {
            'securitySchemes': {
                'auth_tkt': {
                    'type': 'apiKey',
                    'name': 'auth_tkt',
                    'in': 'cookie'
                }
            }
        }
    }

    if schemas:
        spec['components']['schemas'] = schemas

    return spec
