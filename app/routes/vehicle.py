from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models.vehicle import Vehicle
from app.models.mfo import MFO  # Import the MFO model
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut, VehiclePatch
from app.core.config import settings
import logging
from app.models.assignment import DriverVehicleAssignment  # New assignment model
from app.models.driver import Driver
from app.schemas.assignment import DriverAssignment, DriverAssignmentOut, SwitchDriver  # New assignment schemas

# Change tokenUrl to have a leading slash
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/mfo/login")

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_current_mfo(token: str = Depends(oauth2_scheme)):
    logger.info(f"Received token: {token}")
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub") or payload.get("email")
        if not email:
            logger.error(f"Token payload missing 'sub' or 'email': {payload}")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError: {e}")
        raise credentials_exception
    mfo = await MFO.get_or_none(email=email)
    if mfo is None:
        logger.error(f"No MFO found with email: {email}")
        raise credentials_exception
    logger.info(f"MFO authenticated: {mfo.id}")
    return mfo

@router.post("/", response_model=VehicleOut)
async def add_vehicle(request: Request, vehicle: VehicleCreate, mfo: MFO = Depends(get_current_mfo)):
    logger.info(f"Request body: {await request.body()}")
    logger.info(f"Adding vehicle for MFO: {mfo.id}")
    vehicle_data = vehicle.model_dump()
    vehicle_data['mfo_id'] = mfo.id
    vehicle_obj = await Vehicle.create(**vehicle_data)
    return vehicle_obj

@router.get("/", response_model=list[VehicleOut])
async def list_vehicles(current_mfo: MFO = Depends(get_current_mfo)):
    print(current_mfo)
    vehicles = await Vehicle.filter(mfo_id=current_mfo.id).all()
    return vehicles

@router.get("/{vehicle_id}/", response_model=VehicleOut)
async def get_vehicle(vehicle_id: int, current_mfo: MFO = Depends(get_current_mfo)):
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.patch("/{vehicle_id}", response_model=VehicleOut)
async def patch_vehicle(vehicle_id: int, vehicle_update: VehiclePatch, current_mfo: MFO = Depends(get_current_mfo)):
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")
    update_data = vehicle_update.model_dump(exclude_unset=True)
    if update_data:
        await vehicle.update_from_dict(update_data).save()
    return vehicle


# ------------ upper apis for driver crud operations --------------

@router.post("/{vehicle_id}/assign-driver/", response_model=DriverAssignmentOut)
async def assign_driver(
    vehicle_id: int,
    assignment: DriverAssignment,
    current_mfo: MFO = Depends(get_current_mfo)
):
    # Check vehicle exists and belongs to current MFO
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")

    # Check the driver exists
    driver = await Driver.get_or_none(id=assignment.driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Ensure the driver is not already assigned to another vehicle
    existing_assignment = await DriverVehicleAssignment.get_or_none(driver_id=assignment.driver_id, active=True)
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Driver is already assigned to a vehicle")

    # Example: if vehicle is under maintenance, allow reassigning (your business logic can be more advanced)
    if vehicle.status.lower() == "maintenance":
        # Optionally remove previous assignments for this vehicle if needed
        await DriverVehicleAssignment.filter(vehicle_id=vehicle_id).update(active=False)

    # Create the new assignment (including the shift if provided)
    assignment_obj = await DriverVehicleAssignment.create(
        vehicle_id=vehicle_id,
        driver_id=assignment.driver_id,
        shift=assignment.shift,
        active=True
    )
    return DriverAssignmentOut.from_orm(assignment_obj)

@router.patch("/{vehicle_id}/switch-driver/", response_model=DriverAssignmentOut)
async def switch_driver(
    vehicle_id: int,
    switch: SwitchDriver,
    current_mfo: MFO = Depends(get_current_mfo)
):
    # Ensure the vehicle belongs to the logged-in MFO
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")
    
    # Check the current assignment exists for old_driver
    current_assignment = await DriverVehicleAssignment.get_or_none(vehicle_id=vehicle_id, driver_id=switch.old_driver_id, active=True)
    if not current_assignment:
        raise HTTPException(status_code=404, detail="Current driver assignment not found")

    # Ensure the new driver is not already assigned
    new_driver_assignment = await DriverVehicleAssignment.get_or_none(driver_id=switch.new_driver_id, active=True)
    if new_driver_assignment:
        raise HTTPException(status_code=400, detail="New driver is already assigned to a vehicle")

    # Update the assignment – in this example, we simply update the driver_id and shift.
    current_assignment.driver_id = switch.new_driver_id
    if switch.shift is not None:
        current_assignment.shift = switch.shift
    await current_assignment.save()
    
    return DriverAssignmentOut.from_orm(current_assignment)

@router.get("/{vehicle_id}/assigned-driver/", response_model=DriverAssignmentOut)
async def get_assigned_driver(vehicle_id: int, current_mfo: MFO = Depends(get_current_mfo)):
    # Validate vehicle ownership
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")
    # Get the active driver assignment
    assignment = await DriverVehicleAssignment.get_or_none(vehicle_id=vehicle_id, active=True)
    if not assignment:
        raise HTTPException(status_code=404, detail="No active driver assignment found for this vehicle")
    return DriverAssignmentOut.from_orm(assignment)

@router.get("/{vehicle_id}/assigned-drivers/", response_model=list[DriverAssignmentOut])
async def list_assigned_drivers(vehicle_id: int, current_mfo: MFO = Depends(get_current_mfo)):
    # Validate vehicle ownership
    vehicle = await Vehicle.get_or_none(id=vehicle_id, mfo_id=current_mfo.id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")
    # Query all assignments for the vehicle
    assignments = await DriverVehicleAssignment.filter(vehicle_id=vehicle_id).all()
    return [DriverAssignmentOut.from_orm(assignment) for assignment in assignments]
