#!/usr/bin/env python3
"""Agrège audit-log.jsonl → grid.csv (source unique : test_result MCP).

Ne devine jamais C/NC — lit uniquement les entrées test_result.
Règles : scoring.md (fail > nt > pass > na).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent


def aggregate_tests(results: list[str]) -> str:
    if "fail" in results:
        return "NC"
    if results and all(r == "na" for r in results):
        return "NA"
    if any(r == "nt" for r in results):
        return "NT"
    if any(r == "pass" for r in results):
        return "C"
    return "NT"


def aggregate_site(statuses: list[str]) -> str:
    if "NC" in statuses:
        return "NC"
    if statuses and all(s == "NA" for s in statuses):
        return "NA"
    if any(s == "NT" for s in statuses):
        return "NT"
    if any(s == "C" for s in statuses):
        return "C"
    return "NT"


def load_test_results(audit_dir: Path) -> dict[tuple[str, str, str], str]:
    """(criterion, sample, test_id) → pass|fail|na|nt"""
    out: dict[tuple[str, str, str], str] = {}
    log = audit_dir / "audit-log.jsonl"
    if not log.exists():
        return out
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") != "test_result":
            continue
        key = (e["criterion"], e["sample"], e["test"])
        out[key] = e["agent_result"]
    return out


def load_samples(audit_dir: Path) -> list[str]:
    status = audit_dir / "samples-status.json"
    if status.exists():
        data = json.loads(status.read_text(encoding="utf-8"))
        return sorted(s["slug"] for s in data["samples"] if s.get("status") == "ok")
    samples_dir = audit_dir / "samples"
    return sorted(p.stem for p in samples_dir.glob("*.json"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_dir", type=Path, nargs="?", default=_ROOT / "audits/cmvmediforce-fr/2026-06-22")
    args = parser.parse_args()

    rules = json.loads((_ROOT / "data/rgaa-rules.json").read_text(encoding="utf-8"))
    results = load_test_results(args.audit_dir)
    slug_order = load_samples(args.audit_dir)

    rows = []
    ts = datetime.now(timezone.utc).isoformat()
    tested_count = len(results)

    for theme in rules["themes"]:
        for criterion in theme["criteria"]:
            cid = criterion["id"]
            row = {
                "theme_id": theme["id"],
                "theme_title": theme["title"],
                "criterion_id": cid,
                "criterion_title": criterion["title"][:100],
                "wcag_level": ",".join(criterion.get("wcag_levels", [])),
            }
            statuses = []
            for slug in slug_order:
                test_results = []
                for test in criterion["tests"]:
                    tid = test["id"]
                    r = results.get((cid, slug, tid))
                    if r is not None:
                        test_results.append(r)
                if not test_results:
                    row[slug] = "NT"
                    statuses.append("NT")
                else:
                    st = aggregate_tests(test_results)
                    row[slug] = st
                    statuses.append(st)
            row["site_status"] = aggregate_site(statuses)
            row["notes"] = ""
            rows.append(row)

    headers = ["theme_id", "theme_title", "criterion_id", "criterion_title", "wcag_level"] + slug_order + ["site_status", "notes"]
    csv_path = args.audit_dir / "grid.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)

    site_counts = Counter(r["site_status"] for r in rows)
    with (args.audit_dir / "audit-log.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"event": "grid_aggregated", "test_results_in_log": tested_count, "site_counts": dict(site_counts), "timestamp": ts}, ensure_ascii=False) + "\n")

    print(f"grid.csv ← {tested_count} test results | site: {dict(site_counts)}")


if __name__ == "__main__":
    main()
