from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.modules.jobs.models import (
    JobCreate,
    JobResponse,
    JobFilterParams,
    Seniority,
    RemotePolicy,
    EmploymentType,
    JobSemanticSearchResponse,
    ChatRequest,
)
from app.modules.jobs.views import JobViews


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    title: Optional[str] = Query(default=None),
    seniority: Optional[Seniority] = Query(default=None),
    remote_policy: Optional[RemotePolicy] = Query(default=None),
    employment_type: Optional[EmploymentType] = Query(default=None),
    min_salary: Optional[float] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve filtered job postings with pagination."""
    filters = JobFilterParams(
        title=title,
        seniority=seniority,
        remote_policy=remote_policy,
        employment_type=employment_type,
        min_salary=min_salary,
    )
    return await JobViews.list_jobs(db, limit=limit, offset=offset, filters=filters)


@router.get("/search", response_model=List[JobSemanticSearchResponse])
async def search_jobs(
    q: str = Query(..., description="Query string for semantic search"),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Semantic similarity search for job postings using pgvector."""
    return await JobViews.search_jobs_semantically(db, query=q, limit=limit)


@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """Retrieve IT job market trend statistics with caching."""
    return await JobViews.get_analytics_overview(db)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Fetch a specific job posting details by ID."""
    return await JobViews.get_job(db, job_id)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def post_job(job_in: JobCreate, db: AsyncSession = Depends(get_db)):
    """Publish a new job posting or update it if already registered."""
    return await JobViews.post_job(db, job_in)


@router.post("/chat")
async def chat_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    RAG virtual assistant chat endpoint.
    Streams model response with retrieved jobs context.
    """
    history = request.history or []
    return StreamingResponse(
        JobViews.stream_chat(db, query=request.message, history=history),
        media_type="text/event-stream",
    )
