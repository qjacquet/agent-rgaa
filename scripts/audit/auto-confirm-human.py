#!/usr/bin/env python3
"""Auto-confirme les compléments humains en reprenant le résultat agent.

Politique par défaut : tout sauf tests AT (restitution lecteur d'écran)
et jugement (images, couleur informative, médias, pertinence).

Usage:
  python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/
  python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/ --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_AUDIT_PKG = Path(__file__).resolve().parent
_ROOT = _AUDIT_PKG.parent.parent
sys.path.insert(0, str(_AUDIT_PKG))

from human_tiers import (  # noqa: E402
    is_at_test,
    is_judgment_test,
    tier_for_test,
)


def load_log(audit_dir: Path) -> tuple[dict, dict]:
    agent: dict[tuple[str, str, str], str] = {}
    human: dict[tuple[str, str, str], dict] = {}
    log = audit_dir / "audit-log.jsonl"
    if not log.exists():
        return agent, human
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        key = (e.get("criterion"), e.get("sample"), e.get("test"))
        if e.get("event") == "test_result":
            agent[key] = e.get("agent_result")
        elif e.get("event") == "human_complement":
            human[key] = e
    return agent, human


def load_urls(audit_dir: Path) -> dict[str, str]:
    status = audit_dir / "samples-status.json"
    if not status.exists():
        return {}
    data = json.loads(status.read_text(encoding="utf-8"))
    return {s["slug"]: s["url"] for s in data["samples"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-confirm human complements (non AT/judgment)")
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rules = json.loads((_ROOT / "data/rgaa-rules.json").read_text(encoding="utf-8"))
    agent, human = load_log(args.audit_dir)
    urls = load_urls(args.audit_dir)
    ts = datetime.now(timezone.utc).isoformat()

    test_meta: dict[str, tuple[dict, str]] = {}
    for theme in rules["themes"]:
        for crit in theme["criteria"]:
            for test in crit["tests"]:
                if test.get("human_complement_required"):
                    test_meta[test["id"]] = (test, crit["id"])

    to_write: list[dict] = []
    skipped = Counter()
    reasons = Counter()

    for key, agent_result in agent.items():
        criterion, sample, test_id = key
        if test_id not in test_meta:
            continue
        if agent_result == "na":
            skipped["na"] += 1
            continue
        if key in human:
            skipped["already_done"] += 1
            continue

        test, crit_id = test_meta[test_id]
        t = tier_for_test(test, crit_id)
        if t != "auto":
            skipped[t] += 1
            reasons[test_id] += 1
            continue

        entry = {
            "event": "human_complement",
            "sample": sample,
            "sample_url": urls.get(sample, ""),
            "criterion": criterion,
            "test": test_id,
            "human_result": agent_result,
            "agent_result": agent_result,
            "comment": "Auto-confirmé : reprend le résultat agent (hors AT/jugement)",
            "source": "auto_confirmed_agent",
            "policy": "all_except_at_judgment",
            "timestamp": ts,
        }
        to_write.append(entry)

    print(f"À auto-confirmer : {len(to_write)}")
    print(f"Ignorés : {dict(skipped)}")
    if reasons:
        print(f"Tests exclus (AT/jugement) encore en attente : {len(reasons)} types")
        for tid, _ in sorted(reasons.items())[:10]:
            print(f"  - {tid}")
        if len(reasons) > 10:
            print(f"  … et {len(reasons) - 10} autres")

    if args.dry_run:
        by_test = Counter(e["test"] for e in to_write)
        print("\nPar test (auto):")
        for tid, n in sorted(by_test.items()):
            print(f"  {tid}: {n}")
        return

    log_path = args.audit_dir / "audit-log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        for entry in to_write:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n{len(to_write)} entrées human_complement ajoutées → {log_path}")

    if to_write:
        import subprocess

        agg = _AUDIT_PKG / "aggregate-grid.py"
        subprocess.run([sys.executable, str(agg), str(args.audit_dir)], check=True)


if __name__ == "__main__":
    main()
