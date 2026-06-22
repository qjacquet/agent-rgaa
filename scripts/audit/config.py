"""Configuration partagée — audit RGAA MCP."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RULES_PATH = ROOT / "data" / "rgaa-rules.json"
CDP_DIR = ROOT / "scripts" / "cdp"

# Tests dont la méthodologie exige une restitution AT (VoiceOver/NVDA) — seul vrai NT agent
AT_ONLY_TEST_IDS = frozenset({
    "1.3.8",
    "1.6.6",
    "1.6.8",
    "1.6.9",
    "7.1.2",
    "10.8.1",
})

# Complément humain clavier/focus après passe agent MCP
KEYBOARD_COMPLEMENT_TEST_IDS = frozenset({
    "7.3.1",
    "7.3.2",
    "7.4.1",
    "8.9.1",
    "8.9.2",
    "9.3.1",
    "9.3.2",
    "9.3.3",
    "10.7.1",
    "10.7.2",
    "10.7.3",
    "12.7.1",
    "12.7.2",
})

# Scripts CDP — helpers appelés PENDANT un test, jamais pour scorer en masse
CDP_SCRIPTS = {
    "query-dom": "query-dom.js",
    "contrast-scan": "contrast-scan.js",
    "keyboard-map": "keyboard-map.js",
}
