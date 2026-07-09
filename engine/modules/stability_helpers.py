"""
Stability helpers for PersonaLock - Simple, practical error handling

Focused on graceful degradation rather than complex recovery systems.
"""

import logging
import traceback
from typing import Callable, Any, Optional
from functools import wraps


class SimpleErrorHandler:
    """Simple, practical error handling for PersonaLock"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def safe_call(self, func: Callable, *args, 
                  fallback_value: Any = None, 
                  error_context: str = "") -> Any:
        """
        Safely call a function with error handling
        
        Args:
            func: Function to call
            fallback_value: Value to return if function fails
            error_context: Description for logging
            
        Returns:
            Function result or fallback_value on error
        """
        try:
            return func(*args)
        except Exception as e:
            context = error_context or func.__name__
            self.logger.error(f"[ERROR] {context}: {type(e).__name__} - {str(e)}")
            return fallback_value
    
    def with_retry(self, func: Callable, max_attempts: int = 3, 
                  *args, **kwargs) -> tuple[bool, Any]:
        """
        Try calling a function multiple times
        
        Returns:
            tuple: (success: bool, result: Any)
        """
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                self.logger.warning(f"[RETRY] Attempt {attempt + 1}/{max_attempts} failed: {e}")
                if attempt < max_attempts - 1:
                    import time
                    time.sleep(0.5 * (attempt + 1))  # Brief backoff
        
        self.logger.error(f"[ERROR] All {max_attempts} attempts failed: {last_error}")
        return False, None


def safe_execute(default_return=None):
    """Decorator for safe function execution with fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log if logger available
                if hasattr(args[0], 'logger'):
                    args[0].logger.error(f"[ERROR] {func.__name__}: {e}")
                else:
                    print(f"[ERROR] {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


class ImprovedWakeWordDetector:
    """Simple, effective wake word detection with fuzzy matching"""
    
    def __init__(self, wake_word: str = "ada", 
                 alternatives: list = None,
                 fuzzy_threshold: float = 0.75):
        """
        Initialize wake word detector
        
        Args:
            wake_word: Primary wake word (default: "ada")
            alternatives: List of alternative wake phrases
            fuzzy_threshold: Minimum similarity for fuzzy match (0.0-1.0)
        """
        self.wake_word = wake_word.lower()
        self.alternatives = [alt.lower() for alt in (alternatives or [])]
        self.fuzzy_threshold = fuzzy_threshold
    
    def _fuzzy_match(self, word1: str, word2: str) -> float:
        """Calculate simple similarity between two words"""
        word1, word2 = word1.lower(), word2.lower()
        
        # Exact match
        if word1 == word2:
            return 1.0
        
        # Substring match
        if word1 in word2 or word2 in word1:
            return 0.9
        
        # Character overlap (simple Jaccard similarity)
        set1, set2 = set(word1), set(word2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def detect(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Detect wake word in text
        
        Returns:
            tuple: (detected: bool, matched_phrase: Optional[str])
        """
        if not text:
            return False, None
        
        text_lower = text.lower().strip()
        
        # Check for exact primary wake word
        if self.wake_word in text_lower:
            return True, self.wake_word
        
        # Check for alternatives
        for alt in self.alternatives:
            if alt in text_lower:
                return True, alt
        
        # Fuzzy matching for wake word
        words = text_lower.split()
        for word in words:
            similarity = self._fuzzy_match(word, self.wake_word)
            if similarity >= self.fuzzy_threshold:
                return True, word
        
        return False, None
    
    def extract_command(self, text: str, wake_phrase: str) -> str:
        """Extract command after wake phrase"""
        text_lower = text.lower()
        wake_lower = wake_phrase.lower()
        
        # Find wake phrase and return text after it
        idx = text_lower.find(wake_lower)
        if idx != -1:
            return text[idx + len(wake_phrase):].strip()
        
        return text.strip()


# User-friendly error messages that match Sam's personality
USER_FRIENDLY_MESSAGES = {
    'brain_backend_failed': "I'm having trouble thinking right now. Let me try a different approach.",
    'memory_failed': "I couldn't save that, but I'm still listening.",
    'voice_failed': "I can't speak right now, but I can still respond in text.",
    'network_timeout': "That's taking too long. Let me try something else.",
    'unknown': "Something unexpected happened, but I'm still here to help."
}


def get_friendly_error_message(error_type: str = 'unknown') -> str:
    """Get a Sam-style error message"""
    return USER_FRIENDLY_MESSAGES.get(error_type, USER_FRIENDLY_MESSAGES['unknown'])
