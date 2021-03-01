from typing import Type, Union

from marshmallow import Schema
from pyramid.view import view_config as pyramid_view_config

from {{cookiecutter.project_slug}}.lib.openapi import APISpec


class Handler:
    def __init__(self, context, request):
        self.context = context
        self.request = request


class view_config(pyramid_view_config):
    def __init__(
        self,
        path_hints: list[str],
        request_method: str,
        request_schema_class: Type[Schema] = None,
        response_schema_class: Type[Schema] = None,
        successful_response_code: int = None,
        tags: Union[str, list[str]] = [],
        public_hint: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(request_method=request_method, renderer='json',
                         *args, **kwargs)
        APISpec.register_handler(
            path_hints,
            request_method,
            request_schema_class,
            response_schema_class,
            successful_response_code,
            tags,
            public_hint
        )
