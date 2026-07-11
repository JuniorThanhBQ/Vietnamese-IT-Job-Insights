import json
from uuid import UUID
from typing import List, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.jobs.models import (
    JobCreate,
    JobResponse,
    JobFilterParams,
    JobSemanticSearchResponse,
    ChatMessage,
)
from app.modules.jobs.services import JobService
from app.modules.jobs.rag_service import GeminiChatService


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

    @staticmethod
    async def search_jobs_semantically(
        db: AsyncSession, query: str, limit: int
    ) -> List[JobSemanticSearchResponse]:
        """Fetch semantically similar jobs and return serialized responses with scores."""
        results = await JobService.search_jobs_semantically(db, query, limit)
        return [
            JobSemanticSearchResponse(
                job=JobResponse.model_validate(job), similarity_score=score
            )
            for job, score in results
        ]

    @staticmethod
    async def stream_chat(
        db: AsyncSession, query: str, history: List[ChatMessage]
    ) -> AsyncGenerator[str, None]:
        """Expose chat streaming generator and format as SSE data lines."""
        chat_service = GeminiChatService()
        async for chunk in chat_service.stream_chat(db, query, history):
            yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
