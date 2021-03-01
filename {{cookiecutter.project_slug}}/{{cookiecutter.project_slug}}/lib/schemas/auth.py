from marshmallow import fields, Schema


class AccountRecoverySchema(Schema):
    email_address = fields.Email(required=True, load_only=True)


class BaseLoginSchema(Schema):
    email_address = fields.Email(required=True, load_only=True)


class AccountRecoveryLoginSchema(BaseLoginSchema):
    token = fields.Str(required=True, load_only=True)


class LoginSchema(BaseLoginSchema):
    password = fields.Str(required=True, load_only=True)
