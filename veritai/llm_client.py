"""Gemini LLM client abstraction for VeritAI agents."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from google import genai
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class GeminiClient:
    """Thin wrapper around the `google-genai` SDK with JSON schema support."""

    def __init__(
        self,
        model: str = "gemini-2.5-pro",
        temperature: float = 0.4,
        max_output_tokens: int = 2048,
    ) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY is not set; GeminiClient will be a no-op")
            self._client = None
        else:
            self._client = genai.Client(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def generate_structured_content(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        *,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate structured JSON adhering to the provided schema.

        Returns the parsed JSON response or ``None`` if parsing fails.
        """

        if self._client is None:
            logger.warning("GeminiClient is not configured; returning no response")
            return None

        try:
            config_kwargs: Dict[str, Any] = {
                "temperature": temperature if temperature is not None else self._temperature,
                "max_output_tokens": max_output_tokens
                if max_output_tokens is not None
                else self._max_output_tokens,
            }

            if schema:
                config_kwargs["response_mime_type"] = "application/json"
                config_kwargs["response_schema"] = self._to_schema(schema)

            response = self._client.responses.generate(
                model=self._model,
                contents=[prompt],
                config=genai_types.GenerateContentConfig(**config_kwargs),
            )
        except Exception:  # pragma: no cover - network/runtime failures
            logger.exception("Gemini content generation failed")
            return None

        text = getattr(response, "output_text", None)
        if not text:
            logger.warning("Gemini response missing output text")
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:  # pragma: no cover - unexpected model output
            logger.exception("Failed to parse Gemini response as JSON")
            return None

    @staticmethod
    def _to_schema(schema_dict: Dict[str, Any]) -> genai_types.Schema:
        """Convert a JSON schema dictionary into the SDK Schema object."""
        if isinstance(schema_dict, genai_types.Schema):
            return schema_dict

        # The Schema dataclass expects native Python structures. Using recursion
        # via json ensures complex nested structures remain compatible.
        payload = json.loads(json.dumps(schema_dict))
        return genai_types.Schema(**payload)

