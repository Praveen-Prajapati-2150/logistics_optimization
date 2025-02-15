import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models.driver import Driver
from app.models.mfo import MFO
from app.schemas.driver import DriverCreate, DriverUpdate, DriverDelete, DriverOut
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/mfo/login")

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_current_mfo(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.error("Token payload does not contain 'sub'")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError: {e}")
        raise credentials_exception
    mfo = await MFO.get_or_none(email=email)
    if mfo is None:
        logger.error(f"No MFO found with email: {email}")
        raise credentials_exception
    return mfo

@router.post("/", response_model=DriverOut)
async def add_driver(request: Request, driver: DriverCreate, mfo: MFO = Depends(get_current_mfo)):
    logger.info(f"Request body: {await request.body()}")
    logger.info(f"Adding driver for MFO: {mfo.id}")
    driver_data = driver.model_dump()
    driver_data['mfo_id'] = mfo.id
    driver_obj = await Driver.create(**driver_data)
    return driver_obj

@router.patch("/{driver_id}", response_model=DriverOut)
async def patch_driver(driver_id: int, driver: DriverUpdate, mfo: MFO = Depends(get_current_mfo)):
    driver_obj = await Driver.get_or_none(id=driver_id)
    if not driver_obj:
        raise HTTPException(status_code=404, detail="Driver not found")
    logger.info(f"Patching driver with ID: {driver_id}")
    logger.info(f"Driver data: {driver.model_dump(exclude_unset=True)}")
    await driver_obj.update_from_dict(driver.model_dump(exclude_unset=True))
    await driver_obj.save()
    return driver_obj

@router.get("/{driver_id}", response_model=DriverOut)
async def get_driver(driver_id: int, mfo: MFO = Depends(get_current_mfo)):
    driver_obj = await Driver.get_or_none(id=driver_id)
    if not driver_obj:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver_obj

@router.delete("/", response_model=DriverOut)
async def delete_driver(driver: DriverDelete, mfo: MFO = Depends(get_current_mfo)):
    driver_obj = await Driver.get_or_none(id=driver.id)
    if not driver_obj:
        raise HTTPException(status_code=404, detail="Driver not found")
    await driver_obj.delete()
    return driver_obj

@router.get("/", response_model=list[DriverOut])
async def list_drivers(mfo: MFO = Depends(get_current_mfo)):
    drivers = await Driver.filter(mfo_id=mfo.id).all()
    return drivers
