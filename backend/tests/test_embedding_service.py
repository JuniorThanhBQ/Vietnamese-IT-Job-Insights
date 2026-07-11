import sys
import os
import pytest
from unittest.mock import patch, AsyncMock
import httpx

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.config import settings
from app.modules.jobs.embedding_service import GeminiEmbeddingService


@pytest.mark.anyio
async def test_key_rotation_on_failure():
    """Verify that GeminiEmbeddingService rotates keys when hitting rate limits (429)."""
    original_keys = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = "key_one, key_two"

    service = GeminiEmbeddingService()
    assert service._keys == ["key_one", "key_two"]
    assert service._current_key_idx == 0

    response_429 = httpx.Response(429, text="Too Many Requests")
    response_200 = httpx.Response(200, json={"embedding": {"values": [0.2] * 768}})

    mock_post = AsyncMock()
    mock_post.side_effect = [response_429, response_200]

    with patch("httpx.AsyncClient.post", mock_post):
        vector = await service.get_embedding("test query text")

        assert len(vector) == 768
        assert vector[0] == 0.2
        assert service._current_key_idx == 1
        assert mock_post.call_count == 2

        first_call_url = mock_post.call_args_list[0][0][0]
        assert "key=key_one" in first_call_url

        second_call_url = mock_post.call_args_list[1][0][0]
        assert "key=key_two" in second_call_url

    settings.GEMINI_API_KEY = original_keys
