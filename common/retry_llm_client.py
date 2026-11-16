"""LiteLLM client that retries rate-limited requests with exponential backoff.

Pass an instance to LiteLlm so every model call made by the agent is retried:

    LiteLlm(model="groq/openai/gpt-oss-120b", llm_client=RetryingLiteLLMClient())
"""

import asyncio
import logging
import random
from typing import Any

import litellm
from google.adk.models.lite_llm import LiteLLMClient

logger = logging.getLogger(__name__)


class RetryingLiteLLMClient(LiteLLMClient):
    """Retries litellm.RateLimitError (HTTP 429) with exponential backoff and full jitter.

    The wait before retry n (0-based) is a random value between 0 and
    min(max_delay, base_delay * 2**n). If the provider sends a Retry-After
    header, that wait is used instead (plus up to 1s of jitter), since retrying
    sooner is guaranteed to fail again.
    """

    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def acompletion(self, model: Any, messages: Any, tools: Any, **kwargs: Any):
        for attempt in range(self.max_retries + 1):
            try:
                return await super().acompletion(
                    model=model, messages=messages, tools=tools, **kwargs
                )
            except litellm.RateLimitError as e:
                if attempt == self.max_retries:
                    raise
                delay = self._delay(attempt, e)
                logger.warning(
                    "Rate limited by %s (attempt %d/%d); retrying in %.1fs",
                    model, attempt + 1, self.max_retries, delay,
                )
                await asyncio.sleep(delay)

    def _delay(self, attempt: int, error: litellm.RateLimitError) -> float:
        retry_after = _retry_after_seconds(error)
        if retry_after is not None:
            return retry_after + random.uniform(0, 1)
        return random.uniform(0, min(self.max_delay, self.base_delay * 2**attempt))


def _retry_after_seconds(error: litellm.RateLimitError) -> float | None:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None) or {}
    try:
        return float(headers.get("retry-after"))
    except (TypeError, ValueError):
        return None
