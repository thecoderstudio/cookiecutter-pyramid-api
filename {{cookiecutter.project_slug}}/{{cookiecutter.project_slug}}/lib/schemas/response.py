from marshmallow import fields, Schema
from marshmallow.validate import OneOf


class ForbiddenSchema(Schema):
    message = fields.Str(dump_only=True, validate=OneOf(['Forbidden']))


class UnauthorizedSchema(Schema):
    message = fields.Str(dump_only=True, validate=OneOf(['Unauthorized']))
