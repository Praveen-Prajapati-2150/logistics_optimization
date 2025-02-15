from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.mfo import MFO
from app.schemas.mfo import MFOCreate, MFOOut
from app.core.auth import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register/")
async def register_mfo(mfo: MFOCreate):
    print(mfo)
    existing = await MFO.get_or_none(email=mfo.email)
    if existing:
        raise HTTPException(status_code=400, detail="MFO already exists")
    mfo_obj = await MFO.create(name=mfo.name, email=mfo.email, password_hash=hash_password(mfo.password))
    return {"id": mfo_obj.id, "email": mfo_obj.email}

@router.post("/login/")
async def login_mfo(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    mfo = await MFO.get_or_none(email=form_data.username)
    if not mfo or not verify_password(form_data.password, mfo.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": mfo.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/{mfo_id}/", response_model=MFOOut)
async def get_mfo(mfo_id: int):
    print(mfo_id)
    mfo = await MFO.get_or_none(id=mfo_id)
    if not mfo:
        raise HTTPException(status_code=404, detail="MFO not found")
    return mfo
