"""
Ollama backend implementation.

Local LLM server for running open-source models.
"""

import requests
from .base_backend import BaseBrainBackend
from typing import Dict, Any, Optional, List


class OllamaBackend(BaseBrainBackend):
    """Ollama backend for local models"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Ollama backend.
        
        Args:
            config: Configuration with base_url, model, and timeout
        """
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.1:8b')
        self.timeout = config.get('timeout', 60)  # Ollama can be slower
        
    def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Ollama API.
        
        Args:
            system_prompt: System prompt with personality and memory
            user_message: Current user message
            conversation_history: Previous conversation messages
            
        Returns:
            Generated response text
        """
        try:
            # Build prompt from system + conversation + user message
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System: {system_prompt}\n\n"
                
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    full_prompt += f"{role.title()}: {content}\n"
                    
            full_prompt += f"User: {user_message}\nAssistant:"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from Ollama')
            else:
                return f"Ollama API error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Ollama timeout - response took too long (try a smaller model)"
        except requests.exceptions.ConnectionError:
            return "Ollama connection error - is the server running? (try 'ollama serve')"
        except Exception as e:
            return f"Ollama error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available.
        
        Returns:
            True if Ollama server is responding and model exists
        """
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
                
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            return any(self.model in name for name in model_names)
            
        except:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get Ollama model information.
        
        Returns:
            Dictionary with backend details
        """
        return {
            "backend": "Ollama",
            "type": "Local",
            "model": self.model,
            "url": self.base_url
        }
