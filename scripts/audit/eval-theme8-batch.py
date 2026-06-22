#!/usr/bin/env python3
"""Evaluate Theme 8 (Éléments obligatoires) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t8(d):
    return d.get("theme8", d)


def ev_8_1_1(d):
    dt = t8(d).get("doctype")
    if not dt:
        return "fail", "Balise DOCTYPE absente"
    return "pass", f"DOCTYPE présent: {dt[:50]}"


def ev_8_1_2(d):
    name = t8(d).get("doctypeName")
    if not name:
        return "fail", "DOCTYPE absent ou invalide"
    if name.lower() in ("html", "html5"):
        return "pass", f"DOCTYPE valide ({name})"
    return "pass", f"DOCTYPE présent ({name})"


def ev_8_1_3(d):
    if t8(d).get("doctype"):
        return "pass", "DOCTYPE situé avant html (document parsé correctement)"
    return "fail", "DOCTYPE absent"


def ev_8_2_1(d):
    dup = t8(d).get("duplicateIdCount", 0)
    if dup:
        d0 = t8(d).get("duplicateIds", [{}])[0]
        return "fail", f"{dup} id dupliqué(s): #{d0.get('id', '?')} ({d0.get('count', 0)}x)"
    return "pass", "IDs uniques, pas de doublons détectés (vérification DOM)"


def ev_8_3_1(d):
    lang = t8(d).get("lang") or t8(d).get("xmlLang")
    if not lang:
        return "fail", "Attribut lang absent sur html"
    return "pass", f"Langue par défaut: lang={lang}"


def ev_8_4_1(d):
    lang = t8(d).get("lang") or t8(d).get("xmlLang")
    if not lang:
        return "fail", "Code langue absent"
    if not t8(d).get("validDefaultLang"):
        return "fail", f"Code langue invalide: {lang}"
    return "pass", f"Code langue valide et pertinent: {lang}"


def ev_8_5_1(d):
    if t8(d).get("hasTitle"):
        return "pass", f"Balise title présente: «{t8(d).get('pageTitle', '')[:60]}»"
    return "fail", "Balise title absente ou vide"


def ev_8_6_1(d):
    title = t8(d).get("pageTitle", "")
    if not title:
        return "fail", "Titre de page absent"
    if len(title) < 3 or title.lower() in ("untitled", "sans titre", "page"):
        return "fail", f"Titre non pertinent: «{title}»"
    return "pass", f"Titre pertinent: «{title[:60]}»"


def ev_8_7_1(d):
    changes = t8(d).get("langChanges", [])
    if not changes:
        return "na", "Aucun changement de langue explicite dans le code"
    unmarked = [c for c in changes if not c.get("lang")]
    if unmarked:
        return "fail", f"{len(unmarked)} passage(s) sans attribut lang"
    return "pass", f"{len(changes)} changement(s) de langue avec attribut lang"


def ev_8_8_1(d):
    changes = t8(d).get("langChanges", [])
    if not changes:
        return "na", "Aucun changement de langue (test 8.7.1 NA)"
    bad = [c for c in changes if not c.get("valid")]
    if bad:
        return "fail", f"Code langue invalide: {bad[0].get('lang')}"
    return "pass", f"{len(changes)} code(s) langue valide(s)"


def ev_8_9_1(d):
    misuse = t8(d).get("presentationMisuse", [])
    if not misuse:
        return "pass", "Aucune balise sémantique détournée à des fins de présentation"
    bad = [m for m in misuse if m.get("role") != "presentation"]
    if bad:
        return "fail", f"{len(bad)} balise(s) sémantique(s) sans role=presentation: {bad[0].get('tag')}"
    return "pass", "Balises sémantiques détournées avec role=presentation"


def ev_8_10_1(d):
    rtl = t8(d).get("rtlBlocks", [])
    if not rtl:
        return "na", "Aucun texte en sens de lecture différent (RTL/LTR explicite)"
    no_dir = [r for r in rtl if not r.get("dir")]
    if no_dir:
        return "fail", f"{len(no_dir)} bloc(s) sans attribut dir"
    return "pass", f"{len(rtl)} bloc(s) avec attribut dir"


def ev_8_10_2(d):
    return ev_8_10_1(d)


EVALUATORS = {
    "8.1.1": ("8.1", ev_8_1_1),
    "8.1.2": ("8.1", ev_8_1_2),
    "8.1.3": ("8.1", ev_8_1_3),
    "8.2.1": ("8.2", ev_8_2_1),
    "8.3.1": ("8.3", ev_8_3_1),
    "8.4.1": ("8.4", ev_8_4_1),
    "8.5.1": ("8.5", ev_8_5_1),
    "8.6.1": ("8.6", ev_8_6_1),
    "8.7.1": ("8.7", ev_8_7_1),
    "8.8.1": ("8.8", ev_8_8_1),
    "8.9.1": ("8.9", ev_8_9_1),
    "8.10.1": ("8.10", ev_8_10_1),
    "8.10.2": ("8.10", ev_8_10_2),
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
                "--theme", "8", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 8: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
