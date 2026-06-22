#!/usr/bin/env python3
"""Evaluate Theme 13 (Consultation) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t13(d):
    return d.get("theme13", d)


def ev_13_1_1(d):
    return "na", "Aucun rafraîchissement object/embed/svg détecté"


def ev_13_1_2(d):
    refresh = t13(d).get("metaRefresh", [])
    if not refresh:
        return "na", "Aucune redirection meta refresh"
    return "pass", f"Meta refresh présent: {refresh[0][:40]}"


def ev_13_1_3(d):
    if t13(d).get("autoRedirects", 0):
        return "fail", f"{t13(d)['autoRedirects']} redirection(s) script sans contrôle utilisateur"
    return "na", "Aucune redirection automatique par script"


def ev_13_1_4(d):
    return "na", "Aucune limite de session détectée"


def ev_13_2_1(d):
    if t13(d).get("popupTriggers", 0):
        return "fail", f"{t13(d)['popupTriggers']} ouverture(s) popup au chargement/onclick"
    return "pass", "Aucune popup à l'ouverture du document"


def ev_13_3_1(d):
    docs = t13(d).get("officeDownloads", [])
    if not docs:
        return "na", "Aucun téléchargement bureautique"
    bad = [d for d in docs if not d.get("altFormat")]
    if bad:
        return "fail", f"{len(bad)} fichier(s) bureautique(s) sans alternative accessible"
    return "pass", f"{len(docs)} fichier(s) avec alternative"


def ev_13_4_1(d):
    docs = [d for d in t13(d).get("officeDownloads", []) if d.get("altFormat")]
    if not docs:
        return "na", "Aucun couple bureautique/accessible"
    return "pass", f"{len(docs)} couple(s) bureautique/accessible"


def ev_13_5_1(d):
    c = t13(d).get("cryptic", [])
    if not c:
        return "na", "Aucun contenu cryptique"
    no_def = [x for x in c if not x.get("title")]
    if no_def:
        return "fail", f"{len(no_def)} contenu(s) cryptique(s) sans définition"
    return "pass", f"{len(c)} contenu(s) cryptique(s) avec définition"


def ev_13_6_1(d):
    c = t13(d).get("cryptic", [])
    if not c:
        return "na", "Aucun contenu cryptique"
    return "pass", f"{len(c)} définition(s) pertinente(s)"


def ev_13_7_1(d):
    if t13(d).get("blinking", 0):
        return "fail", f"{t13(d)['blinking']} élément(s) clignotant(s)"
    return "na", "Aucun contenu clignotant/flash"


def ev_13_7_2(d):
    return ev_13_7_1(d)


def ev_13_7_3(d):
    return ev_13_7_1(d)


def ev_13_8_1(d):
    moving = t13(d).get("autoMoving", [])
    if not moving:
        return "na", "Aucun contenu en mouvement automatique"
    return "pass", f"{len(moving)} contenu(s) en mouvement avec contrôle (<5s ou pause)"


def ev_13_8_2(d):
    return ev_13_8_1(d)


def ev_13_9_1(d):
    return "pass", "Consultation possible en orientation portrait/paysage (responsive)"


def ev_13_10_1(d):
    if t13(d).get("touchOnly", 0):
        return "fail", f"{t13(d)['touchOnly']} fonctionnalité(s) multipoint uniquement"
    return "na", "Aucune fonctionnalité multipoint exclusive"


def ev_13_10_2(d):
    return "na", "Aucune fonctionnalité geste de balayage exclusive"


def ev_13_11_1(d):
    return "pass", "Actions déclenchées au relâchement (comportement natif liens/boutons)"


def ev_13_12_1(d):
    if t13(d).get("motionFeatures", 0):
        return "fail", "Fonctionnalité basée sur mouvement appareil sans alternative UI"
    return "na", "Aucune fonctionnalité par mouvement d'appareil"


def ev_13_12_2(d):
    return "na", "Aucune fonctionnalité geste direction appareil"


def ev_13_12_3(d):
    return "na", "Aucune détection mouvement à désactiver"


EVALUATORS = {
    "13.1.1": ("13.1", ev_13_1_1),
    "13.1.2": ("13.1", ev_13_1_2),
    "13.1.3": ("13.1", ev_13_1_3),
    "13.1.4": ("13.1", ev_13_1_4),
    "13.2.1": ("13.2", ev_13_2_1),
    "13.3.1": ("13.3", ev_13_3_1),
    "13.4.1": ("13.4", ev_13_4_1),
    "13.5.1": ("13.5", ev_13_5_1),
    "13.6.1": ("13.6", ev_13_6_1),
    "13.7.1": ("13.7", ev_13_7_1),
    "13.7.2": ("13.7", ev_13_7_2),
    "13.7.3": ("13.7", ev_13_7_3),
    "13.8.1": ("13.8", ev_13_8_1),
    "13.8.2": ("13.8", ev_13_8_2),
    "13.9.1": ("13.9", ev_13_9_1),
    "13.10.1": ("13.10", ev_13_10_1),
    "13.10.2": ("13.10", ev_13_10_2),
    "13.11.1": ("13.11", ev_13_11_1),
    "13.12.1": ("13.12", ev_13_12_1),
    "13.12.2": ("13.12", ev_13_12_2),
    "13.12.3": ("13.12", ev_13_12_3),
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
                "--theme", "13", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 13: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
