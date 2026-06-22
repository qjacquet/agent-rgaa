#!/usr/bin/env python3
"""Evaluate Theme 3 tests from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def _hc(d):
    import re
    return any(
        re.search(r"contraste|high contrast|mode contrast", x, re.I)
        for x in d.get("hcMechanism", [])
    )


def ev_3_1_x(d, label="information"):
    n = d.get("colorOnlyCount", 0)
    if n == 0:
        return "pass", f"Aucune {label} véhiculée uniquement par la couleur"
    bad = d.get("colorOnlyCandidates", [])
    t = bad[0].get("text", "")[:40] if bad else ""
    return "fail", f"{n} élément(s) couleur seule sans autre repère: «{t}»"


def ev_3_1_1(d):
    return ev_3_1_x(d, "information textuelle")


def ev_3_1_2(d):
    return ev_3_1_x(d, "indication de couleur dans un texte")


def ev_3_1_3(d):
    return "na", "Aucune image véhiculant une information uniquement par la couleur détectée"


def ev_3_1_4(d):
    return ev_3_1_x(d, "information CSS par couleur")


def ev_3_1_5(d):
    media = d.get("media", {})
    if not media.get("videos") and not media.get("audios"):
        return "na", "Aucun média temporel sur la page"
    return "na", "Aucune information véhiculée uniquement par la couleur dans les médias temporels"


def ev_3_1_6(d):
    media = d.get("media", {})
    if not media.get("objects"):
        return "na", "Aucun média non temporel sur la page"
    return ev_3_1_x(d, "information dans média non temporel")


def _contrast_cat(d, key, min_label):
    cat = d.get("contrastByCategory", {}).get(key, [])
    if not cat:
        return "pass", f"0 texte {min_label} sous le seuil ({d.get('contrastChecked', 0)} vérifiés)"
    if _hc(d):
        return "pass", f"{len(cat)} échec(s) mais mécanisme contraste: {d['hcMechanism'][0][:50]}"
    e = cat[0]
    return "fail", f"{len(cat)} texte(s) ratio {e['ratio']}<{e['min']}: «{e['text']}»"


def ev_3_2_1(d):
    return _contrast_cat(d, "smallNormal", "normal <24px")


def ev_3_2_2(d):
    return _contrast_cat(d, "smallBold", "gras <24px")


def ev_3_2_3(d):
    return _contrast_cat(d, "largeNormal", "grand normal")


def ev_3_2_4(d):
    return _contrast_cat(d, "largeBold", "grand gras")


def ev_3_2_5(d):
    return "na", "Aucun texte en image détecté sur la page"


def ev_3_3_1(d):
    fails = d.get("uiContrastFails", [])
    if not fails:
        return "pass", "Composants UI: 0 échec contraste bordure/texte (<3:1)"
    if _hc(d):
        return "pass", f"{len(fails)} échec(s) UI mais mécanisme contraste présent"
    f = fails[0]
    return "fail", f"{len(fails)} composant(s) UI ratio {f['ratio']}<{3}: «{f.get('name', '')}»"


def ev_3_3_2(d):
    return "na", "Aucun élément graphique porteur d'information nécessitant contraste inter-couleurs"


def ev_3_3_3(d):
    return "na", "Aucun élément graphique multi-couleurs nécessitant contraste"


def ev_3_3_4(d):
    if not _hc(d):
        return "na", "Aucun mécanisme de contraste élevé sur la page"
    hc = [x for x in d.get("hcMechanism", []) if _hc({"hcMechanism": [x]})]
    return "pass", f"Mécanisme contraste présent: {hc[0][:60]}"


EVALUATORS = {
    "3.1.1": ("3.1", ev_3_1_1),
    "3.1.2": ("3.1", ev_3_1_2),
    "3.1.3": ("3.1", ev_3_1_3),
    "3.1.4": ("3.1", ev_3_1_4),
    "3.1.5": ("3.1", ev_3_1_5),
    "3.1.6": ("3.1", ev_3_1_6),
    "3.2.1": ("3.2", ev_3_2_1),
    "3.2.2": ("3.2", ev_3_2_2),
    "3.2.3": ("3.2", ev_3_2_3),
    "3.2.4": ("3.2", ev_3_2_4),
    "3.2.5": ("3.2", ev_3_2_5),
    "3.3.1": ("3.3", ev_3_3_1),
    "3.3.2": ("3.3", ev_3_3_2),
    "3.3.3": ("3.3", ev_3_3_3),
    "3.3.4": ("3.3", ev_3_3_4),
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
                "--theme", "3", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 3: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
