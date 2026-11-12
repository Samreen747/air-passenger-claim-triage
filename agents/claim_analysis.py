"""Extract complaint facts. The demo extractor does not make legal findings."""

import re
from typing import Any

from .model import JsonModel
from .schemas import ClaimAnalysis

_FLIGHT = re.compile(r"\b([A-Z0-9]{2,3}\s?-?\d{1,4})\b", re.I)
_TIME = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")


def analyze_claim(claim: str | dict[str, Any], model: JsonModel | None = None) -> ClaimAnalysis:
    """Accept complaint text or a structured claim; return normalized fields."""
    if isinstance(claim, dict):
        source = dict(claim)
        complaint = str(source.get("complaint", source.get("text", "")))
        if model:
            result = model.generate_json(task="claim_analysis", payload={"claim": source})
            return ClaimAnalysis(**result)
        fields = {k: source.get(k) for k in ClaimAnalysis.__dataclass_fields__}
        fields["complaint_summary"] = fields.get("complaint_summary") or complaint[:240]
        missing = list(fields.get("missing_information") or [])
        if not fields.get("flight_number"):
            missing.append("flight number")
        if not fields.get("disruption_type"):
            missing.append("disruption type")
        fields["missing_information"] = list(dict.fromkeys(missing))
        return ClaimAnalysis(**fields)

    complaint = str(claim).strip()
    if model:
        result = model.generate_json(task="claim_analysis", payload={"complaint": complaint})
        return ClaimAnalysis(**result)
    lower = complaint.lower()
    disruption = next((name for name, terms in {
        "cancellation": ("cancel", "cancelled", "canceled"),
        "delay": ("delay", "delayed", "late"),
        "denied boarding": ("denied boarding", "bumped"),
        "missed connection": ("missed connection", "connection"),
    }.items() if any(term in lower for term in terms)), None)
    times = _TIME.findall(complaint)
    flight = _FLIGHT.search(complaint)
    missing = []
    if not flight:
        missing.append("flight number")
    if not disruption:
        missing.append("disruption type")
    if not times:
        missing.append("scheduled and actual timings")
    if not re.search(r"\b(?:Airlines?|Airways?)\b", complaint, re.I):
        missing.append("airline")
    if not re.search(r"\bfrom\s+[A-Z][A-Za-z -]+\s+to\s+[A-Z][A-Za-z -]+", complaint):
        missing.append("origin and destination")
    if disruption in {"cancellation", "delay"} and not re.search(r"\balternate\s+flight\b", lower):
        missing.append("whether an alternate flight was offered")
    return ClaimAnalysis(
        claim_type="flight disruption compensation" if disruption else None,
        flight_number=flight.group(1).replace(" ", "").upper() if flight else None,
        disruption_type=disruption,
        scheduled_time=times[0] if times else None,
        actual_time=times[1] if len(times) > 1 else None,
        alternate_flight=None,
        complaint_summary=complaint[:240],
        missing_information=missing,
    )
