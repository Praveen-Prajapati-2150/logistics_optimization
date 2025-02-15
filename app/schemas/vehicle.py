from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VehicleCreate(BaseModel):
    model: str
    number_plate: str
    battery_capacity: float
    soc: float
    last_maintenance: datetime = None
    status: str

class VehicleUpdate(BaseModel):
    model: str
    number_plate: str
    battery_capacity: float
    soc: float
    last_maintenance: datetime = None
    status: str

class VehicleOut(BaseModel):
    id: int
    mfo_id: int
    model: str
    number_plate: str
    battery_capacity: float
    soc: float
    last_maintenance: datetime = None
    status: str

    class Config:
        from_attributes = True

class VehiclePatch(BaseModel):
    model: Optional[str] = None
    number_plate: Optional[str] = None
    battery_capacity: Optional[float] = None
    soc: Optional[float] = None
    last_maintenance: Optional[datetime] = None
    status: Optional[str] = None
