import logging

from marshmallow import ValidationError
from pyramid.httpexceptions import HTTPBadRequest


def validate(data, validation_schema):
    try:
        return validation_schema.load(data)
    except ValidationError as e:
        logging.debug(e.messages)
        raise HTTPBadRequest(json={'message': e.messages})
