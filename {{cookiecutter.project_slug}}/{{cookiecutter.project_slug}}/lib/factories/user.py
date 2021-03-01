import uuid

from pyramid.security import Allow, Everyone
from sqlalchemy.orm.exc import NoResultFound

from {{cookiecutter.project_slug}}.lib.factories import BaseFactory
from {{cookiecutter.project_slug}}.models.user import get_one_user_by_id


class UserFactory(BaseFactory):
    @property
    def __getitem_methods__(self):
        return [
            self._get_current_user,
            self._get_user_by_id
        ]

    def __acl__(self):
        return ((Allow, Everyone, 'user.post'),)

    def _get_current_user(self, key):
        if key == 'me' and self.request.user:
            return self.request.user

    def _get_user_by_id(self, key):
        try:
            return get_one_user_by_id(uuid.UUID(key))
        except (ValueError, NoResultFound):
            return None
