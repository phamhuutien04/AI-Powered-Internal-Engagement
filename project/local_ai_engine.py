"""Small Ollama client used by the desktop application.

The application deliberately talks only to the local Ollama service. Workbook
data therefore stays on the user's computer unless another provider is added
explicitly in the future.
"""

from __future__ import annotations

import json
from urllib import error, request


OLLAMA_URL = "http://127.0.0.1:11434"
MODEL_NAME = "qwen3.5:4b-q4_K_M"
MODEL_LABEL = "Qwen 3.5 · 4B"


class LocalAIError(RuntimeError):
    """Raised when the local AI service cannot complete a request."""


def _json_request(path: str, payload: dict | None = None, timeout: int = 10) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        f"{OLLAMA_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise LocalAIError(
            "The local AI service is not running. Open Ollama and try again."
        ) from exc
    except (json.JSONDecodeError, TimeoutError) as exc:
        raise LocalAIError("The local AI service returned an invalid response.") from exc


def model_is_ready() -> bool:
    """Return True when Ollama is running and the configured model is installed."""
    response = _json_request("/api/tags", timeout=5)
    installed = {item.get("name", "") for item in response.get("models", [])}
    return MODEL_NAME in installed


def generate(prompt: str, system: str | None = None, timeout: int = 180) -> str:
    """Generate one non-streaming response with the configured local model."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = _json_request(
        "/api/chat",
        {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "options": {"temperature": 0.15, "num_ctx": 4096, "num_predict": 500},
        },
        timeout=timeout,
    )
    content = response.get("message", {}).get("content", "").strip()
    if not content:
        raise LocalAIError("The local AI model returned an empty response.")
    return content
