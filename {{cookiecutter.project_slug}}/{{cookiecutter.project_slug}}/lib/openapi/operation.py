from http import HTTPStatus
from typing import Optional, Type

from marshmallow import Schema


class OperationSpec:
    def __init__(
        self,
        request_schema_class: Optional[Type[Schema]],
        response_schema_class: Optional[Type[Schema]],
        successful_response_code: int,
        tags: list[str],
        public: bool
    ):
        self.__dict__ = {
            'responses': {}
        }

        self._add_tags(tags)
        self._add_request(request_schema_class)
        self._add_successful_response(successful_response_code,
                                      response_schema_class)
        self._add_security(public)

    def _add_tags(self, tags: list[str]):
        self.__dict__['tags'] = tags

    def _add_request(self, request_schema_class: Type[Schema]):
        if not request_schema_class:
            return

        self.__dict__['requestBody'] = {
            'content': {
                'application/json': {
                    'schema': request_schema_class
                }
            }
        }
        self.__dict__['responses'][HTTPStatus.BAD_REQUEST] = {}

    def _add_successful_response(
        self,
        successful_response_code: int,
        response_schema_class
    ):
        successful_response_body = {}

        if response_schema_class:
            successful_response_body = {
                'content': {
                    'application/json': {
                        'schema': response_schema_class
                    }
                }
            }

        self.__dict__['responses'][successful_response_code] = (
            successful_response_body)

    def _add_security(self, public: bool):
        if not public:
            self.__dict__['security'] = {'auth_tkt': []}
            self.__dict__['responses'][HTTPStatus.FORBIDDEN] = {}
        else:
            self.__dict__['security'] = []

    def to_dict(self):
        return self.__dict__
