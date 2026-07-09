"""
PersonaLock LLM Inference Layer
Supports: LM Studio, OpenAI, Anthropic, Groq, Together, Ollama
Swap providers by changing LLM_PROVIDER in .env
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Config from environment
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "lmstudio").lower()
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "not-needed")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))


def get_completion(
    user_message: str,
    system_prompt: str,
    conversation_history: Optional[list] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Get a completion from the configured LLM provider.
    
    Args:
        user_message: The current user input
        system_prompt: Personality/context instructions
        conversation_history: Optional list of {"role": "user"|"assistant", "content": "..."}
        max_tokens: Override default max tokens
        temperature: Override default temperature
    
    Returns:
        The assistant's response text
    """
    max_tokens = max_tokens or LLM_MAX_TOKENS
    temperature = temperature or LLM_TEMPERATURE
    
    if LLM_PROVIDER == "anthropic":
        return _anthropic_completion(user_message, system_prompt, conversation_history, max_tokens, temperature)
    else:
        # OpenAI-compatible: lmstudio, openai, groq, together, ollama
        return _openai_compatible_completion(user_message, system_prompt, conversation_history, max_tokens, temperature)


def _openai_compatible_completion(
    user_message: str,
    system_prompt: str,
    conversation_history: Optional[list],
    max_tokens: int,
    temperature: float
) -> str:
    """Works with LM Studio, OpenAI, Groq, Together, Ollama"""
    from openai import OpenAI
    
    # Set base URL based on provider
    if LLM_PROVIDER == "openai":
        client = OpenAI(api_key=LLM_API_KEY)
    elif LLM_PROVIDER == "groq":
        client = OpenAI(api_key=LLM_API_KEY, base_url="https://api.groq.com/openai/v1")
    elif LLM_PROVIDER == "together":
        client = OpenAI(api_key=LLM_API_KEY, base_url="https://api.together.xyz/v1")
    elif LLM_PROVIDER == "ollama":
        client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    else:
        # lmstudio or custom
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)
    
    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return response.choices[0].message.content


def _anthropic_completion(
    user_message: str,
    system_prompt: str,
    conversation_history: Optional[list],
    max_tokens: int,
    temperature: float
) -> str:
    """Anthropic has a slightly different API"""
    from anthropic import Anthropic
    
    client = Anthropic(api_key=LLM_API_KEY)
    
    # Build messages (Anthropic doesn't include system in messages array)
    messages = []
    
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_message})
    
    response = client.messages.create(
        model=LLM_MODEL,
        system=system_prompt,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return response.content[0].text


# Quick test
if __name__ == "__main__":
    print(f"Provider: {LLM_PROVIDER}")
    print(f"Model: {LLM_MODEL}")
    print(f"Base URL: {LLM_API_BASE}")
    print("-" * 40)
    
    response = get_completion(
        user_message="Hello! What's your name?",
        system_prompt="You are a friendly assistant named Ada. Keep responses brief."
    )
    print(f"Response: {response}")
