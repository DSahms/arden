"""
Google Gemini backend implementation.
"""

import os
from typing import Dict, Any, Optional, List

from .base_backend import BaseBrainBackend


class GeminiBackend(BaseBrainBackend):
    """Google Gemini API backend"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_name = config.get("model", "gemini-2.0-flash")

        api_key = config.get("api_key") or os.getenv("GEMINI_API_KEY") or os.getenv(
            "GOOGLE_API_KEY"
        )
        if not api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY or GOOGLE_API_KEY env var"
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            self._genai = genai
            self.model = genai.GenerativeModel(self.model_name)
        except ImportError:
            raise ImportError(
                "google-generativeai package required. "
                "Install with: pip install google-generativeai"
            )

    def _build_prompt(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        parts = []
        if system_prompt:
            parts.append(f"System:\n{system_prompt}\n")
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user").capitalize()
                parts.append(f"{role}: {msg.get('content', '')}\n")
        parts.append(f"User: {user_message}\nAssistant:")
        return "\n".join(parts)

    def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        try:
            prompt = self._build_prompt(system_prompt, user_message, conversation_history)
            response = self.model.generate_content(prompt)
            return response.text or ""
        except Exception as e:
            return f"Gemini API error: {str(e)}"

    def is_available(self) -> bool:
        try:
            response = self.model.generate_content("Reply with: ok")
            return bool(response.text)
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, str]:
        return {
            "backend": "Gemini",
            "type": "Cloud API",
            "model": self.model_name,
            "provider": "Google",
        }
