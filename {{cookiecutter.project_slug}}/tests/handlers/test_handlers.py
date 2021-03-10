from http import HTTPStatus

from {{cookiecutter.project_slug}} import VERSION
from {{cookiecutter.project_slug}}.handlers import Handler, view_config
from {{cookiecutter.project_slug}}.lib.openapi import OPENAPI_VERSION


def test_handler_constructor(dummy_request, mocker):
    mock = mocker.Mock()
    handler = Handler(mock, dummy_request)

    assert handler.context == mock
    assert handler.request == dummy_request


def test_view_config(clean_api_spec):
    @view_config(
        path_hints=['/sample'],
        request_method='POST'
    )
    def sample():
        pass

    assert clean_api_spec.to_dict() == {
        'openapi': OPENAPI_VERSION,
        'paths': {
            '/sample': {
                'post': {
                    'tags': [],
                    'responses': {
                        str(int(HTTPStatus.CREATED)): {
                            'content': {'application/json': {'schema': {
                                '$ref': '#/components/schemas/Created'
                            }}}
                        },
                        str(int(HTTPStatus.UNAUTHORIZED)): {
                            'content': {'application/json': {'schema': {
                                '$ref': '#/components/schemas/Unauthorized'
                            }}}
                        },
                        str(int(HTTPStatus.FORBIDDEN)): {
                            'content': {'application/json': {'schema': {
                                '$ref': '#/components/schemas/Forbidden'
                            }}}
                        },
                        str(int(HTTPStatus.INTERNAL_SERVER_ERROR)): {
                            'content': {'application/json': {'schema': {
                                '$ref': (
                                    '#/components/schemas/InternalServerError')
                            }}}
                        }
                    },
                    'security': {
                        'auth_tkt': []
                    }
                }
            }
        },
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
            },
            'schemas': {
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
                },
                'Created': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'enum': ["Resource created"],
                            'readOnly': True
                        }
                    }
                },
                'InternalServerError': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'enum': ["Something went wrong on our end"],
                            'readOnly': True
                        }
                    }
                }
            }
        }
    }
