# Air Passenger Compensation Claim Triage Service

## Overview
An AI-powered service designed to analyse and triage air passenger compensation claims arising from flight disruptions.

The system processes passenger complaints through a structured multi-agent workflow to assess claims, research applicable regulations, evaluate compensation entitlement, and verify the results.

## AI Agent Workflow

The system consists of four stages:

1. **Claim Analysis:** Extracts relevant information from passenger complaints, including flight details, delays, and disruption information.

2. **Regulation Research:** Identifies relevant regulatory information and supporting evidence for the claim.

3. **Entitlement Assessment:** Evaluates whether the passenger may be eligible for compensation based on the available claim information and regulatory evidence.

4. **Verification:** Checks the assessment and supporting evidence before producing the result.

## Human Review

When required information or supporting regulatory evidence is unavailable or cannot be verified, the system escalates the claim for human review rather than making unsupported decisions.

## Testing

Run the AI agent workflow tests using:

```bash
python -m unittest agents.test_workflow
```

## Project Status

The project is being developed collaboratively, with separate contributions to AI agents, RAG-based regulation research, and backend infrastructure.
