import logging
from typing import Union
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import mfo, vehicle, driver  # Import the routers
from app.core.config import settings  # Import settings
from app.core.database import init_db, close_db  # Import database functions

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

app.include_router(mfo.router, prefix="/api/mfo", tags=["MFO"])  # Include the MFO router
app.include_router(vehicle.router, prefix="/api/vehicles", tags=["Vehicles"])  # Include the vehicle router
app.include_router(driver.router, prefix="/api/drivers", tags=["Drivers"])  # Include the driver router

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



