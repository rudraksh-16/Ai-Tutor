import asyncio
import logging

from src.backend.db.database import Base, engine
import src.backend.models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def init_db() -> None:
    async with engine.begin() as conn:
        logger.info("Dropping old schema...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Recreating database schema...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Done!")

if __name__ == "__main__":
    asyncio.run(init_db())
