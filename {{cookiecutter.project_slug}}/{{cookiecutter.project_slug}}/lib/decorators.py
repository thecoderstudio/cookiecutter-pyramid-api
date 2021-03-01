from functools import wraps

from {{cookiecutter.project_slug}}.lib.schemas import validate as validate_


def validate(validation_schema):
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            validated_data = validate_(self.request.json_body,
                                       validation_schema)
            return func(self, validated_data, *args, **kwargs)
        return wrapper
    return decorate
