"""Check whether recommendations are traceable to supplied evidence."""

from .schemas import ClaimAnalysis, EntitlementResult, ResearchResult, VerificationResult


def verify_recommendation(
    claim: ClaimAnalysis, research: ResearchResult, entitlement: EntitlementResult
) -> VerificationResult:
    flags = []
    citations_available = {str(p["citation"]) for p in research.relevant_provisions if p.get("citation")}
    if not entitlement.citations:
        flags.append("Recommendation has no citations.")
    elif not set(entitlement.citations).issubset(citations_available):
        flags.append("One or more recommendation citations are absent from supplied passages.")
    if not research.relevant_provisions:
        flags.append("No regulatory evidence was supplied.")
    if entitlement.compensation_amount is not None and not entitlement.citations:
        flags.append("Compensation amount is unsupported by a cited passage.")
    if entitlement.uncertainties or claim.missing_information or research.evidence_gaps:
        flags.append("Assessment contains missing information or uncertainty.")
    recommendation = entitlement.recommendation
    if flags and recommendation in {"pay_as_computed", "decline"}:
        recommendation = "escalate_to_human"
        flags.append("Escalated because the conclusion cannot be confidently verified.")
    return VerificationResult(supported=not flags, flags=flags, recommendation=recommendation)
