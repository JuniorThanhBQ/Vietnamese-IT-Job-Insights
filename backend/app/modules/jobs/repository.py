from uuid import UUID
from typing import Sequence, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Job
from app.modules.jobs.models import JobCreate, JobFilterParams


class JobRepository:
    """Repository pattern for database operations on Job objects."""

    @staticmethod
    async def get_by_id(db: AsyncSession, job_id: UUID) -> Optional[Job]:
        """Fetch a single job by its ID."""
        result = await db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_url(db: AsyncSession, url: str) -> Optional[Job]:
        """Fetch a job by its unique URL (used for change detection / crawler checks)."""
        result = await db.execute(select(Job).where(Job.url == url))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[JobFilterParams] = None,
    ) -> Sequence[Job]:
        """List active jobs with optional filtering options and pagination."""
        query = select(Job).where(Job.is_active)

        if filters:
            conditions = []
            if filters.title:
                conditions.append(Job.title.ilike(f"%{filters.title}%"))
            if filters.seniority:
                conditions.append(Job.seniority == filters.seniority.value)
            if filters.remote_policy:
                conditions.append(Job.remote_policy == filters.remote_policy.value)
            if filters.employment_type:
                conditions.append(Job.employment_type == filters.employment_type.value)
            if filters.min_salary:
                conditions.append(Job.salary_min >= filters.min_salary)

            if conditions:
                query = query.where(and_(*conditions))

        result = await db.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, job_in: JobCreate) -> Job:
        """Create a new job posting in the database."""
        db_job = Job(
            company_id=job_in.company_id,
            source_id=job_in.source_id,
            source_site=job_in.source_site,
            title=job_in.title,
            url=job_in.url,
            salary_min=job_in.salary_min,
            salary_max=job_in.salary_max,
            salary_currency=job_in.salary_currency.value
            if job_in.salary_currency
            else "VND",
            salary_raw=job_in.salary_raw,
            seniority=job_in.seniority.value if job_in.seniority else "Unknown",
            remote_policy=job_in.remote_policy.value
            if job_in.remote_policy
            else "Unknown",
            employment_type=job_in.employment_type.value
            if job_in.employment_type
            else "Unknown",
            description=job_in.description,
            requirements=job_in.requirements,
            posting_time=job_in.posting_time,
            expiry_time=job_in.expiry_time,
            raw_metadata=job_in.raw_metadata or {},
            is_active=job_in.is_active,
            content_hash=job_in.content_hash,
        )
        db.add(db_job)
        await db.commit()
        await db.refresh(db_job)
        return db_job
