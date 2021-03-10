from http import HTTPStatus
from typing import Optional, Type

from marshmallow import Schema

from {{cookiecutter.project_slug}}.lib.schemas.response import (
    CreatedSchema, ForbiddenSchema, InternalServerErrorSchema,
    NotFoundSchema, OKSchema, UnauthorizedSchema
)


class OperationSpec:
    def __init__(
        self,
        request_schema_class: Optional[Type[Schema]],
        response_schema_class: Optional[Type[Schema]],
        successful_response_code: int,
        tags: list[str],
        public: bool,
        not_found_possible: bool
    ):
        self.__dict__ = {
            'responses': {}
        }

        self._add_tags(tags)
        self._add_request(request_schema_class)
        self._add_unsuccessful_responses(not_found_possible)
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

    def _add_unsuccessful_responses(self, not_found_possible: bool):
        self.__dict__['responses'][HTTPStatus.INTERNAL_SERVER_ERROR] = (
            self._build_response_content(InternalServerErrorSchema))

        if not_found_possible:
            self.__dict__['responses'][HTTPStatus.NOT_FOUND] = (
                self._build_response_content(NotFoundSchema))

    def _add_successful_response(
        self,
        successful_response_code: int,
        response_schema_class: Type[Schema]
    ):
        successful_response_body = {}

        if response_schema_class:
            successful_response_body = self._build_response_content(
                response_schema_class)
        else:
            if successful_response_code == HTTPStatus.OK:
                successful_response_body = self._build_response_content(
                    OKSchema)
            elif successful_response_code == HTTPStatus.CREATED:
                successful_response_body = self._build_response_content(
                    CreatedSchema)

        self.__dict__['responses'][successful_response_code] = (
            successful_response_body)

    def _add_security(self, public: bool):
        if not public:
            self.__dict__['security'] = {'auth_tkt': []}
            self.__dict__['responses'].update({
                HTTPStatus.FORBIDDEN: self._build_response_content(
                    ForbiddenSchema),
                HTTPStatus.UNAUTHORIZED: self._build_response_content(
                    UnauthorizedSchema)
            })
        else:
            self.__dict__['security'] = []

    @staticmethod
    def _build_response_content(schema_class: Type[Schema]):
        return {
            'content': {
                'application/json': {
                    'schema': schema_class
                }
            }
        }

    def to_dict(self):
        return self.__dict__
