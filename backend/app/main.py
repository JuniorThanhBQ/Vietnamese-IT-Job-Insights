"""
Main FastAPI application entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.models.database import init_db
from app.modules.companies import router as companies_router
from app.modules.jobs import router as jobs_router
from app.admin import init_admin


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan event handler for FastAPI app.
    Initializes database tables on startup.
    """
    await init_db()
    yield


app = FastAPI(
    title="Vietnamese IT Job Insights API",
    description=(
        "REST API for exploring Software Engineering jobs "
        "in Vietnam from TopDev and ITviec"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Initialize SQLAdmin CRUD interface
init_admin(app)

# Register routers under api/v1 prefix
app.include_router(companies_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """Redirect root path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health_check():
    """Simple API health check endpoint."""
    return {"status": "ok"}
