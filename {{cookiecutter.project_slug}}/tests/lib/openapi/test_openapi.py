from http import HTTPStatus

import pytest

from {{cookiecutter.project_slug}} import VERSION
from {{cookiecutter.project_slug}}.lib.openapi import OPENAPI_VERSION
from tests.lib.openapi import SampleSchema

security_schemas = {
    'Unauthorized': {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'enum': ['Unauthorized'],
                'readOnly': True
            }
        }
    },
    'Forbidden': {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'enum': ['Forbidden'],
                'readOnly': True
            }
        }
    }
}


@pytest.mark.parametrize('request_method', ('GET', 'POST', 'PUT', 'PATCH',
                                            'DELETE'))
def test_register_minimal_handler(clean_api_spec, request_method):
    clean_api_spec.register_handler(
        paths=['/sample'],
        request_method=request_method
    )

    if request_method == 'POST':
        expected_status_code = HTTPStatus.CREATED
    elif request_method == 'DELETE':
        expected_status_code = HTTPStatus.NO_CONTENT
    else:
        expected_status_code = HTTPStatus.OK

    assert clean_api_spec.to_dict() == get_expected_spec({
        '/sample': {
            request_method.lower(): {
                'tags': [],
                'responses': {
                    str(int(expected_status_code)): {},
                    str(int(HTTPStatus.UNAUTHORIZED)): {
                        'content': {'application/json': {'schema': {
                            '$ref': '#/components/schemas/Unauthorized'
                        }}}
                    },
                    str(int(HTTPStatus.FORBIDDEN)): {
                        'content': {'application/json': {'schema': {
                            '$ref': '#/components/schemas/Forbidden'
                        }}}
                    }
                },
                'security': {
                    'auth_tkt': []
                }
            }
        }
    }, schemas=security_schemas)


def test_register_full_handler(clean_api_spec):
    clean_api_spec.register_handler(
        paths=['/sample', '/alias'],
        request_method='POST',
        request_schema_class=SampleSchema,
        response_schema_class=SampleSchema,
        successful_response_code=int(HTTPStatus.ACCEPTED),
        tags=['sample', 'alias'],
        public=True
    )

    expected_path_spec = {
        'post': {
            'tags': ['sample', 'alias'],
            'responses': {
                str(int(HTTPStatus.ACCEPTED)): {
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Sample'
                            }
                        }
                    }
                },
                str(int(HTTPStatus.BAD_REQUEST)): {},
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
        {
            'Sample': {
                'type': 'object',
                'properties': {
                    'test': {'type': 'string'}
                },
                'required': ['test']
            }
        }
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
