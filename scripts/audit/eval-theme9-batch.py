#!/usr/bin/env python3
"""Evaluate Theme 9 (Structuration) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t9(d):
    return d.get("theme9", d)


def ev_9_1_1(d):
    jumps = t9(d).get("headingJumps", [])
    if not t9(d).get("headings"):
        return "fail", "Aucun titre (hx) détecté"
    if jumps:
        j = jumps[0]
        return "fail", f"Saut hiérarchie {j['from']['tag']}→{j['to']['tag']}: «{j['from']['text'][:30]}» → «{j['to']['text'][:30]}»"
    return "pass", f"{len(t9(d)['headings'])} titres, hiérarchie cohérente"


def ev_9_1_2(d):
    headings = t9(d).get("headings", [])
    if not headings:
        return "na", "Aucun titre"
    empty = t9(d).get("emptyHeadings", [])
    if empty:
        return "fail", f"{len(empty)} titre(s) sans contenu pertinent"
    generic = [h for h in headings if len(h.get("text", "")) < 2]
    if generic:
        return "fail", f"{len(generic)} titre(s) non pertinent(s)"
    return "pass", f"{len(headings)} titre(s) avec contenu pertinent"


def ev_9_1_3(d):
    headings = t9(d).get("headings", [])
    if not headings:
        return "na", "Aucun titre"
    bad = [h for h in headings if h.get("tag") not in ("H1", "H2", "H3", "H4", "H5", "H6") and h.get("role") != "heading"]
    if bad:
        return "fail", f"{len(bad)} titre(s) sans balise hx ni role=heading"
    return "pass", f"{len(headings)} titre(s) structurés via hx/role=heading"


def ev_9_2_1(d):
    lm = t9(d).get("landmarks", {})
    issues = []
    if not lm.get("hasHeader"):
        issues.append("pas de header")
    if lm.get("navCount", 0) < 1:
        issues.append("pas de nav")
    if not lm.get("hasMain"):
        issues.append("pas de main")
    if not lm.get("hasFooter"):
        issues.append("pas de footer")
    if lm.get("navMisuse", 0):
        issues.append(f"{lm['navMisuse']} nav mal utilisé(s)")
    if t9(d).get("navOutsideNav"):
        issues.append("navigation hors nav")
    if issues:
        return "fail", "; ".join(issues)
    return "pass", f"Landmarks: header, {lm['navCount']} nav, main, footer"


def ev_9_3_1(d):
    bad = t9(d).get("lists", {}).get("badUlOl", [])
    if bad:
        return "fail", f"{len(bad)} liste(s) non ordonnée(s) mal structurée(s)"
    return "pass", f"{t9(d).get('lists', {}).get('ul', 0)} liste(s) ul/role=list correctement structurée(s)"


def ev_9_3_2(d):
    bad = t9(d).get("lists", {}).get("badUlOl", [])
    if bad:
        return "fail", f"{len(bad)} liste(s) ordonnée(s) mal structurée(s)"
    return "pass", f"{t9(d).get('lists', {}).get('ol', 0)} liste(s) ol correctement structurée(s)"


def ev_9_3_3(d):
    bad = t9(d).get("lists", {}).get("badDl", [])
    dl = t9(d).get("lists", {}).get("dl", 0)
    if not dl:
        return "na", "Aucune liste de description"
    if bad:
        return "fail", f"{len(bad)} dl mal structurée(s)"
    return "pass", f"{dl} liste(s) dl/dt/dd correctement structurée(s)"


def ev_9_4_1(d):
    inline = t9(d).get("quotes", {}).get("inlineCitations", [])
    q = t9(d).get("quotes", {}).get("q", [])
    if not inline:
        return "na", "Aucune citation courte détectée"
    if len(q) < len(inline):
        return "fail", f"{len(inline)} citation(s) courte(s) sans balise q"
    return "pass", f"{len(q)} citation(s) courte(s) avec balise q"


def ev_9_4_2(d):
    blocks = t9(d).get("quotes", {}).get("blockCitations", [])
    bq = t9(d).get("quotes", {}).get("blockquote", [])
    if not blocks and not bq:
        return "na", "Aucun bloc de citation"
    unmarked = [b for b in blocks if not b.get("hasBlockquote")]
    if unmarked:
        return "fail", f"{len(unmarked)} bloc(s) citation sans blockquote"
    return "pass", f"{len(bq)} blockquote(s) présent(s)"


EVALUATORS = {
    "9.1.1": ("9.1", ev_9_1_1),
    "9.1.2": ("9.1", ev_9_1_2),
    "9.1.3": ("9.1", ev_9_1_3),
    "9.2.1": ("9.2", ev_9_2_1),
    "9.3.1": ("9.3", ev_9_3_1),
    "9.3.2": ("9.3", ev_9_3_2),
    "9.3.3": ("9.3", ev_9_3_3),
    "9.4.1": ("9.4", ev_9_4_1),
    "9.4.2": ("9.4", ev_9_4_2),
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
                "--theme", "9", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 9: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
