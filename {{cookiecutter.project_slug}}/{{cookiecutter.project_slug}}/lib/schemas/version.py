from marshmallow import fields, Schema


class VersionSchema(Schema):
    version = fields.Str(dump_only=True)
