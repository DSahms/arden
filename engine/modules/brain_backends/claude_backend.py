"""
Claude (Anthropic) backend implementation.

Cloud API backend for Claude models.
"""

from .base_backend import BaseBrainBackend
from typing import Dict, Any, Optional, List
import os


class ClaudeBackend(BaseBrainBackend):
    """Claude API backend"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Claude backend.
        
        Args:
            config: Configuration with model and api_key
        """
        super().__init__(config)
        self.model = config.get('model', 'claude-3-sonnet-20240229')
        
        # Get API key from config or environment
        api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "Claude API key required. Set in config or ANTHROPIC_API_KEY env var"
            )
        
        # Import here to avoid hard dependency
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required for Claude backend. "
                "Install with: pip install anthropic"
            )
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Claude API.
        
        Args:
            system_prompt: System prompt with personality and memory
            user_message: Current user message
            conversation_history: Previous conversation messages
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
                
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Claude API error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Claude API is available.
        
        Returns:
            True if Claude API can be accessed
        """
        try:
            # Test with a minimal request
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get Claude model information.
        
        Returns:
            Dictionary with backend details
        """
        return {
            "backend": "Claude",
            "type": "Cloud API",
            "model": self.model,
            "provider": "Anthropic"
        }
