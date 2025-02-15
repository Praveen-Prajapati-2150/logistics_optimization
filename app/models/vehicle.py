from tortoise.models import Model
from tortoise import fields

class Vehicle(Model):
    id = fields.IntField(pk=True)
    mfo = fields.ForeignKeyField("models.MFO", related_name="vehicles")
    model = fields.CharField(max_length=100)
    number_plate = fields.CharField(max_length=12, unique=True)
    battery_capacity = fields.FloatField()
    soc = fields.FloatField()  # State of Charge
    last_maintenance = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=25, choices=["Active", "Maintenance", "Unavailable"])
