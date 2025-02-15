from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Initializing database...")
    await init_db()  # Initialize Tortoise ORM
    yield  # This allows the app to continue running
    print("Shutting down: Closing database...")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
