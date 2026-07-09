"""
KoboldCpp backend implementation.

OpenAI-compatible local LLM server (llama.cpp, CUDA 11 builds for Maxwell/Pascal).
"""

import requests
from .base_backend import BaseBrainBackend
from typing import Callable, Dict, Any, Optional, List
import json


class KoboldBackend(BaseBrainBackend):
    """KoboldCpp backend (OpenAI-compatible /v1/chat/completions)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://127.0.0.1:5001/v1")
        self.model = config.get("model", "local-model")
        self.timeout = config.get("timeout", 120)

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

            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
                timeout=self.timeout,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            return f"KoboldCpp API error: {response.status_code} - {response.text}"

        except requests.exceptions.Timeout:
            return "KoboldCpp timeout - response took too long"
        except requests.exceptions.ConnectionError:
            return "KoboldCpp connection error - is the server running on port 5001?"
        except Exception as e:
            return f"KoboldCpp error: {str(e)}"

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
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": True,
                },
                timeout=self.timeout,
                stream=True,
            )
            if response.status_code != 200:
                return f"KoboldCpp API error: {response.status_code} - {response.text}"

            parts: list[str] = []
            for raw in response.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data: "):
                    continue
                payload = raw[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta", {}).get("content")
                if delta:
                    parts.append(delta)
                    if on_chunk:
                        on_chunk(delta)
            return "".join(parts)
        except requests.exceptions.Timeout:
            return "KoboldCpp timeout - response took too long"
        except requests.exceptions.ConnectionError:
            return "KoboldCpp connection error - is the server running on port 5001?"
        except Exception as e:
            return f"KoboldCpp error: {str(e)}"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, str]:
        return {
            "backend": "KoboldCpp",
            "type": "Local",
            "model": self.model,
            "url": self.base_url,
        }
