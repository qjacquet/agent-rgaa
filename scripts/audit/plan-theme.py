#!/usr/bin/env python3
"""Génère la file de travail MCP pour une thématique (sous-agent).

Usage:
  python3 scripts/audit/plan-theme.py <theme_id> <audit_dir>

Produit: audits/.../work-queue/theme-{id}.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_AUDIT_PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(_AUDIT_PKG))

from config import ROOT, RULES_PATH  # noqa: E402
from mcp_hints import hints_for_test, test_requires_at_handoff  # noqa: E402


def load_completed(audit_dir: Path, theme_id: str) -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    log = audit_dir / "audit-log.jsonl"
    if not log.exists():
        return done
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") != "test_result" or e.get("theme_id") != theme_id:
            continue
        done.add((e["test"], e["sample"]))
    return done


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("theme_id")
    parser.add_argument("audit_dir", type=Path)
    args = parser.parse_args()

    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    theme = next(t for t in rules["themes"] if t["id"] == args.theme_id)

    samples = json.loads((args.audit_dir / "samples-status.json").read_text(encoding="utf-8"))["samples"]
    ok_samples = [s for s in samples if s.get("status") == "ok"]
    done = load_completed(args.audit_dir, args.theme_id)

    queue = []
    for criterion in theme["criteria"]:
        for test in criterion["tests"]:
            for sample in ok_samples:
                if (test["id"], sample["slug"]) in done:
                    continue
                at_handoff = test_requires_at_handoff(test)
                queue.append({
                    "theme_id": args.theme_id,
                    "criterion_id": criterion["id"],
                    "test_id": test["id"],
                    "test_title": test["title"],
                    "sample_slug": sample["slug"],
                    "sample_url": sample["url"],
                    "agent_scope": test.get("agent_scope", "full"),
                    "human_complement_required": test.get("human_complement_required", False),
                    "at_handoff": at_handoff,
                    "agent_steps": test.get("agent_steps") or test.get("methodology_steps") or [],
                    "human_steps": test.get("human_steps") or [],
                    "success_criterion": test.get("success_criterion", ""),
                    "failure_criterion": test.get("failure_criterion", ""),
                    "mcp_hints": hints_for_test(test),
                    "mcp_workflow": [
                        "browser_navigate(sample_url)",
                        "browser_snapshot",
                        *([] if at_handoff else [
                            "Exécuter chaque agent_step via browser_cdp / browser_press_key / browser_click",
                            "browser_take_screenshot si fail",
                        ]),
                        f"python3 scripts/audit/log-result.py {args.audit_dir} --sample {sample['slug']} ...",
                    ],
                })

    out_dir = args.audit_dir / "work-queue"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "theme_id": args.theme_id,
        "theme_title": theme["title"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pending": len(queue),
        "completed": len(done),
        "items": queue,
    }
    out_path = out_dir / f"theme-{args.theme_id}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{out_path}: {len(queue)} tests pending, {len(done)} done")


if __name__ == "__main__":
    main()
