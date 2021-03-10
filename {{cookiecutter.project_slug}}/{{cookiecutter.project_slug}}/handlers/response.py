import logging
from http import HTTPStatus

from pyramid.httpexceptions import (
    HTTPCreated, HTTPException, HTTPInternalServerError, HTTPNotFound, HTTPOk
)
from pyramid.view import (exception_view_config, forbidden_view_config,
                          view_config)


@exception_view_config(Exception, renderer='json')
def uncaught_exception(context, request):
    logging.error(context, exc_info=True)
    raise HTTPInternalServerError()


@forbidden_view_config(renderer='json')
def forbidden(request):
    if not request.user:
        # No user logged in
        request.response.status_code = HTTPStatus.UNAUTHORIZED
        return {'message': 'Unauthorized'}
    request.response.status_code = HTTPStatus.FORBIDDEN
    return {'message': 'Forbidden'}


@view_config(context=HTTPCreated, renderer='json')
def created(context, request):
    return _set_json_content(context, "Resource created")


@view_config(context=HTTPInternalServerError, renderer='json')
def internal_server_error(context, request):
    return _set_json_content(context, "Something went wrong on our end")


@view_config(context=HTTPNotFound, renderer='json')
def not_found(context, request):
    return _set_json_content(context, "The resource could not be found")


@view_config(context=HTTPOk, renderer='json')
def ok(context, request):
    return _set_json_content(context, "Request processed successfully")


def _set_json_content(http_exception: HTTPException, message: str):
    http_exception.json = {'message': message}
    http_exception.content_type = 'application/json'
    return http_exception
