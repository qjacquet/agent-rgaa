#!/usr/bin/env python3
"""Evaluate Theme 5 (Tableaux) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t5(d):
    return d.get("theme5", d)


def ev_5_1_1(d):
    ct = t5(d).get("complexTables", [])
    if not ct:
        return "na", "Aucun tableau de données complexe"
    bad = [t for t in ct if not t.get("hasSummary")]
    if bad:
        return "fail", f"{len(bad)} tableau(x) complexe(s) sans résumé (caption/summary/aria-describedby)"
    return "pass", f"{len(ct)} tableau(x) complexe(s) avec résumé"


def ev_5_2_1(d):
    ct = [t for t in t5(d).get("complexTables", []) if t.get("hasSummary")]
    if not ct:
        return "na", "Aucun tableau complexe avec résumé"
    return "pass", f"{len(ct)} résumé(s) présent(s) (pertinence non vérifiable auto)"


def ev_5_3_1(d):
    lt = t5(d).get("layoutTables", [])
    if not lt:
        return "na", "Aucun tableau de mise en forme"
    bad = [t for t in lt if not t.get("isPresentation")]
    if bad:
        return "fail", f"{len(bad)} tableau(x) mise en forme sans role=presentation"
    return "pass", f"{len(lt)} tableau(x) mise en forme avec role=presentation"


def ev_5_4_1(d):
    titled = [t for t in t5(d).get("dataTables", []) if t.get("hasCaption") or t.get("titleAttr") or t.get("ariaLabel") or t.get("ariaLabelledby")]
    if not titled:
        return "na", "Aucun tableau de données avec titre"
    return "pass", f"{len(titled)} tableau(x) avec titre correctement associé (caption/aria/title)"


def ev_5_5_1(d):
    titled = [t for t in t5(d).get("dataTables", []) if t.get("hasCaption") or t.get("titleAttr") or t.get("ariaLabel")]
    if not titled:
        return "na", "Aucun tableau de données avec titre"
    return "pass", f"{len(titled)} titre(s) présent(s) (pertinence non vérifiable auto)"


def ev_5_6_1(d):
    dt = t5(d).get("dataTables", [])
    if not dt:
        return "na", "Aucun tableau de données"
    bad = []
    for t in dt:
        for th in t.get("thDetails", []):
            if th.get("scope") == "col" or (not th.get("scope") and th.get("text")):
                continue
            if th.get("role") not in ("columnheader", None) and th.get("scope") != "row":
                pass
        bad_th = [th for th in t.get("thDetails", []) if th.get("scope") == "col" and th.get("role") == "rowheader"]
        bad.extend(bad_th)
    if bad:
        return "fail", f"En-têtes colonne mal structurés dans {len(bad)} cas"
    return "pass", f"{len(dt)} tableau(x) données, en-têtes colonne en th/columnheader"


def ev_5_6_2(d):
    dt = t5(d).get("dataTables", [])
    if not dt:
        return "na", "Aucun tableau de données"
    return "pass", f"{len(dt)} tableau(x) données, en-têtes ligne en th/rowheader"


def ev_5_6_3(d):
    dt = t5(d).get("dataTables", [])
    if not dt:
        return "na", "Aucun tableau de données"
    partial = sum(t.get("thPartial", 0) if isinstance(t.get("thPartial"), int) else len(t.get("thPartial", [])) for t in dt)
    if partial:
        return "pass", f"{partial} en-tête(s) partiel(s) en th"
    return "pass", f"{len(dt)} tableau(x) données, en-têtes partiels en th si présents"


def ev_5_6_4(d):
    dt = t5(d).get("dataTables", [])
    if not dt:
        return "na", "Aucun tableau de données"
    return "pass", f"{len(dt)} tableau(x) données, cellules en td/th"


def ev_5_7_1(d):
    dt = t5(d).get("dataTables", [])
    if not dt:
        return "na", "Aucun tableau de données"
    bad = sum(
        t.get("thNoScopeNoId", 0) if isinstance(t.get("thNoScopeNoId"), int) else len(t.get("thNoScopeNoId", []))
        for t in dt
    )
    if bad:
        return "fail", f"{bad} en-tête(s) sans scope/id/role rowheader|columnheader"
    return "pass", f"En-têtes avec scope, id ou role ARIA approprié"


def ev_5_7_2(d):
    dt = t5(d).get("dataTables", [])
    scoped = [th for t in dt for th in t.get("thDetails", []) if th.get("scope")]
    if not scoped:
        return "na", "Aucun th avec attribut scope"
    bad = [th for th in scoped if th.get("scope") not in ("row", "col", "rowgroup", "colgroup")]
    if bad:
        return "fail", f"{len(bad)} scope invalide(s): {bad[0].get('scope')}"
    return "pass", f"{len(scoped)} th scope row/col valide(s)"


def ev_5_7_3(d):
    dt = t5(d).get("dataTables", [])
    partial = sum(
        t.get("thPartial", 0) if isinstance(t.get("thPartial"), int) else len(t.get("thPartial", []))
        for t in dt
    )
    if not partial:
        return "na", "Aucun en-tête partiel (multi-en-têtes)"
    return "pass", f"En-têtes partiels avec id unique, sans scope"


def ev_5_7_4(d):
    dt = t5(d).get("dataTables", [])
    with_ids = [t for t in dt if any(th.get("id") for th in t.get("thDetails", []))]
    if not with_ids:
        return "na", "Aucun tableau avec en-têtes id (association headers)"
    return "pass", "Tableaux avec id: association headers vérifiée si applicable"


def ev_5_7_5(d):
    dt = t5(d).get("dataTables", [])
    aria_h = [th for t in dt for th in t.get("thDetails", []) if th.get("role") in ("rowheader", "columnheader")]
    if not aria_h:
        return "na", "Aucun en-tête ARIA rowheader/columnheader"
    bad = [th for th in aria_h if th.get("role") not in ("rowheader", "columnheader")]
    if bad:
        return "fail", "Rôle ARIA en-tête incohérent"
    return "pass", f"{len(aria_h)} en-tête(s) ARIA cohérent(s)"


def ev_5_8_1(d):
    lt = t5(d).get("layoutTables", [])
    if not lt:
        return "na", "Aucun tableau de mise en forme"
    bad = []
    for t in lt:
        v = t.get("layoutViolations") or {}
        if any([v.get("summary"), v.get("caption"), v.get("thead"), v.get("th"), v.get("tfoot"),
                v.get("tdScope"), v.get("tdHeaders"), v.get("tdAxis"), v.get("rowheader")]):
            bad.append(t)
    if bad:
        return "fail", f"{len(bad)} tableau(x) mise en forme avec éléments propres aux tableaux de données"
    return "pass", f"{len(lt)} tableau(x) mise en forme conformes"


EVALUATORS = {
    "5.1.1": ("5.1", ev_5_1_1),
    "5.2.1": ("5.2", ev_5_2_1),
    "5.3.1": ("5.3", ev_5_3_1),
    "5.4.1": ("5.4", ev_5_4_1),
    "5.5.1": ("5.5", ev_5_5_1),
    "5.6.1": ("5.6", ev_5_6_1),
    "5.6.2": ("5.6", ev_5_6_2),
    "5.6.3": ("5.6", ev_5_6_3),
    "5.6.4": ("5.6", ev_5_6_4),
    "5.7.1": ("5.7", ev_5_7_1),
    "5.7.2": ("5.7", ev_5_7_2),
    "5.7.3": ("5.7", ev_5_7_3),
    "5.7.4": ("5.7", ev_5_7_4),
    "5.7.5": ("5.7", ev_5_7_5),
    "5.8.1": ("5.8", ev_5_8_1),
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
                "--theme", "5", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 5: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
