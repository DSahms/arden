"""
OpenAI backend implementation.

Cloud API backend for OpenAI models (GPT-3.5, GPT-4, etc).
"""

from .base_backend import BaseBrainBackend
from typing import Dict, Any, Optional, List
import os


class OpenAIBackend(BaseBrainBackend):
    """OpenAI API backend"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI backend.
        
        Args:
            config: Configuration with model and api_key
        """
        super().__init__(config)
        self.model = config.get('model', 'gpt-3.5-turbo')
        
        # Get API key from config or environment
        api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set in config or OPENAI_API_KEY env var"
            )
        
        # Import here to avoid hard dependency
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "openai package required for OpenAI backend. "
                "Install with: pip install openai"
            )
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using OpenAI API.
        
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
            return f"OpenAI API error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available.
        
        Returns:
            True if OpenAI API can be accessed
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get OpenAI model information.
        
        Returns:
            Dictionary with backend details
        """
        return {
            "backend": "OpenAI",
            "type": "Cloud API",
            "model": self.model,
            "provider": "OpenAI"
        }
