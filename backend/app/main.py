from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models.database import init_db
from app.modules.companies import router as companies_router
from app.modules.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Automatically initialize tables in database on startup
    await init_db()
    yield


app = FastAPI(
    title="Vietnamese IT Job Insights API",
    description="REST API for exploring Software Engineering jobs in Vietnam from TopDev and ITviec",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers under api/v1 prefix
app.include_router(companies_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    """Simple API health check endpoint."""
    return {"status": "ok"}
