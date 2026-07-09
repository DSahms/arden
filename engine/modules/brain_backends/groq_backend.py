"""
Groq backend implementation.

Cloud API backend for Groq's LLMs (Llama 3.3, Mixtral, etc).
Groq's API is OpenAI-compatible.
"""

from .base_backend import BaseBrainBackend
from typing import Callable, Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()


class GroqBackend(BaseBrainBackend):
    """Groq API backend - OpenAI-compatible interface to Groq's fast inference"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Groq backend.
        
        Args:
            config: Configuration with model and api_key
                   base_url defaults to https://api.groq.com/openai/v1
                   model defaults to llama-3.3-70b-versatile
        """
        super().__init__(config)
        
        # Default model and base URL for Groq
        self.model = config.get('model', 'llama-3.3-70b-versatile')
        self.base_url = config.get('base_url', 'https://api.groq.com/openai/v1')
        
        # Get API key from config or environment
        api_key = os.getenv("GROQ_API_KEY") or config.get("api_key")
        if not api_key:
            raise ValueError(
                "Groq API key required. Set in config or GROQ_API_KEY env var"
            )
        
        # Import here to avoid hard dependency
        try:
            from openai import OpenAI
            # Use Groq's OpenAI-compatible endpoint
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
                timeout=60.0,
            )
        except ImportError:
            raise ImportError(
                "openai package required for Groq backend. "
                "Install with: pip install openai"
            )
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Groq API.
        
        Args:
            system_prompt: System prompt with personality and memory
            user_message: Current user message
            conversation_history: Previous conversation messages
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
                
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            err = str(e).lower()
            if "invalid api key" in err or "401" in err:
                raise ValueError(
                    "Groq API key is invalid. Get a new key at console.groq.com"
                ) from e
            return f"Groq API error: {str(e)}"

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
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    parts.append(delta)
                    if on_chunk:
                        on_chunk(delta)
            return "".join(parts)
        except Exception as e:
            err = str(e).lower()
            if "invalid api key" in err or "401" in err:
                raise ValueError(
                    "Groq API key is invalid. Get a new key at console.groq.com"
                ) from e
            return f"Groq API error: {str(e)}"

    def is_available(self) -> bool:
        """Groq is available if the client was created (key present at init)."""
        return self.client is not None
    
    def get_model_info(self) -> Dict[str, str]:
        """Get Groq model information.
        
        Returns:
            Dictionary with backend details
        """
        return {
            "backend": "Groq",
            "type": "Cloud API",
            "model": self.model,
            "provider": "Groq"
        }
