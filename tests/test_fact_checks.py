"""Reproduce unknown-to-false projection without live customer data or writes."""

import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "plugins/eightdegrees-sales-workflow/scripts/fact_checks.py"
SPEC = importlib.util.spec_from_file_location("fact_checks", PATH)
FACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FACTS)


class FactChecksTests(unittest.TestCase):
    def test_observed_unknown_finance_false_projection_is_rejected(self):
        result = FACTS.check_facts({"finance_approved": False, "finance_status": "Not confirmed"})
        self.assertEqual(result["status"], "NeedsCorrection")

    def test_unknown_finance_null_and_explicit_yes_no_are_distinct(self):
        for state, value in [("Not confirmed", None), ("Approved", True), ("Rejected", False)]:
            with self.subTest(state=state):
                self.assertEqual(FACTS.check_facts({"finance_approved": value, "finance_status": state})["status"], "ValidFactSemantics")

    def test_missing_or_ambiguous_status_is_not_inferred_from_boolean(self):
        for data in [{"finance_approved": False}, {"finance_status": "Unknown"},
                     {"finance_approved": False, "finance_status": "Not approved"},
                     {"finance_approved": 1, "finance_status": "Approved"}]:
            with self.subTest(data=data):
                self.assertEqual(FACTS.check_facts(data)["status"], "NeedsCorrection")

    def test_general_three_state_facts_require_known_evidence(self):
        for state, value in FACTS.STATES.items():
            data = {"facts": [{"name": "viewing_confirmed", "status": state, "value": value,
                               "evidence": "Operator confirmed the requested appointment." if value is not None else "Not provided"}]}
            self.assertEqual(FACTS.check_facts(data)["status"], "ValidFactSemantics")
        data["facts"][0].update(status="ConfirmedNo", value=False, evidence="")
        self.assertEqual(FACTS.check_facts(data)["status"], "NeedsCorrection")

    def test_system_flags_are_not_customer_facts(self):
        with self.assertRaises(ValueError):
            FACTS.check_facts({"crm_written": False, "confirmed_persona": False})

    def test_duplicate_conflicting_fact_is_rejected(self):
        data = {"facts": [{"name": "viewing_confirmed", "status": "Unknown", "value": None},
                          {"name": "viewing_confirmed", "status": "ConfirmedNo", "value": False, "evidence": "Cancelled"}]}
        self.assertEqual(FACTS.check_facts(data)["status"], "NeedsCorrection")
