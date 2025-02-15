from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DriverAssignment(BaseModel):
    driver_id: int
    shift: Optional[str] = "Day"

class DriverAssignmentOut(BaseModel):
    id: int
    vehicle_id: int
    driver_id: int
    shift: Optional[str] = "Day"  # Changed from required to Optional with a default
    active: bool
    created_at: datetime

    class Config:
        # Use from_attributes for pydantic v2 compatibility
        from_attributes = True

class SwitchDriver(BaseModel):
    old_driver_id: int
    new_driver_id: int
    shift: Optional[str] = "Day"
