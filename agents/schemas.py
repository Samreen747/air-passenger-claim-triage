"""Shared data contract used by the agents and their callers."""

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Recommendation = Literal[
    "pay_as_computed",
    "request_further_evidence",
    "decline",
    "escalate_to_human",
]


@dataclass
class ClaimAnalysis:
    claim_type: str | None = None
    flight_number: str | None = None
    airline: str | None = None
    origin: str | None = None
    destination: str | None = None
    disruption_type: str | None = None
    scheduled_time: str | None = None
    actual_time: str | None = None
    alternate_flight: str | None = None
    complaint_summary: str = ""
    missing_information: list[str] = field(default_factory=list)


@dataclass
class ResearchResult:
    relevant_provisions: list[dict[str, Any]] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)


@dataclass
class EntitlementResult:
    recommendation: Recommendation
    rationale: str
    compensation_amount: float | None = None
    currency: str | None = None
    citations: list[str] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    supported: bool
    flags: list[str] = field(default_factory=list)
    recommendation: Recommendation | None = None


@dataclass
class WorkflowResult:
    mode: Literal["demo", "llm"]
    claim_analysis: ClaimAnalysis
    regulation_research: ResearchResult
    entitlement: EntitlementResult
    verification: VerificationResult
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
