#!/usr/bin/env python3
"""Evaluate Theme 2 tests from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def ev_2_1_1(d):
    vf = d.get("visibleFrames", [])
    if not vf:
        return "na", "Aucun cadre iframe/frame visible"
    bad = d.get("noTitle", [])
    if bad:
        src = bad[0].get("src", "")[:60]
        return "fail", f"{len(bad)} cadre(s) visible(s) sans attribut title: {src}"
    return "pass", f"{len(vf)} cadre(s) visible(s), tous avec attribut title"


def ev_2_2_1(d):
    vf = d.get("visibleFrames", [])
    if not vf:
        return "na", "Aucun cadre iframe/frame visible"
    with_title = [f for f in vf if f.get("hasTitle")]
    if not with_title:
        return "na", "Aucun cadre avec attribut title"
    generic = d.get("genericTitle", [])
    if generic:
        t = generic[0].get("title", "")
        return "fail", f"Title générique/non pertinent: «{t}» ({len(generic)} cadre(s))"
    titles = [f.get("title", "") for f in with_title]
    return "pass", f"{len(with_title)} cadre(s) title pertinent(s): {titles[0][:50]}"


EVALUATORS = {
    "2.1.1": ("2.1", ev_2_1_1),
    "2.2.1": ("2.2", ev_2_2_1),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--collect", type=Path, required=True)
    parser.add_argument("--skip", default="")
    args = parser.parse_args()

    data = json.loads(args.collect.read_text(encoding="utf-8"))
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    logged = 0
    for test_id, (criterion, fn) in EVALUATORS.items():
        if test_id in skip:
            continue
        result, evidence = fn(data)
        subprocess.run(
            [
                sys.executable, str(LOG_SCRIPT), str(args.audit_dir),
                "--sample", args.sample, "--url", args.url,
                "--theme", "2", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 2: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
