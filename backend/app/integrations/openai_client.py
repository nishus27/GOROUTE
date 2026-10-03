"""OpenAI integration.

OpenAI *explains* the decision the engine already made. It never computes the
route score. When ``OPENAI_API_KEY`` is configured this client asks OpenAI for a
plain-language explanation; otherwise the caller uses the deterministic
explanation built from the engine's own output.
"""

import json
import logging
import os
import urllib.request

logger = logging.getLogger(__name__)

CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are GoRoute's journey assistant. A deterministic scoring engine has "
    "already computed and ranked the routes. Explain the recommendation in 2-3 "
    "short sentences using only the metrics provided. Never invent numbers and "
    "never recalculate or dispute the score."
)


class OpenAIExplainer:
    """Minimal client for OpenAI chat completions used for explanations only."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 12) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or ""
        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        """True when an OpenAI API key is available."""
        return bool(self.api_key)

    def explain(self, context: dict) -> str | None:
        """Return a short explanation, or None to use the deterministic fallback."""
        if not self.is_configured:
            return None

        body = {
            "model": self.model,
            "temperature": 0.2,
            "max_tokens": 220,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(context, default=str)},
            ],
        }
        request = urllib.request.Request(
            CHAT_COMPLETIONS_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("OpenAI explanation failed, using deterministic text: %s", exc)
            return None
