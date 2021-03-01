from {{cookiecutter.project_slug}}.lib.resources import LocationAwareResource


class BaseFactory(dict, LocationAwareResource):
    __getitem_methods__ = []

    def __init__(self, request, parent=None):
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, key):
        for method in self.__getitem_methods__:
            resource = method(key)
            if not resource:
                continue

            resource.__parent__ = self
            return resource

        return super().__getitem__(key)
