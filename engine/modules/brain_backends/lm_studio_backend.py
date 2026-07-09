"""
LM Studio backend implementation.

Local LLM server compatible with OpenAI API.
"""

import requests
from .base_backend import BaseBrainBackend
from typing import Dict, Any, Optional, List


class LMStudioBackend(BaseBrainBackend):
    """LM Studio backend (OpenAI-compatible local server)"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LM Studio backend.
        
        Args:
            config: Configuration with base_url, model, and timeout
        """
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:1234/v1')
        self.model = config.get('model', 'local-model')
        self.timeout = config.get('timeout', 30)
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using LM Studio API.
        
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
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"LM Studio API error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "LM Studio timeout - response took too long"
        except requests.exceptions.ConnectionError:
            return "LM Studio connection error - is the server running?"
        except Exception as e:
            return f"LM Studio error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if LM Studio is running and accessible.
        
        Returns:
            True if LM Studio server is responding
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get LM Studio model information.
        
        Returns:
            Dictionary with backend details
        """
        return {
            "backend": "LM Studio",
            "type": "Local",
            "model": self.model,
            "url": self.base_url
        }
