from uuid import UUID
from typing import Sequence, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Job
from app.modules.companies.services import CompanyService
from app.modules.jobs.models import JobCreate, JobFilterParams
from app.modules.jobs.repository import JobRepository


class JobService:
    """Service layer managing business logic for job postings."""

    @staticmethod
    async def get_job(db: AsyncSession, job_id: UUID) -> Job:
        """Fetch a job posting by ID or raise 404."""
        job = await JobRepository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        return job

    @staticmethod
    async def list_jobs(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[JobFilterParams] = None,
    ) -> Sequence[Job]:
        """Fetch all active jobs matching optional filters."""
        return await JobRepository.list_all(db, limit, offset, filters)

    @staticmethod
    async def post_job(db: AsyncSession, job_in: JobCreate) -> Job:
        """
        Creates or updates a job posting.
        Implements SHA-256 change detection to avoid duplicate DB writes.
        """
        await CompanyService.get_company(db, job_in.company_id)

        existing_job = await JobRepository.get_by_url(db, job_in.url)

        if existing_job:
            if existing_job.content_hash == job_in.content_hash:
                return existing_job

            existing_job.title = job_in.title
            existing_job.salary_min = job_in.salary_min
            existing_job.salary_max = job_in.salary_max
            existing_job.salary_currency = (
                job_in.salary_currency.value if job_in.salary_currency else "VND"
            )
            existing_job.salary_raw = job_in.salary_raw
            existing_job.seniority = (
                job_in.seniority.value if job_in.seniority else "Unknown"
            )
            existing_job.remote_policy = (
                job_in.remote_policy.value if job_in.remote_policy else "Unknown"
            )
            existing_job.employment_type = (
                job_in.employment_type.value if job_in.employment_type else "Unknown"
            )
            existing_job.description = job_in.description
            existing_job.requirements = job_in.requirements
            existing_job.posting_time = job_in.posting_time
            existing_job.expiry_time = job_in.expiry_time
            existing_job.raw_metadata = job_in.raw_metadata or {}
            existing_job.is_active = job_in.is_active
            existing_job.content_hash = job_in.content_hash

            await db.commit()
            await db.refresh(existing_job)
            return existing_job

        return await JobRepository.create(db, job_in)
