"""Simple multi-backend inference client.

Supported backends (aliases):
- lmstudio  -> http://localhost:1234/v1        (OpenAI-format)
- openai    -> https://api.openai.com/v1       (OpenAI-format)
- anthropic -> https://api.anthropic.com       (Anthropic Responses API)
- groq      -> https://api.groq.com/v1         (OpenAI-format)
- together  -> https://api.together.xyz/v1     (OpenAI-format)
- ollama    -> http://localhost:11434/v1      (OpenAI-format)

This module provides a tiny `InferenceClient` to send a prompt or
chat-style messages to any of the above backends with a single interface.

Usage example:

    from llm.inference import InferenceClient

    client = InferenceClient(backend="ollama", model="gpt-4o-mini")
    out = client.request("Say hello")
    print(out)

Notes:
- Configure API keys via environment variables named in the
  `DEFAULT_BACKENDS` mapping (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
"""

from dataclasses import dataclass
import os
import requests
from typing import Optional, List, Dict, Any


@dataclass
class BackendConfig:
    base_url: str
    api_key_env: Optional[str] = None
    fmt: str = "openai"  # 'openai' or 'anthropic'


DEFAULT_BACKENDS: Dict[str, BackendConfig] = {
    "lmstudio": BackendConfig("http://localhost:1234", api_key_env="LMSTUDIO_API_KEY", fmt="openai"),
    "openai": BackendConfig("https://api.openai.com", api_key_env="OPENAI_API_KEY", fmt="openai"),
    "anthropic": BackendConfig("https://api.anthropic.com", api_key_env="ANTHROPIC_API_KEY", fmt="anthropic"),
    "groq": BackendConfig("https://api.groq.com", api_key_env="GROQ_API_KEY", fmt="openai"),
    "together": BackendConfig("https://api.together.xyz", api_key_env="TOGETHER_API_KEY", fmt="openai"),
    "ollama": BackendConfig("http://localhost:11434", api_key_env=None, fmt="openai"),
}


class InferenceClient:
    def __init__(self, backend: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4o-mini", timeout: int = 30):
        self.backend_name = backend
        cfg = DEFAULT_BACKENDS.get(backend, None)
        if cfg is None:
            raise ValueError(f"Unknown backend: {backend}")

        self.fmt = cfg.fmt
        self.base_url = base_url.rstrip("/") if base_url else cfg.base_url.rstrip("/")
        # priority: explicit api_key argument > env var from mapping > unset
        if api_key:
            self.api_key = api_key
        elif cfg.api_key_env:
            self.api_key = os.environ.get(cfg.api_key_env)
        else:
            self.api_key = None

        self.model = model
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            # prefer Authorization: Bearer for OpenAI-format backends
            if self.fmt == "openai":
                headers["Authorization"] = f"Bearer {self.api_key}"
            else:
                # Anthropic historically used x-api-key; accept either
                headers["x-api-key"] = self.api_key
        return headers

    def request(self, prompt: Optional[str] = None, messages: Optional[List[Dict[str, str]]] = None, max_tokens: int = 512, temperature: float = 0.0, **kwargs) -> str:
        """Send either a single `prompt` (string) or chat-style `messages`.

        Returns the text output as a string.
        """
        if self.fmt == "openai":
            url = f"{self.base_url}/v1/chat/completions"
            if messages is None:
                if prompt is None:
                    raise ValueError("Either prompt or messages must be provided")
                messages = [{"role": "user", "content": prompt}]

            payload: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            payload.update(kwargs)
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # handle chat/completions response shape
            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                # fallback: completion-style
                if "choices" in data and len(data["choices"]) and "text" in data["choices"][0]:
                    return data["choices"][0]["text"]
                # ollama sometimes returns 'choices' -> 'message' -> 'content'
                return str(data)

        elif self.fmt == "anthropic":
            # Use Anthropic Responses API format: POST /v1/responses with {model, input}
            url = f"{self.base_url}/v1/responses"
            if prompt is None and messages is not None:
                # flatten messages to a single prompt
                prompt = "\n".join(m["content"] for m in messages if "content" in m)
            if prompt is None:
                raise ValueError("prompt required for anthropic backend")
            payload = {"model": self.model, "input": prompt}
            payload.update(kwargs)
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # try several output shapes
            # Responses API: data['output'][0]['content'][0]['text']
            try:
                out = data
                if "output" in out and len(out["output"]) and "content" in out["output"][0]:
                    # content is a list of content blocks
                    blocks = out["output"][0]["content"]
                    for b in blocks:
                        if isinstance(b, dict) and b.get("type") == "output_text" and "text" in b:
                            return b["text"]
                    # fallback: join any text fields
                    texts = [b.get("text") for b in blocks if isinstance(b, dict) and "text" in b]
                    if texts:
                        return "\n".join(texts)
            except Exception:
                pass
            # last resort
            if "completion" in data:
                return data["completion"]
            return str(data)

        else:
            raise ValueError(f"Unsupported backend format: {self.fmt}")


if __name__ == "__main__":
    # tiny CLI demo
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="ollama", help="backend alias from DEFAULT_BACKENDS")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--prompt", default="Say hello from the chosen backend")
    args = parser.parse_args()

    client = InferenceClient(backend=args.backend, model=args.model)
    out = client.request(prompt=args.prompt)
    print(out)


def get_completion(
    user_message: str,
    system_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """Compatibility wrapper used by PersonaLock code (Cline).

    Reads provider/model/keys from environment variables if not passed
    and returns the assistant text. Accepts the same basic args as
    the project's `local_inference.get_completion`.
    """
    # env-configurable defaults
    env_backend = os.environ.get("LLM_PROVIDER")
    env_api_key = os.environ.get("LLM_API_KEY")
    env_base = os.environ.get("LLM_API_BASE")
    env_model = os.environ.get("LLM_MODEL")

    backend = env_backend or "openai"
    api_key = env_api_key or None
    base_url = env_base or None
    # Use env model if present, otherwise let InferenceClient default apply
    if env_model:
        client = InferenceClient(backend=backend, api_key=api_key, base_url=base_url, model=env_model)
    else:
        client = InferenceClient(backend=backend, api_key=api_key, base_url=base_url)

    max_tokens = max_tokens or int(os.environ.get("LLM_MAX_TOKENS", "1024"))
    temperature = temperature or float(os.environ.get("LLM_TEMPERATURE", "0.7"))

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    return client.request(messages=messages, max_tokens=max_tokens, temperature=temperature)
