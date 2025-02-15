from pydantic import BaseModel
from typing import Optional

class DriverCreate(BaseModel):
    name: str
    contact: str
    license_number: str  # Updated field name
    status: str

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    license_number: Optional[str] = None  # Updated field name
    status: Optional[str] = None

class DriverOut(BaseModel):
    id: int
    mfo_id: int
    name: str
    contact: str
    license_number: str  # Updated field name
    status: str

    class Config:
        from_attributes = True

class DriverDelete(BaseModel):
    id: int