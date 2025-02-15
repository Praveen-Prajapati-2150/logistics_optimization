from tortoise.models import Model
from tortoise import fields

class MFO(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

