from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import Authenticated, Everyone

from {{cookiecutter.project_slug}}.models.user import get_user_by_id


class DefaultAuthenticationPolicy(AuthTktAuthenticationPolicy):
    def effective_principals(self, request):
        principals = [Everyone]

        if request.authenticated_userid is not None:
            principals += [
                f"user:{request.authenticated_userid}",
                Authenticated
            ]

            try:
                if (request.user.active_recovery_token.used):
                    principals.append(
                        f"recovering_user:{request.authenticated_userid}"
                    )
            except AttributeError:
                pass

        return principals


def get_principals(user_id, request):
    return (f"user:{user_id}",)


def get_authenticated_user(request):
    if not request.authenticated_userid:
        return None

    return get_user_by_id(request.authenticated_userid)
