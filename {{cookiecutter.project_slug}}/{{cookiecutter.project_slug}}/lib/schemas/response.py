from marshmallow import fields, Schema
from marshmallow.validate import OneOf


class CreatedSchema(Schema):
    message = fields.Str(dump_only=True, validate=OneOf(["Resource created"]))


class ForbiddenSchema(Schema):
    message = fields.Str(dump_only=True, validate=OneOf(['Forbidden']))


class InternalServerErrorSchema(Schema):
    message = fields.Str(dump_only=True,
                         validate=OneOf(["Something went wrong on our end"]))


class NotFoundSchema(Schema):
    message = fields.Str(dump_only=True,
                         validate=OneOf(["The resource could not be found"]))


class OKSchema(Schema):
    message = fields.Str(dump_only=True,
                         validate=OneOf(["Request processed successfully"]))


class UnauthorizedSchema(Schema):
    message = fields.Str(dump_only=True, validate=OneOf(['Unauthorized']))
