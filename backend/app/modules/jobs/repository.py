# pylint: disable=not-callable
from uuid import UUID
from datetime import datetime
from typing import Sequence, Optional
from sqlalchemy import select, and_, case, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_models import Job, JobEmbedding, Company
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

    @staticmethod
    async def upsert_embedding(
        db: AsyncSession, job_id: UUID, embedding_vector: list[float]
    ) -> JobEmbedding:
        """Upsert a job embedding vector."""
        result = await db.execute(
            select(JobEmbedding).where(JobEmbedding.job_id == job_id)
        )
        db_embedding = result.scalar_one_or_none()
        if db_embedding:
            db_embedding.embedding = embedding_vector
            db_embedding.updated_date = datetime.utcnow()
        else:
            db_embedding = JobEmbedding(
                job_id=job_id,
                embedding=embedding_vector,
                created_date=datetime.utcnow(),
                updated_date=datetime.utcnow(),
            )
            db.add(db_embedding)
        await db.commit()
        return db_embedding

    @staticmethod
    async def search_similar_jobs(
        db: AsyncSession, query_vector: list[float], limit: int = 10
    ) -> Sequence[tuple[Job, float]]:
        """
        Perform a semantic similarity search using pgvector cosine distance.
        Returns a sequence of tuples containing the Job and its similarity score.
        """
        distance_expr = JobEmbedding.embedding.cosine_distance(query_vector)
        stmt = (
            select(Job, distance_expr.label("distance"))
            .join(JobEmbedding, Job.id == JobEmbedding.job_id)
            .options(joinedload(Job.company))
            .where(Job.is_active)
            .order_by("distance")
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [(row[0], 1.0 - float(row[1])) for row in rows]

    @staticmethod
    async def get_salary_trends_by_seniority(db: AsyncSession) -> list[dict]:
        """Calculate average salary ranges grouped by seniority."""
        min_vnd = case(
            (Job.salary_currency == "USD", Job.salary_min * 25000),
            else_=Job.salary_min,
        )
        max_vnd = case(
            (Job.salary_currency == "USD", Job.salary_max * 25000),
            else_=Job.salary_max,
        )
        stmt = (
            select(
                Job.seniority,
                func.avg(min_vnd).label("avg_min_vnd"),
                func.avg(max_vnd).label("avg_max_vnd"),
                func.count(Job.id).label("job_count"),
            )
            .where(
                Job.is_active,
                Job.salary_min.is_not(None),
                Job.salary_max.is_not(None),
            )
            .group_by(Job.seniority)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "seniority": row[0],
                "avg_min_vnd": float(row[1]) if row[1] else 0.0,
                "avg_max_vnd": float(row[2]) if row[2] else 0.0,
                "job_count": int(row[3]),
            }
            for row in rows
        ]

    @staticmethod
    async def get_remote_policy_distribution(db: AsyncSession) -> dict[str, int]:
        """Count occurrences of remote work policies."""
        stmt = (
            select(Job.remote_policy, func.count(Job.id).label("job_count"))
            .where(Job.is_active)
            .group_by(Job.remote_policy)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return {row[0]: int(row[1]) for row in rows}

    @staticmethod
    async def get_location_distribution(db: AsyncSession) -> dict[str, int]:
        """Group and count jobs by major Vietnamese cities/regions."""
        location_case = case(
            (
                Company.address.ilike("%Hồ Chí Minh%")
                | Company.address.ilike("%HCM%")
                | Company.address.ilike("%HCMC%"),
                "Hồ Chí Minh",
            ),
            (
                Company.address.ilike("%Hà Nội%") | Company.address.ilike("%Ha Noi%"),
                "Hà Nội",
            ),
            (
                Company.address.ilike("%Đà Nẵng%") | Company.address.ilike("%Da Nang%"),
                "Đà Nẵng",
            ),
            else_="Other",
        )
        stmt = (
            select(
                location_case.label("location"),
                func.count(Job.id).label("job_count"),
            )
            .join(Company, Job.company_id == Company.id)
            .where(Job.is_active)
            .group_by(location_case)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return {row[0]: int(row[1]) for row in rows}

    @staticmethod
    async def get_tech_stack_demand(
        db: AsyncSession, keywords: list[str]
    ) -> dict[str, int]:
        """Count occurrences of technical stack keywords in a single table scan query."""
        if not keywords:
            return {}

        select_exprs = []
        for kw in keywords:
            kw_cond = (
                Job.title.ilike(f"%{kw}%")
                | Job.description.ilike(f"%{kw}%")
                | Job.requirements.ilike(f"%{kw}%")
            )
            select_exprs.append(func.sum(case((kw_cond, 1), else_=0)).label(kw.lower()))

        stmt = select(*select_exprs).where(Job.is_active)
        result = await db.execute(stmt)
        row = result.first()

        stats = {}
        if row:
            for idx, kw in enumerate(keywords):
                stats[kw] = int(row[idx]) if row[idx] is not None else 0
        return stats
