"""
Brain Factory for creating and managing LLM backends.

This is the central component that enables brain swapping.
"""

from typing import Dict, Any, Optional
from .base_backend import BaseBrainBackend
from .lm_studio_backend import LMStudioBackend
from .ollama_backend import OllamaBackend
from .groq_backend import GroqBackend
from .kobold_backend import KoboldBackend


class BrainFactory:
    """Factory for creating and managing brain backends"""
    
    BACKENDS = {
        'kobold': KoboldBackend,
        'lm_studio': LMStudioBackend,
        'ollama': OllamaBackend,
        'groq': GroqBackend,
    }

    LOCAL_BACKENDS = frozenset({'kobold', 'lm_studio', 'ollama'})
    
    # Optional backends (imported only if packages available)
    _OPTIONAL_BACKENDS = {
        'claude': ('claude_backend', 'ClaudeBackend'),
        'openai': ('openai_backend', 'OpenAIBackend'),
        'venice': ('venice_backend', 'VeniceBackend'),
        'gemini': ('gemini_backend', 'GeminiBackend'),
    }
    
    @classmethod
    def _register_optional_backends(cls):
        """Register optional backends if their dependencies are available"""
        for backend_name, (module_name, class_name) in cls._OPTIONAL_BACKENDS.items():
            if backend_name not in cls.BACKENDS:
                try:
                    # Try to import the backend
                    module = __import__(
                        f'modules.brain_backends.{module_name}',
                        fromlist=[class_name]
                    )
                    backend_class = getattr(module, class_name)
                    cls.BACKENDS[backend_name] = backend_class
                except (ImportError, AttributeError):
                    # Backend not available - that's OK
                    pass
    
    @classmethod
    def create_backend(
        cls, 
        backend_type: str, 
        config: Dict[str, Any]
    ) -> Optional[BaseBrainBackend]:
        """Create a brain backend of the specified type.
        
        Args:
            backend_type: Type of backend ('lm_studio', 'ollama', 'claude', 'openai')
            config: Configuration dictionary for the backend
            
        Returns:
            BaseBrainBackend instance or None if creation failed
            
        Raises:
            ValueError: If backend_type is unknown
        """
        # Ensure optional backends are registered
        cls._register_optional_backends()
        
        if backend_type not in cls.BACKENDS:
            available = ', '.join(cls.BACKENDS.keys())
            raise ValueError(
                f"Unknown backend type: {backend_type}. Available: {available}"
            )
            
        backend_class = cls.BACKENDS[backend_type]
        try:
            backend_config = config.copy()
            backend_config['name'] = backend_type
            backend_config['is_local'] = backend_type in cls.LOCAL_BACKENDS
            
            return backend_class(backend_config)
        except Exception as e:
            print(f"[ERROR] Failed to create {backend_type} backend: {e}")
            return None
    
    @classmethod
    def test_all_backends(cls, full_config: Dict[str, Any]) -> Dict[str, tuple]:
        """Test all configured backends.
        
        Args:
            full_config: Full configuration dictionary with backend configs
            
        Returns:
            Dictionary mapping backend name to (success: bool, message: str)
        """
        # Ensure optional backends are registered
        cls._register_optional_backends()
        
        results = {}
        
        for backend_type in cls.BACKENDS.keys():
            if backend_type in full_config:
                try:
                    backend = cls.create_backend(backend_type, full_config[backend_type])
                    if backend:
                        results[backend_type] = backend.test_connection()
                    else:
                        results[backend_type] = (False, f"Failed to create {backend_type} backend")
                except Exception as e:
                    results[backend_type] = (False, f"Error testing {backend_type}: {e}")
            else:
                results[backend_type] = (False, f"No config found for {backend_type}")
                
        return results
    
    @classmethod
    def get_available_backends(cls) -> list:
        """Get list of available backend types.
        
        Returns:
            List of backend type names
        """
        cls._register_optional_backends()
        return list(cls.BACKENDS.keys())
