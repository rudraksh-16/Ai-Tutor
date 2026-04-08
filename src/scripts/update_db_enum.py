import asyncio
from sqlalchemy import text
from src.backend.db.database import SessionLocal

async def alter_enum():
    async with SessionLocal() as session:
        try:
            # Need to disable transaction block to alter enum in postgres
            await session.execute(text("COMMIT"))
            await session.execute(text("ALTER TYPE chapterstatus ADD VALUE IF NOT EXISTS 'generating'"))
            await session.execute(text("ALTER TYPE chapterstatus ADD VALUE IF NOT EXISTS 'failed'"))
            print("Successfully updated chapterstatus enum in the database.")
        except Exception as e:
            print(f"Error updating enum: {e}")

if __name__ == "__main__":
    asyncio.run(alter_enum())
