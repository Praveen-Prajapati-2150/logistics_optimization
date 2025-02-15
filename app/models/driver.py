from tortoise.models import Model
from tortoise import fields

class Driver(Model):
    id = fields.IntField(pk=True)
    mfo = fields.ForeignKeyField("models.MFO", related_name="drivers")
    name = fields.CharField(max_length=100)
    contact = fields.CharField(max_length=10, unique=True)
    license_number = fields.CharField(max_length=20, unique=True)
    status = fields.CharField(max_length=10, choices=["Active", "Inactive"])
