"""Optional LLM adapter contract. No provider or secret is bundled here."""

from typing import Any, Protocol


class JsonModel(Protocol):
    """Implement generate_json to connect a provider such as a hosted LLM."""

    def generate_json(self, *, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Return the requested JSON object; callers must validate its fields."""


def configured_mode() -> str:
    """Read AGENT_MODE without requiring a dotenv file or extra dependency."""
    import os

    mode = os.getenv("AGENT_MODE", "demo").strip().lower()
    if mode not in {"demo", "llm"}:
        raise ValueError("AGENT_MODE must be 'demo' or 'llm'")
    return mode
