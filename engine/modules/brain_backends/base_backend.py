"""
Abstract base class for LLM backends.

All brain backends must implement this interface to work with PersonaLock.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List, Optional


class BaseBrainBackend(ABC):
    """Abstract base class for LLM backends"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize backend with configuration.
        
        Args:
            config: Backend configuration dictionary
        """
        self.config = config
        self.name = config.get('name', 'unknown')
        self.is_local = config.get('is_local', False)
        
    @abstractmethod
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response from the LLM backend.
        
        Args:
            system_prompt: System prompt (includes personality + memory context)
            user_message: Current user message
            conversation_history: List of previous messages in format:
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                
        Returns:
            Generated response text
        """
        pass

    def supports_streaming(self) -> bool:
        """True when backend can stream tokens (Venice, Groq, etc.)."""
        return False

    def generate_response_stream(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Stream tokens when supported; returns full assembled response."""
        text = self.generate_response(system_prompt, user_message, conversation_history)
        if on_chunk and text:
            on_chunk(text)
        return text

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available and working."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model.
        
        Returns:
            Dictionary with keys: backend, type, model, and any other relevant info
        """
        pass
    
    def test_connection(self) -> tuple:
        """Test backend connection and return (success, message).
        
        Returns:
            Tuple of (bool, str) indicating success and status message
        """
        try:
            if not self.is_available():
                return False, f"{self.name} backend not available"
            
            # Simple test prompt
            response = self.generate_response(
                "You are a test assistant. Reply with exactly: 'Test successful'",
                "Test message"
            )
            
            if response and "Test successful" in response:
                return True, f"{self.name} backend working correctly"
            else:
                return False, f"{self.name} backend responded but with unexpected output"
                
        except Exception as e:
            return False, f"{self.name} backend error: {str(e)}"
