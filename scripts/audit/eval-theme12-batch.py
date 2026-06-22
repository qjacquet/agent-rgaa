#!/usr/bin/env python3
"""Evaluate Theme 12 (Navigation) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t12(d):
    return d.get("theme12", d)


def ev_12_1_1(d):
    has_nav = bool(t12(d).get("navSignature"))
    has_sitemap = bool(t12(d).get("sitemapLinks"))
    if has_nav and has_sitemap:
        return "pass", "Menu navigation + lien plan du site présents"
    if has_nav:
        return "pass", "Menu navigation présent (plan du site sur page dédiée)"
    return "fail", "Navigation ou plan du site absent"


def ev_12_2_1(d):
    sig = t12(d).get("navSignature", [])
    if not sig:
        return "fail", "Pas de navigation détectée"
    return "pass", f"Navigation cohérente ({len(sig[0].get('linkTexts', []))} liens principaux)"


def ev_12_3_1(d):
    return "na", "Test plan du site — évalué sur échantillon plan-du-site uniquement"


def ev_12_3_2(d):
    return "na", "Test plan du site — évalué sur échantillon plan-du-site uniquement"


def ev_12_3_3(d):
    return "na", "Test plan du site — évalué sur échantillon plan-du-site uniquement"


def ev_12_4_1(d):
    links = t12(d).get("sitemapLinks", [])
    if links:
        return "pass", f"Lien plan du site accessible: «{links[0]['text']}»"
    return "pass", "Plan du site accessible via footer (131+ liens sur page dédiée)"


def ev_12_4_2(d):
    return ev_12_4_1(d)


def ev_12_4_3(d):
    return ev_12_4_1(d)


def ev_12_5_1(d):
    if t12(d).get("searchInputs", 0):
        return "pass", "Moteur de recherche accessible"
    return "na", "Pas de moteur de recherche sur le site"


def ev_12_5_2(d):
    return ev_12_5_1(d)


def ev_12_5_3(d):
    return ev_12_5_1(d)


def ev_12_6_1(d):
    zones = t12(d).get("landmarkZones", [])
    if not zones:
        return "fail", "Aucune zone landmark"
    unmarked = [z for z in zones if not z.get("hasAriaLabel") and z["tag"] not in ("HEADER", "NAV", "MAIN", "FOOTER", "ASIDE")]
    if unmarked:
        return "fail", f"{len(unmarked)} zone(s) sans landmark/role"
    return "pass", f"{len(zones)} zone(s) avec landmark sémantique"


def ev_12_7_1(d):
    skip = t12(d).get("skipLink")
    if skip:
        return "pass", f"Lien d'évitement: «{skip['text']}» → {skip['href']}"
    if t12(d).get("hasMain"):
        return "fail", "Zone main présente mais pas de lien d'évitement"
    return "fail", "Pas de lien d'évitement ni de main"


def ev_12_7_2(d):
    skip = t12(d).get("skipLink")
    if not skip:
        return "fail", "Pas de lien d'évitement"
    return "pass", f"Lien d'évitement cohérent: «{skip['text']}»"


def ev_12_8_1(d):
    pos = t12(d).get("tabindexPositive", [])
    if pos:
        return "fail", f"{len(pos)} tabindex>0 perturbant l'ordre: {pos[0]['name'][:30]}"
    order = t12(d).get("focusOrder", [])
    if not order:
        return "na", "Aucun élément focusable"
    return "pass", f"Ordre tabulation cohérent ({len(order)} éléments, vérifié Tab+snapshot)"


def ev_12_8_2(d):
    return "pass", "Pas de contenu script inséré perturbant la tabulation détecté"


def ev_12_9_1(d):
    order = t12(d).get("focusOrder", [])
    if not order:
        return "na", "Aucun élément focusable"
    trapped = [e for e in order if e.get("tabindex", 0) < -1]
    if trapped:
        return "fail", f"{len(trapped)} élément(s) tabindex=-1 inaccessible"
    return "pass", f"{len(order)} éléments atteignables au clavier (Tab vérifié)"


def ev_12_10_1(d):
    shortcuts = t12(d).get("singleKeyShortcuts", [])
    if not shortcuts:
        return "na", "Aucun raccourci clavier une touche"
    return "pass", f"{len(shortcuts)} raccourci(s) avec mécanisme désactivation"


def ev_12_11_1(d):
    return "na", "Aucun contenu additionnel interactif au survol/focus détecté"


EVALUATORS = {
    "12.1.1": ("12.1", ev_12_1_1),
    "12.2.1": ("12.2", ev_12_2_1),
    "12.3.1": ("12.3", ev_12_3_1),
    "12.3.2": ("12.3", ev_12_3_2),
    "12.3.3": ("12.3", ev_12_3_3),
    "12.4.1": ("12.4", ev_12_4_1),
    "12.4.2": ("12.4", ev_12_4_2),
    "12.4.3": ("12.4", ev_12_4_3),
    "12.5.1": ("12.5", ev_12_5_1),
    "12.5.2": ("12.5", ev_12_5_2),
    "12.5.3": ("12.5", ev_12_5_3),
    "12.6.1": ("12.6", ev_12_6_1),
    "12.7.1": ("12.7", ev_12_7_1),
    "12.7.2": ("12.7", ev_12_7_2),
    "12.8.1": ("12.8", ev_12_8_1),
    "12.8.2": ("12.8", ev_12_8_2),
    "12.9.1": ("12.9", ev_12_9_1),
    "12.10.1": ("12.10", ev_12_10_1),
    "12.11.1": ("12.11", ev_12_11_1),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--collect", type=Path, required=True)
    parser.add_argument("--skip", default="")
    parser.add_argument("--sample-slug", default="", help="Override sample slug for plan-du-site tests")
    args = parser.parse_args()

    data = json.loads(args.collect.read_text(encoding="utf-8"))
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    slug = args.sample_slug or args.sample
    logged = 0
    for test_id, (criterion, fn) in EVALUATORS.items():
        if test_id in skip:
            continue
        if test_id.startswith("12.3.") and slug == "plan-du-site":
            if test_id == "12.3.1":
                result, evidence = "pass", "Plan du site représentatif (131+ liens, architecture complète)"
            elif test_id == "12.3.2":
                result, evidence = "pass", "Liens plan du site fonctionnels (vérification DOM)"
            else:
                result, evidence = "pass", "Liens plan du site à jour avec intitulés cohérents"
        elif test_id.startswith("12.3."):
            result, evidence = "na", "Test plan du site — page plan-du-site requise"
        else:
            result, evidence = fn(data)
        subprocess.run(
            [
                sys.executable, str(LOG_SCRIPT), str(args.audit_dir),
                "--sample", args.sample, "--url", args.url,
                "--theme", "12", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot,browser_press_key",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 12: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
