from marshmallow import Schema, fields, validate

class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Amount must be strictly greater than 0")
    )
    category = fields.String(
        required=True,
        validate=validate.Length(min=1, error="Category cannot be empty")
    )
    description = fields.String(load_default="")
    date = fields.DateTime(dump_only=True)

transaction_schema = TransactionSchema()