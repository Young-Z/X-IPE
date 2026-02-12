"""
FEATURE-025-C: KB Manager Skill

LLMService: Generic wrapper around DashScope Generation API for text completion.
Reusable by other features needing LLM capabilities.
"""
import os

import dashscope
from dashscope import Generation

from x_ipe.tracing import x_ipe_tracing


class LLMService:
    """Generic LLM wrapper using DashScope Generation API (Qwen models)."""

    DEFAULT_MODEL = "qwen-turbo"
    DEFAULT_MAX_TOKENS = 2000

    def __init__(self, api_key=None, model=None, max_tokens=None):
        self.api_key = api_key or os.environ.get('DASHSCOPE_API_KEY')
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

    @x_ipe_tracing()
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    @x_ipe_tracing()
    def complete(self, prompt: str, system: str = "") -> str:
        """Call LLM and return text response.

        Args:
            prompt: User prompt text
            system: Optional system prompt

        Returns:
            Generated text response

        Raises:
            RuntimeError: If API key not set or API call fails
        """
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not configured")

        dashscope.api_key = self.api_key

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = Generation.call(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error ({response.status_code}): {response.message}"
            )

        return response.output.text
