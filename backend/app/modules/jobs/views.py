from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.jobs.models import JobCreate, JobResponse, JobFilterParams
from app.modules.jobs.services import JobService


class JobViews:
    """Views layer handling payload mapping for job postings."""

    @staticmethod
    async def get_job(db: AsyncSession, job_id: UUID) -> JobResponse:
        """Fetch a job posting and return serialized schema."""
        db_job = await JobService.get_job(db, job_id)
        return JobResponse.model_validate(db_job)

    @staticmethod
    async def list_jobs(
        db: AsyncSession, limit: int, offset: int, filters: Optional[JobFilterParams]
    ) -> List[JobResponse]:
        """Fetch filtered job list and return serialized responses."""
        jobs = await JobService.list_jobs(db, limit, offset, filters)
        return [JobResponse.model_validate(j) for j in jobs]

    @staticmethod
    async def post_job(db: AsyncSession, job_in: JobCreate) -> JobResponse:
        """Create or update a job and return serialized response."""
        db_job = await JobService.post_job(db, job_in)
        return JobResponse.model_validate(db_job)
