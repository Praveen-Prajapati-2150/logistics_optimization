from pydantic import BaseModel

class MFOCreate(BaseModel):
    name: str
    email: str
    password: str

class MFOOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True
