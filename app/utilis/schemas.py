from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class OrganizationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str(validate=validate.OneOf(['pending', 'approved', 'rejected']))
    created_at = fields.DateTime(dump_only=True)

class DonationSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    currency = fields.Str(validate=validate.Length(equal=3))
    is_anonymous = fields.Bool()
    is_recurring = fields.Bool()
    recurring_interval = fields.Str(validate=validate.OneOf(['monthly', 'quarterly', 'yearly']))
    payment_status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    organization_id = fields.Int(required=True)
    payment_method_id = fields.Str()

class StorySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    image_url = fields.Url()
    created_at = fields.DateTime(dump_only=True)
    organization_id = fields.Int(required=True)

class BeneficiarySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    impact_details = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    organization_id = fields.Int(required=True)