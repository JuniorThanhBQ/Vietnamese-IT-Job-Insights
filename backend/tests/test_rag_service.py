import sys
import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
import json

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.config import settings
from app.modules.jobs.rag_service import GeminiChatService


class AsyncIterator:
    """Helper to mock async iteration over stream lines."""

    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)


class MockStreamContext:
    """Helper to mock async context manager for httpx client.stream."""

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.anyio
async def test_chat_service_streaming_key_rotation():
    """Test GeminiChatService streaming response and round-robin key rotation on 429."""
    original_keys = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = "key_one, key_two"

    chat_service = GeminiChatService()
    assert chat_service._keys == ["key_one", "key_two"]

    # Mock job database model
    job_mock = MagicMock()
    job_mock.id = "123"
    job_mock.title = "Test Python"
    job_mock.address = "HCM"
    job_mock.salary_min = 10
    job_mock.salary_max = 20
    job_mock.salary_currency = "VND"
    job_mock.salary_raw = "10-20M"
    job_mock.seniority = "Junior"
    job_mock.remote_policy = "Remote"
    job_mock.employment_type = "Full-time"
    job_mock.description = "Desc"
    job_mock.requirements = "Reqs"
    job_mock.url = "https://example.com/job"

    mock_jobs = [(job_mock, 0.9)]

    mock_response_429 = MagicMock(spec=httpx.Response)
    mock_response_429.status_code = 429
    mock_response_429.aread = AsyncMock(return_value=b"Rate Limit Exceeded")

    mock_response_200 = MagicMock(spec=httpx.Response)
    mock_response_200.status_code = 200

    lines = [
        "data: "
        + json.dumps({"candidates": [{"content": {"parts": [{"text": "Hello "}]}}]}),
        "data: "
        + json.dumps({"candidates": [{"content": {"parts": [{"text": "world!"}]}}]}),
    ]
    mock_response_200.aiter_lines = MagicMock(return_value=AsyncIterator(lines))

    mock_stream = MagicMock()
    mock_stream.side_effect = [
        MockStreamContext(mock_response_429),
        MockStreamContext(mock_response_200),
    ]

    with patch(
        "app.modules.jobs.services.JobService.search_jobs_semantically",
        AsyncMock(return_value=mock_jobs),
    ):
        with patch("httpx.AsyncClient.stream", mock_stream):
            db_mock = AsyncMock()

            chunks = []
            async for chunk in chat_service.stream_chat(db_mock, "Junior python", []):
                chunks.append(chunk)

            assert "".join(chunks) == "Hello world!"
            assert chat_service._current_key_idx == 1
            assert mock_stream.call_count == 2

            # Check URLs used in requests
            first_call_args = mock_stream.call_args_list[0]
            first_url = (
                first_call_args[1]["url"]
                if "url" in first_call_args[1]
                else first_call_args[0][1]
            )
            assert "key=key_one" in first_url

            second_call_args = mock_stream.call_args_list[1]
            second_url = (
                second_call_args[1]["url"]
                if "url" in second_call_args[1]
                else second_call_args[0][1]
            )
            assert "key=key_two" in second_url

    settings.GEMINI_API_KEY = original_keys
