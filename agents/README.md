# AI Agents module

## Architecture

`workflow.run_workflow(claim, passages)` sends the same structured claim through four small steps:

1. `claim_analysis` extracts reported facts and highlights missing details.
2. `regulation_research` associates the passages supplied by the RAG pipeline with their citation/source IDs. It does not retrieve documents.
3. `entitlement` returns one of `pay_as_computed`, `request_further_evidence`, `decline`, or `escalate_to_human`.
4. `verification` checks citations and uncertainty and can escalate an unsupported pay/decline recommendation.

Passages can be strings or objects such as `{"id": "source-1", "text": "..."}`. A structured claim can use keys such as `complaint`, `flight_number`, `disruption_type`, `scheduled_time`, and `actual_time`. The result is a dataclass with `to_dict()` for JSON/API integration.

## Run the demo

From the repository root, run:

```powershell
$env:AGENT_MODE = "demo"
Get-Content agents/sample_complaint.txt -Raw | python -c "import sys; from agents.workflow import run_workflow; import json; print(json.dumps(run_workflow(sys.stdin.read(), [], mode='demo').to_dict(), indent=2))"
```

Demo mode is explicitly labelled and does not decide legal eligibility. With no real passages it escalates; with passages it requests further evidence. It never fabricates compensation amounts.

## Connect an LLM

Implement the `JsonModel.generate_json(task=..., payload=...)` protocol in your provider adapter, then call `run_workflow(claim, passages, model=adapter, mode="llm")`. The adapter should return the schema fields requested for each task. No provider SDK or API key handling is built into this module; load secrets from your runtime environment and do not commit `.env` files. LLM output remains provisional and should be reviewed by a human.

## Tests

Run `python -m unittest agents.test_workflow` from the repository root. The module uses only the Python standard library, so no shared requirements file needs changing.
