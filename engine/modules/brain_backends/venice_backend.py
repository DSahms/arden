"""
Venice AI backend implementation.

OpenAI-compatible privacy-oriented cloud API.
"""

import os
import time
from typing import Callable, Dict, Any, Optional, List

from .base_backend import BaseBrainBackend


class VeniceBackend(BaseBrainBackend):
    """Venice AI backend (OpenAI-compatible API at api.venice.ai)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = config.get("model", "llama-3.3-70b")
        self.base_url = config.get("base_url", "https://api.venice.ai/api/v1")

        api_key = os.getenv("VENICE_API_KEY") or config.get("api_key")
        if not api_key:
            raise ValueError(
                "Venice API key required. Set in config or VENICE_API_KEY env var"
            )

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key, base_url=self.base_url, timeout=60.0)
        except ImportError:
            raise ImportError(
                "openai package required for Venice backend. "
                "Install with: pip install openai"
            )

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise self._friendly_error(e) from e

    def supports_streaming(self) -> bool:
        return True

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def generate_response_stream(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> str:
        try:
            messages = self._build_messages(system_prompt, user_message, conversation_history)
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )
            parts: list[str] = []
            deadline = time.monotonic() + 55
            for chunk in stream:
                if time.monotonic() > deadline:
                    msg = "".join(parts) or "Venice timed out — press Escape and try again."
                    if on_chunk and parts:
                        pass
                    elif on_chunk and not parts:
                        on_chunk(msg)
                    return msg
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    parts.append(delta)
                    if on_chunk:
                        on_chunk(delta)
            return "".join(parts)
        except Exception as e:
            raise self._friendly_error(e) from e

    def _friendly_error(self, exc: Exception) -> ValueError:
        err = str(exc).lower()
        if "401" in err or "403" in err or ("invalid" in err and "api key" in err):
            return ValueError(
                "Venice API key missing or invalid. Check venice.ai or Settings."
            )
        if "timeout" in err or "timed out" in err:
            return ValueError("Venice timed out. Check your internet and try again.")
        if "connection" in err or "network" in err:
            return ValueError("Could not reach Venice. Check your internet and try again.")
        return ValueError(f"Venice API error: {exc}")

    def is_available(self) -> bool:
        """Available if client was created (key present at init)."""
        return self.client is not None

    def get_model_info(self) -> Dict[str, str]:
        return {
            "backend": "Venice AI",
            "type": "Cloud API",
            "model": self.model,
            "provider": "Venice AI",
        }
