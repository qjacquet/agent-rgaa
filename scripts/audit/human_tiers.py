"""Classification des tests human_complement_required en tiers AT / jugement / auto."""
from __future__ import annotations

import re

from config import AT_ONLY_TEST_IDS

AT_STEP_PATTERNS = [
    r"restitu[ée]* par les technologies d.assistance",
    r"correctement restitu[ée]* par les technologies",
    r"restituable par les technologies",
    r"lecteur d.écran",
]

JUDGMENT_CRITERION_IDS = frozenset({"3.1", "4.2"})
JUDGMENT_TEST_IDS = frozenset({"7.1.3"})

PRIORITY_NC_TESTS = frozenset({"3.1.1", "1.1.5", "9.3.3", "6.1.5", "11.9.1"})


def is_at_test(test: dict) -> bool:
    if test["id"] in AT_ONLY_TEST_IDS:
        return True
    if test.get("agent_scope") == "at_only":
        return True
    blob = " ".join(test.get("human_steps", []))
    return any(re.search(p, blob, re.I) for p in AT_STEP_PATTERNS)


def is_judgment_test(test: dict, criterion_id: str) -> bool:
    if test["id"] in JUDGMENT_TEST_IDS:
        return True
    if criterion_id in JUDGMENT_CRITERION_IDS:
        return True
    if criterion_id.startswith("1."):
        return True
    return False


def tier_for_test(test: dict, criterion_id: str) -> str:
    if is_at_test(test):
        return "at"
    if is_judgment_test(test, criterion_id):
        return "judgment"
    return "auto"
