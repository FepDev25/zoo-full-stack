import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic.config import Config
from alembic import command
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine

from app.modules.personnel.router import router as personnel_router
from app.modules.animals.router import router as animals_router

logger = logging.getLogger(__name__)

ALEMBIC_CFG = Config(str(Path(__file__).parent.parent / "alembic.ini"))


def run_alembic_upgrade():
    command.upgrade(ALEMBIC_CFG, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running database migrations...")
    try:
        await asyncio.to_thread(run_alembic_upgrade)
        logger.info("Migrations completed successfully.")
    except Exception:
        logger.error("Migration failed.", exc_info=True)
        raise
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(personnel_router, prefix=settings.API_V1_PREFIX)
app.include_router(animals_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs" if settings.DEBUG else None,
        "api_version": "v1",
        "api_prefix": settings.API_V1_PREFIX,
    }
