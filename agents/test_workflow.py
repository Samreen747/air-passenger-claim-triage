"""Basic stdlib unit tests; run with python -m unittest agents.test_workflow."""

import unittest

from agents.workflow import run_workflow


class WorkflowTests(unittest.TestCase):
    def test_demo_extracts_flight_disruption_and_times(self):
        result = run_workflow(
            "Flight AI 245 delayed from 09:10 to 13:40",
            [{"id": "demo-source", "text": "Example passage, not a real rule."}],
            mode="demo",
        )
        self.assertEqual(result.claim_analysis.flight_number, "AI245")
        self.assertEqual(result.claim_analysis.disruption_type, "delay")
        self.assertEqual(result.claim_analysis.scheduled_time, "09:10")
        self.assertEqual(result.entitlement.recommendation, "request_further_evidence")
        self.assertIn("Demo/test", result.note)

    def test_no_passages_escalates_and_serializes(self):
        result = run_workflow("My flight was cancelled", [], mode="demo")
        self.assertEqual(result.entitlement.recommendation, "escalate_to_human")
        self.assertEqual(result.verification.recommendation, "escalate_to_human")
        self.assertIsInstance(result.to_dict(), dict)

    def test_llm_mode_needs_adapter(self):
        with self.assertRaises(ValueError):
            run_workflow("complaint", [], mode="llm")


if __name__ == "__main__":
    unittest.main()
