from http import HTTPStatus

from pyramid.view import forbidden_view_config


@forbidden_view_config(renderer='json')
def forbidden(request):
    if not request.user:
        # No user logged in
        request.response.status_code = HTTPStatus.UNAUTHORIZED
        return {'message': 'Unauthorized'}
    request.response.status_code = HTTPStatus.FORBIDDEN
    return {'message': 'Forbidden'}
