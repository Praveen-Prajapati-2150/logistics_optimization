from tortoise.models import Model
from tortoise import fields

class DriverVehicleAssignment(Model):
    id = fields.IntField(pk=True)
    driver = fields.ForeignKeyField("models.Driver", related_name="assignments")
    vehicle = fields.ForeignKeyField("models.Vehicle", related_name="assignments")
    active = fields.BooleanField(default=False)
    shift = fields.CharField(max_length=25, default="Day")  # New field for shift-based assignment
    created_at = fields.DatetimeField(auto_now_add=True)   # Renamed from assigned_at
