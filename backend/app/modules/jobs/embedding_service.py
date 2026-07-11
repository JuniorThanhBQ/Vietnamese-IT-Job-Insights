# pylint: disable=duplicate-code
"""
Service for generating text embeddings using the Gemini REST API.
"""

import httpx
from loguru import logger
from app.config import settings


# pylint: disable=too-few-public-methods
class GeminiEmbeddingService:
    """
    Service to generate text embeddings using Gemini API with API key rotation.
    """

    def __init__(self):
        raw_keys = settings.GEMINI_API_KEY.replace(";", ",")
        self._keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        self._current_key_idx = 0

    def _rotate_key(self) -> None:
        """Rotate to the next API key in the list."""
        if not self._keys:
            return
        self._current_key_idx = (self._current_key_idx + 1) % len(self._keys)
        logger.info(f"Rotated to Gemini API key index: {self._current_key_idx}")

    async def get_embedding(self, text: str) -> list[float]:
        """
        Generate a 768-dimensional embedding vector for the given text.
        Rotates through keys on failure (e.g. rate limit 429).
        """
        if not self._keys:
            raise ValueError(
                "GEMINI_API_KEY is not set or empty in environment settings."
            )

        cleaned_text = text.strip()[:10000]
        max_attempts = len(self._keys) * 2

        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                api_key = self._keys[self._current_key_idx]
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-embedding-001:embedContent?key={api_key}"
                )
                payload = {
                    "model": "models/gemini-embedding-001",
                    "content": {"parts": [{"text": cleaned_text}]},
                    "outputDimensionality": 768,
                }

                try:
                    response = await client.post(url, json=payload, timeout=30.0)
                    if response.status_code == 200:
                        data = response.json()
                        values = data["embedding"]["values"]
                        if len(values) != 768:
                            raise ValueError(
                                f"Unexpected embedding dimension: {len(values)} (expected 768)"
                            )
                        return values

                    logger.warning(
                        f"Gemini API request failed (attempt {attempt + 1}/{max_attempts}) "
                        f"with status {response.status_code}: {response.text}"
                    )
                    self._rotate_key()

                except httpx.RequestError as exc:
                    logger.error(
                        f"HTTP Request error on Gemini API "
                        f"(attempt {attempt + 1}/{max_attempts}): {exc}"
                    )
                    self._rotate_key()

        raise RuntimeError(
            "Failed to generate embedding: "
            "all available Gemini API keys were exhausted or returned errors."
        )
