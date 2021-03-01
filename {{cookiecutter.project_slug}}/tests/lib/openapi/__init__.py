from marshmallow import fields, Schema


class SampleSchema(Schema):
    test = fields.Str(required=True)
