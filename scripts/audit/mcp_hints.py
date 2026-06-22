"""Infère les outils MCP à utiliser pour chaque étape agent_steps."""
from __future__ import annotations

import re

from config import AT_ONLY_TEST_IDS, CDP_SCRIPTS

# Patterns étape → outils MCP (ordre = priorité)
STEP_TOOL_PATTERNS: list[tuple[re.Pattern[str], list[str], str | None]] = [
    (re.compile(r"technologies d.assistance|lecteur d.écran|restitu[ée]", re.I), [], "at_handoff"),
    (re.compile(r"clavier|tabulation|tab |touche|focus|ordre de tab", re.I), ["browser_press_key", "browser_snapshot"], None),
    (re.compile(r"contraste|couleur du texte|ratio", re.I), ["browser_cdp"], "contrast-scan"),
    (re.compile(r"capture|screenshot|preuve", re.I), ["browser_take_screenshot"], None),
    (re.compile(r"clic|pointage|souris|activer", re.I), ["browser_click", "browser_press_key"], None),
    (re.compile(r"getComputedStyle|css|feuille de style|sans css", re.I), ["browser_cdp"], None),
    (re.compile(r"rettrouver|retrouver|présence|vérifier|balise|élément|document", re.I), ["browser_cdp"], "query-dom"),
]


def hints_for_step(step: str, test_id: str) -> dict:
    """Retourne tools, script, note pour une étape de méthodologie."""
    if test_id in AT_ONLY_TEST_IDS:
        return {"tools": [], "script": None, "note": "at_handoff — VoiceOver/NVDA requis", "at_handoff": True}

    low = step.lower()
    for pattern, tools, script_key in STEP_TOOL_PATTERNS:
        if pattern.search(low):
            if script_key == "at_handoff":
                return {"tools": [], "script": None, "note": "restitution AT — hors MCP", "at_handoff": True}
            script = CDP_SCRIPTS.get(script_key) if script_key else None
            return {"tools": tools, "script": script, "note": step[:120], "at_handoff": False}

    return {
        "tools": ["browser_cdp", "browser_snapshot"],
        "script": "query-dom.js",
        "note": step[:120],
        "at_handoff": False,
    }


def hints_for_test(test: dict) -> list[dict]:
    """MCP hints pour toutes les agent_steps d'un test."""
    steps = test.get("agent_steps") or test.get("methodology_steps") or []
    return [
        {"step_index": i, "step": step, **hints_for_step(step, test["id"])}
        for i, step in enumerate(steps)
    ]


def test_requires_at_handoff(test: dict) -> bool:
    if test["id"] in AT_ONLY_TEST_IDS:
        return True
    for step in test.get("human_steps") or []:
        if hints_for_step(step, test["id"]).get("at_handoff"):
            return True
    return False
