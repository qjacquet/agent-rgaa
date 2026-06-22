#!/usr/bin/env python3
"""Enregistre le résultat d'un test RGAA dans audit-log.jsonl.

Usage:
  python3 scripts/audit/log-result.py <audit_dir> \\
    --sample accueil --url "https://..." \\
    --theme 1 --criterion 1.1 --test 1.1.1 \\
    --scope full --result pass \\
    --evidence "12 img, toutes avec alt" \\
    --tools browser_navigate,browser_cdp,browser_press_key
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_AUDIT_PKG = Path(__file__).resolve().parent
_ROOT = _AUDIT_PKG.parent.parent
sys.path.insert(0, str(_AUDIT_PKG))

from config import KEYBOARD_COMPLEMENT_TEST_IDS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Log RGAA test result")
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--url", default="")
    parser.add_argument("--theme", required=True)
    parser.add_argument("--criterion", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--scope", default="full")
    parser.add_argument("--result", required=True, choices=["pass", "fail", "na", "nt"])
    parser.add_argument("--evidence", default="")
    parser.add_argument("--tools", default="", help="Comma-separated MCP tools used")
    parser.add_argument("--pre-analysis", default="")
    parser.add_argument("--human-complement", action="store_true")
    args = parser.parse_args()

    test_id = args.test
    human_complement = args.human_complement or test_id in KEYBOARD_COMPLEMENT_TEST_IDS

    entry = {
        "event": "test_result",
        "sample": args.sample,
        "sample_url": args.url,
        "theme_id": args.theme,
        "criterion": args.criterion,
        "test": test_id,
        "agent_scope": args.scope,
        "agent_result": args.result,
        "human_complement_required": human_complement,
        "pre_analysis": args.pre_analysis or None,
        "evidence": args.evidence,
        "mcp_tools_used": [t.strip() for t in args.tools.split(",") if t.strip()],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    log_path = args.audit_dir / "audit-log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"logged {test_id}@{args.sample} → {args.result}")


if __name__ == "__main__":
    main()
