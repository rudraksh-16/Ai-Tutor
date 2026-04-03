import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

    # Fallback if ASYNC_DATABASE_URL isn't explicitly set, convert the sync URL
    if not ASYNC_DATABASE_URL and DATABASE_URL:
        ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # Auth
    ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "b4f2c0b618db0d738f71257121287c2bbedd1c3a7266a2a0914e6e660cd420af")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
