# pylint: disable=duplicate-code
import json
from typing import AsyncGenerator, Sequence
import httpx

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config import settings
from app.models.db_models import Job
from app.modules.jobs.services import JobService
from app.modules.jobs.models import ChatMessage


class GeminiChatService:
    """
    RAG Assistant Service using LangChain messages and Gemini API with key rotation.
    Provides streaming responses for user queries augmented with job metadata.
    """

    def __init__(self):
        self._keys = [
            k.strip() for k in settings.GEMINI_API_KEY.split(",") if k.strip()
        ]
        self._current_key_idx = 0

    def _rotate_key(self) -> None:
        """Rotate to the next API key in the list."""
        if not self._keys:
            return
        self._current_key_idx = (self._current_key_idx + 1) % len(self._keys)
        logger.info(
            f"Rotated to Gemini API key index for chat: {self._current_key_idx}"
        )

    def _format_jobs_context(self, jobs: Sequence[Job]) -> str:
        """Format retrieved job records into structured markdown context."""
        if not jobs:
            return "No matching jobs found in the database."

        context_parts = []
        for idx, job in enumerate(jobs, 1):
            salary_info = (
                f"{job.salary_min} - {job.salary_max} {job.salary_currency}"
                if job.salary_min and job.salary_max
                else job.salary_raw or "Thương lượng"
            )
            part = (
                f"--- Job #{idx} ---\n"
                f"Job ID: {job.id}\n"
                f"Title: {job.title}\n"
                f"Location: {job.company.address or 'N/A'}\n"
                f"Salary: {salary_info}\n"
                f"Seniority: {job.seniority}\n"
                f"Remote Policy: {job.remote_policy}\n"
                f"Employment Type: {job.employment_type}\n"
                f"Description: {job.description}\n"
                f"Requirements: {job.requirements or 'N/A'}\n"
                f"Link: {job.url}\n"
                f"----------------"
            )
            context_parts.append(part)
        return "\n\n".join(context_parts)

    # pylint: disable=too-many-locals
    async def stream_chat(
        self, db: AsyncSession, query: str, history: list[ChatMessage]
    ) -> AsyncGenerator[str, None]:
        """
        Stream generated chat response chunk-by-chunk using key rotation.
        Retrieves matching jobs, constructs RAG prompt, and calls Gemini REST.
        """
        if not self._keys:
            raise ValueError("GEMINI_API_KEY is not set or empty.")

        # Step 1: Semantic search to retrieve context jobs
        jobs_with_scores = await JobService.search_jobs_semantically(db, query, limit=5)
        retrieved_jobs = [job for job, _ in jobs_with_scores]
        jobs_context = self._format_jobs_context(retrieved_jobs)

        # Step 2: Build LangChain message structure
        system_prompt = (
            "You are a polite virtual assistant for Vietnamese Software Engineers looking for jobs.\n"
            "Answer the query ONLY using the provided job listings in the context.\n"
            "If the context does not contain enough information to answer, state clearly: "
            '"Tôi không tìm thấy công việc phù hợp trong cơ sở dữ liệu hiện tại."\n'
            "Do not hallucinate or manufacture job details (salaries, links, contact info).\n"
            "Always provide clickable markdown links from the 'Link' field of matching jobs in your answer.\n"
            "Answer in Vietnamese (or match the user's query language)."
        )
        system_message = SystemMessage(content=system_prompt)

        messages = []
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "model":
                messages.append(AIMessage(content=msg.content))

        augmented_user_content = (
            f"Context (Retrieved Jobs):\n{jobs_context}\n\n" f"User Query: {query}"
        )
        messages.append(HumanMessage(content=augmented_user_content))

        # Step 3: Serialize to Gemini REST payload format
        contents = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        system_instruction = {"parts": [{"text": system_message.content}]}

        # Step 4: Stream response with key rotation
        max_attempts = len(self._keys) * 2
        for attempt in range(max_attempts):
            api_key = self._keys[self._current_key_idx]
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:streamGenerateContent?key={api_key}&alt=sse"
            )
            payload = {
                "contents": contents,
                "systemInstruction": system_instruction,
            }

            try:
                # pylint: disable=no-member
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST", url, json=payload, timeout=60.0
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            logger.warning(
                                f"Gemini API chat failed (attempt {attempt + 1}/{max_attempts}) "
                                f"with status {response.status_code}: {error_text.decode('utf-8')}"
                            )
                            self._rotate_key()
                            continue

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                try:
                                    chunk = json.loads(data_str)
                                    candidates = chunk.get("candidates", [])
                                    if candidates:
                                        text = (
                                            candidates[0]
                                            .get("content", {})
                                            .get("parts", [{}])[0]
                                            .get("text", "")
                                        )
                                        if text:
                                            yield text
                                except json.JSONDecodeError:
                                    continue
                        return
            except httpx.RequestError as exc:
                logger.error(
                    f"HTTP Request error on Gemini API (attempt {attempt + 1}/{max_attempts}): {exc}"
                )
                self._rotate_key()

        raise RuntimeError(
            "Failed to generate chat response: all Gemini API keys were exhausted."
        )
