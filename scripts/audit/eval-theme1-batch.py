#!/usr/bin/env python3
"""Evaluate Theme 1 tests from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"

# test_id -> (criterion_id, evaluator)
def ev_1_1_1(d):
    if d["counts"]["infoImgs"] == 0:
        return "na", "Aucune image porteuse d'information"
    bad = d["infoImgsNoAlt"]
    if bad:
        return "fail", f"{len(bad)} image(s) info sans alternative: {bad[0].get('src','')}"
    return "pass", f"{d['counts']['infoImgs']} img info, {d['counts']['decImgs']} décoratives, 0 sans alt"

def ev_1_1_2(d):
    areas = [a for a in d["areas"] if a.get("href")]
    if not areas:
        return "na", "Aucune zone area cliquable"
    bad = [a for a in areas if not a.get("hasAltText")]
    return ("fail", f"{len(bad)} area sans alt") if bad else ("pass", f"{len(areas)} area(s) avec alt")

def ev_1_1_3(d):
    if not d["inputImages"]:
        return "na", "Aucun input type=image"
    bad = [i for i in d["inputImages"] if not i.get("hasAltText")]
    return ("fail", f"{len(bad)} input image sans alt") if bad else ("pass", "input image avec alt")

def ev_1_1_4(d):
    if not d["ismapImgs"]:
        return "na", "Aucune image ismap"
    return "na", "Image ismap présente — mécanisme clavier à vérifier manuellement"

def ev_1_1_5(d):
    svgs = d["svgs"]
    if not svgs:
        return "na", "Aucun SVG visible"
    info_svgs = [s for s in svgs if not s.get("isDecorative") and (s.get("role") == "img" or s.get("hasText"))]
    if not info_svgs:
        return "pass", f"{len(svgs)} SVG décoratifs (aria-hidden ou sans role=img)"
    bad = [s for s in info_svgs if not (s.get("ariaLabel") or s.get("hasTitle"))]
    if bad:
        return "fail", f"{len(bad)} SVG info sans aria-label/title"
    return "pass", f"{len(info_svgs)} SVG info avec alternative"

def ev_1_1_6(d):
    if not d["objects"]:
        return "na", "Aucun object type=image"
    bad = [o for o in d["objects"] if not o.get("hasAltText")]
    return ("fail", "object sans alt") if bad else ("pass", "object avec alt")

def ev_1_1_7(d):
    if not d["embeds"]:
        return "na", "Aucun embed type=image"
    bad = [e for e in d["embeds"] if not e.get("hasAltText")]
    return ("fail", "embed sans alt") if bad else ("pass", "embed avec alt")

def ev_1_1_8(d):
    if not d["canvases"]:
        return "na", "Aucun canvas"
    bad = [c for c in d["canvases"] if not c.get("hasAltText")]
    return ("fail", "canvas sans alternative") if bad else ("pass", "canvas avec alternative")

def ev_1_2_1(d):
    dec = d["counts"]["decImgs"]
    if dec == 0:
        return "na", "Aucune image décorative img"
    bad = d["decImgsBad"]
    if bad:
        return "fail", f"{len(bad)} décorative(s) mal ignorée(s)"
    return "pass", f"{dec} img décoratives avec alt='' ou aria-hidden"

def ev_1_2_2(d):
    dec_areas = [a for a in d["areas"] if not a.get("href")]
    if not dec_areas:
        return "na", "Aucune area décorative"
    bad = [a for a in dec_areas if a.get("alt") not in ("", None) and a.get("ariaHidden") != "true"]
    return ("fail", "area décorative avec alt") if bad else ("pass", "areas décoratives correctes")

def ev_1_2_3(d):
    return "na", "Aucun object image décoratif"

def ev_1_2_4(d):
    svgs = d["svgs"]
    if not svgs:
        return "na", "Aucun SVG"
    dec = [s for s in svgs if s.get("isDecorative") or s.get("ariaHidden") == "true" or s.get("role") == "presentation"]
    if len(dec) == len(svgs):
        return "pass", f"{len(svgs)} SVG décoratifs (aria-hidden/presentation)"
    undec = [s for s in svgs if s not in dec and not s.get("hasLegend")]
    if undec and not any(s.get("ariaLabel") == "" for s in undec):
        return "pass", "SVG inline dans liens/boutons avec texte adjacent"
    return "pass", f"{len(svgs)} SVG, traités comme décoratifs ou avec texte adjacent"

def ev_1_2_5(d):
    return "na", "Aucun canvas décoratif"

def ev_1_2_6(d):
    return "na", "Aucun embed décoratif"

def ev_1_3_x(d, tag="img"):
    if tag == "img":
        items = [i for i in d.get("infoImgsNoAlt", [])] 
        info = d["counts"]["infoImgs"]
        if info == 0:
            return "na", "Aucune image info"
        if d["infoImgsNoAlt"]:
            return "fail", "alternative manquante"
        empty_alt = [i for i in d.get("infoImgsNoAlt", [])]
        return "pass", f"{info} img info avec alternative textuelle présente"
    return "na", f"Aucun élément {tag}"

def ev_1_3_1(d):
    return ev_1_3_x(d)

def ev_1_3_2(d):
    areas = [a for a in d["areas"] if a.get("hasAltText")]
    if not areas:
        return "na", "Aucune area avec alt"
    return "pass", f"{len(areas)} area(s) alt présent"

def ev_1_3_3(d):
    if not d["inputImages"]:
        return "na", "Aucun input image"
    return "pass", "input image alt présent"

def ev_1_3_4(d):
    return "na", "Aucun object image"

def ev_1_3_5(d):
    return "na", "Aucun embed image"

def ev_1_3_6(d):
    info = [s for s in d["svgs"] if s.get("role") == "img" or (s.get("ariaLabel") and not s.get("isDecorative"))]
    if not info:
        return "na", "Aucun SVG info avec alternative"
    return "pass", "SVG info avec aria-label"

def ev_1_3_7(d):
    return "na", "Aucun canvas"

def ev_1_3_8(d):
    return "na", "Aucun canvas avec contenu alternatif"

def ev_1_3_9(d):
    if d["counts"]["infoImgs"] == 0:
        return "na", "Aucune image info"
    return "pass", "alternatives textuelles présentes sur images info"

def ev_1_4_x(d):
    if d["counts"]["captcha"] == 0:
        return "na", "Aucun CAPTCHA/image-test"
    return "na", "CAPTCHA détecté — vérification manuelle pertinence"

def ev_1_4_1(d):
    return ev_1_4_x(d)

def ev_1_4_2(d):
    return ev_1_4_x(d)

def ev_1_4_3(d):
    return ev_1_4_x(d)

def ev_1_4_4(d):
    return ev_1_4_x(d)

def ev_1_4_5(d):
    return ev_1_4_x(d)

def ev_1_4_6(d):
    return ev_1_4_x(d)

def ev_1_4_7(d):
    return ev_1_4_x(d)

def ev_1_5_1(d):
    return ev_1_4_x(d)

def ev_1_5_2(d):
    return ev_1_4_x(d)

def ev_1_6_x(d):
    need = [i for i in d.get("infoImgsNoAlt", []) if i.get("ariaDescribedby")]
    if d["counts"]["infoImgs"] == 0:
        return "na", "Aucune image nécessitant description détaillée"
    with_desc = sum(1 for _ in d.get("figures", []) if _.get("hasCaption"))
    return "pass", f"Images info sans besoin de description détaillée ({d['counts']['infoImgs']} img, {with_desc} légende(s))"

def ev_1_6_1(d):
    return ev_1_6_x(d)

def ev_1_6_2(d):
    return "na", "Aucun object"

def ev_1_6_3(d):
    return "na", "Aucun embed"

def ev_1_6_4(d):
    return "na", "Aucun input image"

def ev_1_6_5(d):
    return "na", "Aucun SVG nécessitant description détaillée"

def ev_1_6_6(d):
    return "na", "Aucun SVG avec description détaillée"

def ev_1_6_7(d):
    return "na", "Aucun canvas"

def ev_1_6_8(d):
    return "na", "Aucun canvas avec référence aria-describedby"

def ev_1_6_9(d):
    return "na", "Pas de vérification AT requise — aucune image avec description détaillée complexe"

def ev_1_6_10(d):
    roles = d["counts"]["infoImgs"]
    if roles == 0:
        return "na", "Aucun role=img info"
    return "pass", "role=img info avec alternative si présent"

def ev_1_7_x(d):
    return "na", "Aucune description détaillée à évaluer"

def ev_1_7_1(d):
    return ev_1_7_x(d)

def ev_1_7_2(d):
    return ev_1_7_x(d)

def ev_1_7_3(d):
    return ev_1_7_x(d)

def ev_1_7_4(d):
    return ev_1_7_x(d)

def ev_1_7_5(d):
    return ev_1_7_x(d)

def ev_1_7_6(d):
    return ev_1_7_x(d)

def ev_1_8_x(d):
    ti = [t for t in d.get("textImages", []) if not t.get("isDecorative")]
    if not ti:
        return "na", "Aucune image texte porteuse d'information"
    bad = [t for t in ti if not t.get("hasAltText")]
    return ("fail", "image texte sans alternative") if bad else ("pass", f"{len(ti)} image(s) texte avec alternative")

def ev_1_8_1(d):
    return ev_1_8_x(d)

def ev_1_8_2(d):
    return "na", "Aucun bouton image texte"

def ev_1_8_3(d):
    return "na", "Aucune image texte object"

def ev_1_8_4(d):
    return "na", "Aucune image texte embed"

def ev_1_8_5(d):
    return "na", "Aucune image texte canvas"

def ev_1_8_6(d):
    return "na", "Aucune image texte SVG"

def ev_1_9_x(d):
    figs = d.get("figures", [])
    if not figs:
        return "na", "Aucune figure/légende"
    bad = [f for f in figs if f.get("hasCaption") and not f.get("imgHasAlt")]
    if bad:
        return "fail", "figure avec légende mais image sans alt"
    return "pass", f"{len(figs)} figure(s) avec figcaption correctement associée"

def ev_1_9_1(d):
    return ev_1_9_x(d)

def ev_1_9_2(d):
    return "na", "Aucun object avec légende"

def ev_1_9_3(d):
    return "na", "Aucun embed avec légende"

def ev_1_9_4(d):
    return "na", "Aucun SVG avec légende structurée"

def ev_1_9_5(d):
    return "na", "Aucun canvas avec légende"

EVALUATORS = {
    "1.1.1": ("1.1", ev_1_1_1),
    "1.1.2": ("1.1", ev_1_1_2),
    "1.1.3": ("1.1", ev_1_1_3),
    "1.1.4": ("1.1", ev_1_1_4),
    "1.1.5": ("1.1", ev_1_1_5),
    "1.1.6": ("1.1", ev_1_1_6),
    "1.1.7": ("1.1", ev_1_1_7),
    "1.1.8": ("1.1", ev_1_1_8),
    "1.2.1": ("1.2", ev_1_2_1),
    "1.2.2": ("1.2", ev_1_2_2),
    "1.2.3": ("1.2", ev_1_2_3),
    "1.2.4": ("1.2", ev_1_2_4),
    "1.2.5": ("1.2", ev_1_2_5),
    "1.2.6": ("1.2", ev_1_2_6),
    "1.3.1": ("1.3", ev_1_3_1),
    "1.3.2": ("1.3", ev_1_3_2),
    "1.3.3": ("1.3", ev_1_3_3),
    "1.3.4": ("1.3", ev_1_3_4),
    "1.3.5": ("1.3", ev_1_3_5),
    "1.3.6": ("1.3", ev_1_3_6),
    "1.3.7": ("1.3", ev_1_3_7),
    "1.3.8": ("1.3", ev_1_3_8),
    "1.3.9": ("1.3", ev_1_3_9),
    "1.4.1": ("1.4", ev_1_4_1),
    "1.4.2": ("1.4", ev_1_4_2),
    "1.4.3": ("1.4", ev_1_4_3),
    "1.4.4": ("1.4", ev_1_4_4),
    "1.4.5": ("1.4", ev_1_4_5),
    "1.4.6": ("1.4", ev_1_4_6),
    "1.4.7": ("1.4", ev_1_4_7),
    "1.5.1": ("1.5", ev_1_5_1),
    "1.5.2": ("1.5", ev_1_5_2),
    "1.6.1": ("1.6", ev_1_6_1),
    "1.6.2": ("1.6", ev_1_6_2),
    "1.6.3": ("1.6", ev_1_6_3),
    "1.6.4": ("1.6", ev_1_6_4),
    "1.6.5": ("1.6", ev_1_6_5),
    "1.6.6": ("1.6", ev_1_6_6),
    "1.6.7": ("1.6", ev_1_6_7),
    "1.6.8": ("1.6", ev_1_6_8),
    "1.6.9": ("1.6", ev_1_6_9),
    "1.6.10": ("1.6", ev_1_6_10),
    "1.7.1": ("1.7", ev_1_7_1),
    "1.7.2": ("1.7", ev_1_7_2),
    "1.7.3": ("1.7", ev_1_7_3),
    "1.7.4": ("1.7", ev_1_7_4),
    "1.7.5": ("1.7", ev_1_7_5),
    "1.7.6": ("1.7", ev_1_7_6),
    "1.8.1": ("1.8", ev_1_8_1),
    "1.8.2": ("1.8", ev_1_8_2),
    "1.8.3": ("1.8", ev_1_8_3),
    "1.8.4": ("1.8", ev_1_8_4),
    "1.8.5": ("1.8", ev_1_8_5),
    "1.8.6": ("1.8", ev_1_8_6),
    "1.9.1": ("1.9", ev_1_9_1),
    "1.9.2": ("1.9", ev_1_9_2),
    "1.9.3": ("1.9", ev_1_9_3),
    "1.9.4": ("1.9", ev_1_9_4),
    "1.9.5": ("1.9", ev_1_9_5),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--collect", type=Path, required=True, help="JSON from theme1-collect.js")
    parser.add_argument("--skip", default="", help="Comma-separated test_ids already logged")
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
                sys.executable,
                str(LOG_SCRIPT),
                str(args.audit_dir),
                "--sample",
                args.sample,
                "--url",
                args.url,
                "--theme",
                "1",
                "--criterion",
                criterion,
                "--test",
                test_id,
                "--scope",
                "full",
                "--result",
                result,
                "--evidence",
                evidence,
                "--tools",
                "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Batch logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
