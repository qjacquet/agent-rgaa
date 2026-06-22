#!/usr/bin/env python3
"""Evaluate Theme 6 (Liens) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t6(d):
    return d.get("theme6", d)


def ev_6_1_1(d):
    c = t6(d).get("counts", {})
    if c.get("text", 0) == 0:
        return "na", "Aucun lien texte"
    bad = t6(d).get("badText", [])
    if bad:
        t0 = bad[0].get("text") or "?"
        return "fail", f"{len(bad)} lien(s) texte non explicite(s): «{t0}»"
    return "pass", f"{c.get('text', 0)} lien(s) texte avec intitulé ou contexte explicite"


def ev_6_1_2(d):
    c = t6(d).get("counts", {})
    if c.get("image", 0) == 0:
        return "na", "Aucun lien image"
    bad = t6(d).get("badImg", [])
    if bad:
        return "fail", f"{len(bad)} lien(s) image sans alternative textuelle"
    return "pass", f"{c.get('image', 0)} lien(s) image avec alt/contexte"


def ev_6_1_3(d):
    c = t6(d).get("counts", {})
    if c.get("composite", 0) == 0:
        return "na", "Aucun lien composite"
    bad = t6(d).get("badComp", [])
    if bad:
        return "fail", f"{len(bad)} lien(s) composite sans intitulé complet"
    return "pass", f"{c.get('composite', 0)} lien(s) composite avec texte+alt"


def ev_6_1_4(d):
    svg = t6(d).get("counts", {}).get("svg", 0)
    if svg == 0:
        return "na", "Aucun lien SVG"
    bad = t6(d).get("badSvg", 0)
    if bad:
        return "fail", f"{bad} lien(s) SVG sans nom accessible"
    return "pass", f"{svg} lien(s) SVG avec nom accessible"


def ev_6_1_5(d):
    bad = t6(d).get("badAria", [])
    if not bad and not any(l.get("hasBothVisibleAndAria") for l in t6(d).get("links", [])):
        return "na", "Aucun lien avec intitulé visible + aria-label/title"
    if bad:
        v = bad[0].get("visible", "")[:30]
        return "fail", f"{len(bad)} lien(s): nom accessible ne contient pas l'intitulé visible «{v}»"
    return "pass", "Liens avec nom accessible contenant l'intitulé visible"


def ev_6_2_1(d):
    c = t6(d).get("counts", {})
    total = c.get("total", 0)
    if total == 0:
        return "na", "Aucun lien"
    bad = t6(d).get("badEmpty", [])
    if bad:
        return "fail", f"{len(bad)} lien(s) sans intitulé (texte ni alternative)"
    return "pass", f"{total} lien(s) avec intitulé"


EVALUATORS = {
    "6.1.1": ("6.1", ev_6_1_1),
    "6.1.2": ("6.1", ev_6_1_2),
    "6.1.3": ("6.1", ev_6_1_3),
    "6.1.4": ("6.1", ev_6_1_4),
    "6.1.5": ("6.1", ev_6_1_5),
    "6.2.1": ("6.2", ev_6_2_1),
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
                "--theme", "6", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 6: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
