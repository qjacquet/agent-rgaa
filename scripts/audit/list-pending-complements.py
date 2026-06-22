#!/usr/bin/env python3
"""Liste les compléments humains en attente (tiers AT / jugement) et génère pending-complements.md.

Usage:
  python3 scripts/audit/list-pending-complements.py audits/{site}/{date}/
  python3 scripts/audit/list-pending-complements.py audits/{site}/{date}/ --stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

_AUDIT_PKG = Path(__file__).resolve().parent
_ROOT = _AUDIT_PKG.parent.parent
sys.path.insert(0, str(_AUDIT_PKG))

from human_tiers import PRIORITY_NC_TESTS, tier_for_test  # noqa: E402


def load_log(audit_dir: Path) -> tuple[dict, set]:
    agent: dict[tuple[str, str, str], str] = {}
    human: set[tuple[str, str, str]] = set()
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
            human.add(key)
    return agent, human


def load_urls(audit_dir: Path) -> dict[str, str]:
    status = audit_dir / "samples-status.json"
    if not status.exists():
        return {}
    data = json.loads(status.read_text(encoding="utf-8"))
    return {s["slug"]: s["url"] for s in data["samples"]}


def agent_label(result: str) -> str:
    return {"pass": "C", "fail": "NC", "na": "NA", "nt": "NT"}.get(result, result)


def build_pending(audit_dir: Path) -> list[dict]:
    rules = json.loads((_ROOT / "data/rgaa-rules.json").read_text(encoding="utf-8"))
    agent, human = load_log(audit_dir)
    urls = load_urls(audit_dir)

    test_meta: dict[str, tuple[dict, str, str]] = {}
    for theme in rules["themes"]:
        for crit in theme["criteria"]:
            for test in crit["tests"]:
                if test.get("human_complement_required"):
                    test_meta[test["id"]] = (test, crit["id"], test.get("title", ""))

    pending: list[dict] = []
    for key, agent_result in agent.items():
        criterion, sample, test_id = key
        if test_id not in test_meta or agent_result == "na" or key in human:
            continue
        test, crit_id, title = test_meta[test_id]
        tier = tier_for_test(test, crit_id)
        if tier == "auto":
            continue
        pending.append({
            "test": test_id,
            "criterion": criterion,
            "tier": tier,
            "sample": sample,
            "url": urls.get(sample, ""),
            "agent_result": agent_result,
            "agent_label": agent_label(agent_result),
            "priority": test_id in PRIORITY_NC_TESTS or agent_result == "fail",
            "title": title[:120],
        })

    pending.sort(key=lambda x: (
        not x["priority"],
        x["tier"],
        x["test"],
        x["sample"],
    ))
    return pending


def render_markdown(pending: list[dict], audit_dir: Path) -> str:
    samples = json.loads((audit_dir / "samples-status.json").read_text(encoding="utf-8"))
    site = samples.get("site", audit_dir.name)
    date = samples.get("audit_date", "")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    by_test: dict[str, list[dict]] = defaultdict(list)
    for p in pending:
        by_test[p["test"]].append(p)

    lines = [
        f"# Compléments humains en attente — {site}",
        "",
        f"> Généré le {ts} — **{len(pending)}** combinaisons test × page (tiers AT / jugement).",
        "",
        "## Synthèse",
        "",
        "| Tier | Combinaisons |",
        "| ---- | ------------ |",
    ]
    tier_counts = defaultdict(int)
    for p in pending:
        tier_counts[p["tier"]] += 1
    for tier in ("judgment", "at"):
        if tier_counts[tier]:
            lines.append(f"| {tier} | {tier_counts[tier]} |")

    prio = [p for p in pending if p["priority"]]
    lines.extend([
        "",
        f"**Priorité spot-check** : {len(prio)} combinaisons (NC agent ou tests marqués prioritaires).",
        "",
        "## Priorité — NC agent",
        "",
        "| Test | Page | Agent | URL |",
        "| ---- | ---- | ----- | --- |",
    ])
    for p in prio:
        lines.append(f"| {p['test']} | {p['sample']} | **{p['agent_label']}** | {p['url']} |")

    lines.extend([
        "",
        "## Détail par test",
        "",
    ])
    for test_id in sorted(by_test):
        items = by_test[test_id]
        first = items[0]
        lines.append(f"### {test_id} — tier **{first['tier']}**")
        lines.append("")
        lines.append(f"*{first['title']}…*")
        lines.append("")
        lines.append("| Page | Agent | URL |")
        lines.append("| ---- | ----- | --- |")
        for p in items:
            mark = "**" if p["priority"] else ""
            lines.append(f"| {p['sample']} | {mark}{p['agent_label']}{mark} | {p['url']} |")
        lines.append("")

    lines.extend([
        "## Prochaine session",
        "",
        "1. Spot-check les lignes **priorité** ci-dessus",
        "2. 1 page type par test C agent (composants communs header/footer)",
        "3. Logger `human_complement` puis `aggregate-grid.py`",
        "",
        "Voir [human-complement.md](../../.cursor/skills/rgaa-audit/human-complement.md).",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="List pending AT/judgment human complements")
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--stdout", action="store_true", help="Print markdown to stdout only")
    args = parser.parse_args()

    pending = build_pending(args.audit_dir)
    md = render_markdown(pending, args.audit_dir)

    if args.stdout:
        print(md, end="")
        return

    out = args.audit_dir / "pending-complements.md"
    out.write_text(md, encoding="utf-8")
    print(f"{len(pending)} compléments en attente → {out}")


if __name__ == "__main__":
    main()
