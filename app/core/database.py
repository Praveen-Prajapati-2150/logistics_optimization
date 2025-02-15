from tortoise import Tortoise, run_async
from app.core.config import settings

async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={
            "models": [
                "app.models.mfo",
                "app.models.vehicle",
                "app.models.driver",
                "app.models.assignment" 
            ]
        }
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
