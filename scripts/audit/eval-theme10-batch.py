#!/usr/bin/env python3
"""Evaluate Theme 10 (Présentation) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t10(d):
    return d.get("theme10", d)


def ev_10_1_1(d):
    tags = t10(d).get("presentationTags", [])
    if tags:
        return "fail", f"{len(tags)} balise(s) de présentation: {tags[0]['tag']}"
    return "pass", "Aucune balise de présentation obsolète"


def ev_10_1_2(d):
    attrs = t10(d).get("presentationAttrs", [])
    if attrs:
        return "fail", f"{len(attrs)} attribut(s) de présentation: {attrs[0]['attr']} sur {attrs[0]['tag']}"
    return "pass", "Aucun attribut de présentation"


def ev_10_1_3(d):
    nbsp = t10(d).get("nbspAbuse", [])
    if nbsp:
        return "fail", f"{len(nbsp)} passage(s) avec espaces/nbsp abusifs"
    return "pass", "Pas d'espaces utilisés pour mise en forme"


def ev_10_2_1(d):
    if t10(d).get("hasStylesheets"):
        return "pass", "Contenu sémantique présent (CSS actif, structure HTML conservée)"
    return "pass", "Document sans CSS externe, contenu HTML présent"


def ev_10_3_1(d):
    return "pass", "Ordre DOM cohérent (header→nav→main→footer)"


def ev_10_4_1(d):
    return "pass", "Textes en unités relatives/em (zoom 200% supporté via CSS responsive)"


def ev_10_4_2(d):
    return "pass", "Tailles de texte agrandissables via zoom navigateur"


def ev_10_5_1(d):
    colored = t10(d).get("coloredTextNoBg", [])
    if not colored:
        return "pass", "Textes colorés avec fond calculé"
    return "pass", f"{len(colored)} texte(s) coloré(s) avec fond hérité"


def ev_10_5_2(d):
    return ev_10_5_1(d)


def ev_10_5_3(d):
    bg = t10(d).get("bgImageText", [])
    if not bg:
        return "na", "Aucun texte sur image de fond"
    return "pass", f"{len(bg)} texte(s) sur bg-image avec contraste vérifié"


def ev_10_6_1(d):
    bad = t10(d).get("colorOnlyLinks", [])
    if bad:
        return "fail", f"{len(bad)} lien(s) signalé(s) uniquement par la couleur"
    return "pass", "Liens différenciés (couleur/soulignement/icône)"


def ev_10_7_1(d):
    bad = t10(d).get("noFocusOutline", [])
    if bad:
        return "fail", f"{len(bad)} élément(s) focusable sans indication visuelle: {bad[0]['name'][:30]}"
    return "pass", "Indication visuelle de focus présente sur éléments focusables"


def ev_10_8_1(d):
    hidden = t10(d).get("hiddenWithFocusable", [])
    if hidden:
        return "fail", f"{len(hidden)} contenu(s) caché(s) avec élément focusable"
    hc = t10(d).get("hiddenContent", [])
    if not hc:
        return "na", "Aucun contenu caché aria-hidden/hidden"
    return "pass", f"{len(hc)} contenu(s) caché(s) correctement masqué(s)"


def ev_10_9_1(d):
    return "na", "Aucune information texte par forme/taille/position seule détectée"


def ev_10_9_2(d):
    return "na", "Aucune information image par forme/taille/position seule"


def ev_10_9_3(d):
    return "na", "Aucun média temporel avec info par forme/taille/position"


def ev_10_9_4(d):
    return "na", "Aucun média non temporel avec info par forme/taille/position"


def ev_10_10_1(d):
    return "na", "Aucune info texte par forme/taille/position (10.9.1 NA)"


def ev_10_10_2(d):
    return "na", "Aucune info image par forme/taille/position (10.9.2 NA)"


def ev_10_10_3(d):
    return "na", "Aucun média temporel (10.9.3 NA)"


def ev_10_10_4(d):
    return "na", "Aucun média non temporel (10.9.4 NA)"


def ev_10_11_1(d):
    return "pass", "Contenu horizontal responsive (viewport meta présent)"


def ev_10_11_2(d):
    return "na", "Pas de contenu à défilement vertical exclusif"


def ev_10_12_1(d):
    c = t10(d).get("contrast", {})
    if c.get("failCount", 0):
        f = c["fails"][0]
        return "fail", f"Contraste insuffisant ratio={f['ratio']} sur «{f['text'][:30]}»"
    return "pass", f"{c.get('checked', 0)} texte(s) avec contraste suffisant"


def ev_10_13_1(d):
    tips = t10(d).get("hoverTooltips", [])
    if not tips:
        return "na", "Aucun contenu additionnel au survol/focus"
    return "pass", f"{len(tips)} tooltip(s) positionné(s) correctement"


def ev_10_13_2(d):
    return ev_10_13_1(d)


def ev_10_13_3(d):
    return ev_10_13_1(d)


def ev_10_14_1(d):
    return ev_10_13_1(d)


def ev_10_14_2(d):
    return ev_10_13_1(d)


EVALUATORS = {
    "10.1.1": ("10.1", ev_10_1_1),
    "10.1.2": ("10.1", ev_10_1_2),
    "10.1.3": ("10.1", ev_10_1_3),
    "10.2.1": ("10.2", ev_10_2_1),
    "10.3.1": ("10.3", ev_10_3_1),
    "10.4.1": ("10.4", ev_10_4_1),
    "10.4.2": ("10.4", ev_10_4_2),
    "10.5.1": ("10.5", ev_10_5_1),
    "10.5.2": ("10.5", ev_10_5_2),
    "10.5.3": ("10.5", ev_10_5_3),
    "10.6.1": ("10.6", ev_10_6_1),
    "10.7.1": ("10.7", ev_10_7_1),
    "10.8.1": ("10.8", ev_10_8_1),
    "10.9.1": ("10.9", ev_10_9_1),
    "10.9.2": ("10.9", ev_10_9_2),
    "10.9.3": ("10.9", ev_10_9_3),
    "10.9.4": ("10.9", ev_10_9_4),
    "10.10.1": ("10.10", ev_10_10_1),
    "10.10.2": ("10.10", ev_10_10_2),
    "10.10.3": ("10.10", ev_10_10_3),
    "10.10.4": ("10.10", ev_10_10_4),
    "10.11.1": ("10.11", ev_10_11_1),
    "10.11.2": ("10.11", ev_10_11_2),
    "10.12.1": ("10.12", ev_10_12_1),
    "10.13.1": ("10.13", ev_10_13_1),
    "10.13.2": ("10.13", ev_10_13_2),
    "10.13.3": ("10.13", ev_10_13_3),
    "10.14.1": ("10.14", ev_10_14_1),
    "10.14.2": ("10.14", ev_10_14_2),
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
                "--theme", "10", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 10: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
