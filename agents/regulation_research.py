"""Map retrieved passages to claim facts; passage retrieval is external."""

from typing import Any

from .model import JsonModel
from .schemas import ClaimAnalysis, ResearchResult


def research_regulations(
    claim: ClaimAnalysis, passages: list[dict[str, Any] | str], model: JsonModel | None = None
) -> ResearchResult:
    """Identify potentially applicable provisions from supplied passages only."""
    normalized = [({"text": p} if isinstance(p, str) else dict(p)) for p in passages]
    if model:
        result = model.generate_json(task="regulation_research", payload={
            "claim": claim.__dict__, "passages": normalized,
        })
        return ResearchResult(**result)
    provisions = []
    for passage in normalized:
        text = str(passage.get("text", passage.get("content", ""))).strip()
        if not text:
            continue
        citation = passage.get("citation") or passage.get("source") or passage.get("id")
        provisions.append({"text": text, "citation": citation})
    gaps = ["No retrieved regulation passages were supplied."] if not provisions else []
    if provisions and not any(p["citation"] for p in provisions):
        gaps.append("Retrieved passages have no citation or source identifier.")
    return ResearchResult(
        relevant_provisions=provisions,
        conditions=[],
        evidence_gaps=gaps,
    )
