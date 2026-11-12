"""Produce a cautious recommendation from facts and supplied evidence."""

from typing import Any

from .model import JsonModel
from .schemas import ClaimAnalysis, EntitlementResult, ResearchResult

VALID = {"pay_as_computed", "request_further_evidence", "decline", "escalate_to_human"}


def assess_entitlement(
    claim: ClaimAnalysis, research: ResearchResult, model: JsonModel | None = None
) -> EntitlementResult:
    """No mock legal decision is made; an LLM recommendation is provisional."""
    if model:
        result = model.generate_json(task="entitlement", payload={
            "claim": claim.__dict__, "research": research.__dict__,
            "allowed_recommendations": sorted(VALID),
            "instruction": "Use only supplied evidence. Never invent legal rules or amounts.",
        })
        if result.get("recommendation") not in VALID:
            raise ValueError("Model returned an invalid recommendation")
        return EntitlementResult(**result)
    if not research.relevant_provisions:
        recommendation = "escalate_to_human"
        reason = "Demo mode has no supplied regulatory evidence, so eligibility cannot be assessed."
    else:
        recommendation = "request_further_evidence"
        reason = "Demo mode does not decide legal eligibility; a reviewer must assess the supplied passages and facts."
    uncertainties = list(research.evidence_gaps)
    uncertainties.extend(claim.missing_information)
    return EntitlementResult(
        recommendation=recommendation,
        rationale=reason,
        citations=[str(p["citation"]) for p in research.relevant_provisions if p.get("citation")],
        uncertainties=list(dict.fromkeys(uncertainties)),
    )
