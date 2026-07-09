"""LM Studio integration using OpenAI-compatible API.

LM Studio provides an OpenAI-compatible API endpoint at http://localhost:1234/v1
This module provides conversational prompt functionality using the OpenAI client.
"""
from typing import List, Dict
from openai import OpenAI


def get_client(base_url: str = "http://localhost:1234/v1", api_key: str = "lm-studio"):
    """Get an OpenAI client configured for LM Studio.
    
    Args:
        base_url: LM Studio API endpoint (default: http://localhost:1234/v1)
        api_key: API key (LM Studio doesn't require a real key)
        
    Returns:
        OpenAI client configured for LM Studio
    """
    return OpenAI(
        base_url=base_url,
        api_key=api_key  # LM Studio doesn't require a real API key
    )


def conversational_prompt(
    messages: List[Dict[str, str]],
    system_prompt: str = "You are a helpful conversational assistant. Respond in a short, concise, friendly manner.",
    model: str = "local-model",
    base_url: str = "http://localhost:1234/v1",
) -> str:
    """
    Send a conversational prompt to LM Studio using OpenAI-compatible API.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        system_prompt: Optional system prompt to set context
        model: The model identifier (LM Studio uses "local-model" or specific model name)
        base_url: LM Studio API endpoint

    Returns:
        str: The model's response
    """
    try:
        client = get_client(base_url=base_url)
        
        # Add system prompt as first message if not already present
        if not messages or messages[0].get("role") != "system":
            full_messages = [{"role": "system", "content": system_prompt}, *messages]
        else:
            full_messages = messages

        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=0.7,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Error in LM Studio conversational prompt: {str(e)}")


def test_connection(base_url: str = "http://localhost:1234/v1") -> bool:
    """Test if LM Studio is running and accessible.
    
    Args:
        base_url: LM Studio API endpoint
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_client(base_url=base_url)
        # Try to list models as a connection test
        models = client.models.list()
        return True
    except Exception:
        return False
