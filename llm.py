"""Small Responses API client for the experiment scaffold."""

import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://portdan.com/v1/responses"
DEFAULT_MODEL = "gpt-6.1-sol"
TIMEOUT_SECONDS = 120
RETRIES = 2


def _read_api_key() -> str:
    auth_path = Path.home() / ".codex" / "auth.json"
    try:
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        key = auth.get("OPENAI_API_KEY")
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Unable to read API credentials") from exc
    if not isinstance(key, str) or not key:
        raise RuntimeError("API credentials are missing")
    return key


def _response_text(payload: dict) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str):
        return direct

    pieces = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                pieces.append(text)
    if pieces:
        return "".join(pieces)
    raise RuntimeError("API response did not contain text")


def call_llm(prompt: str, effort: str = "low", model: str | None = None) -> str:
    """Call the configured Responses API and return its generated text."""
    api_key = _read_api_key()
    selected_model = model or os.environ.get("RSI_MODEL") or DEFAULT_MODEL
    body = json.dumps({
        "model": selected_model,
        "input": prompt,
        "reasoning": {"effort": effort},
    }).encode("utf-8")
    request = Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(RETRIES + 1):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return _response_text(payload)
        except HTTPError as exc:
            if exc.code != 429 and not 500 <= exc.code < 600:
                raise RuntimeError("API request failed") from None
            if attempt == RETRIES:
                raise RuntimeError("API request failed after retries") from None
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            if attempt == RETRIES:
                raise RuntimeError("API request failed after retries") from None
        time.sleep(attempt + 1)

    raise RuntimeError("API request failed after retries")
