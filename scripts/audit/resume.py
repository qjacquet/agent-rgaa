#!/usr/bin/env python3
"""Point de reprise — prochain test × échantillon à exécuter."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_dir", type=Path)
    args = parser.parse_args()

    rules = json.loads((_ROOT / "data/rgaa-rules.json").read_text(encoding="utf-8"))
    log_path = args.audit_dir / "audit-log.jsonl"
    if not log_path.exists():
        print("Start: theme 1 → python3 scripts/audit/plan-theme.py 1", args.audit_dir)
        return

    done: set[tuple[str, str]] = set()
    last = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") == "test_result":
            done.add((e["test"], e["sample"]))
            last = e

    samples = json.loads((args.audit_dir / "samples-status.json").read_text(encoding="utf-8"))["samples"]
    slugs = sorted(s["slug"] for s in samples if s.get("status") == "ok")

    if last:
        print(f"Last: {last['test']} @ {last['sample']} → {last['agent_result']}")

    for theme in rules["themes"]:
        for criterion in theme["criteria"]:
            for test in criterion["tests"]:
                for slug in slugs:
                    if (test["id"], slug) not in done:
                        print(f"\nNext: theme {theme['id']} | test {test['id']} | sample {slug}")
                        print(f"  python3 scripts/audit/plan-theme.py {theme['id']} {args.audit_dir}")
                        return

    print(f"\nComplete: {len(done)} test×sample results logged.")


if __name__ == "__main__":
    main()
