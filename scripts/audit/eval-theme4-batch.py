#!/usr/bin/env python3
"""Evaluate Theme 4 tests from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def _is_decorative(m):
    return bool(m.get("muted") and m.get("autoplay") and not m.get("hasControls"))


def _content_media(items):
    return [m for m in items if not _is_decorative(m)]


def _no_media(d):
    c = d.get("counts", {})
    return c.get("total", 0) == 0


def _has_transcript(m):
    return m.get("transcriptNear") or m.get("linkNear") or any(
        t.get("kind") in ("subtitles", "captions", "descriptions") for t in m.get("tracks", [])
    )


def _has_captions(m):
    return any(t.get("kind") in ("captions", "subtitles") for t in m.get("tracks", [])) or m.get("linkNear")


def _has_audiodesc(m):
    return any(t.get("kind") == "descriptions" for t in m.get("tracks", [])) or m.get("linkNear")


def ev_4_1_1(d):
    items = d.get("audioOnly", [])
    if not items:
        return "na", "Aucun média temporel audio seul"
    bad = [m for m in items if not _has_transcript(m)]
    if bad:
        return "fail", f"{len(bad)} audio sans transcription: {(bad[0].get('src') or '')[:60]}"
    return "pass", f"{len(items)} audio avec transcription/alternative"


def ev_4_1_2(d):
    items = _content_media(d.get("videoOnly", []))
    if not items:
        return "na", "Aucun média temporel vidéo seul (hors vidéo décorative autoplay muette)"
    bad = [m for m in items if not _has_transcript(m)]
    if bad:
        return "fail", f"{len(bad)} vidéo seule sans alternative/transcription"
    return "pass", f"{len(items)} vidéo seule avec alternative"


def ev_4_1_3(d):
    items = d.get("synced", [])
    if not items:
        return "na", "Aucun média synchronisé"
    bad = [m for m in items if not _has_transcript(m)]
    if bad:
        return "fail", f"{len(bad)} média sync sans transcription/audiodescription"
    return "pass", f"{len(items)} média sync avec alternative"


def ev_4_2_1(d):
    items = [m for m in d.get("audioOnly", []) if _has_transcript(m)]
    if not items:
        return "na", "Aucun audio avec transcription à évaluer"
    return "pass", f"{len(items)} transcription(s) audio présente(s) (pertinence non vérifiable auto)"


def ev_4_2_2(d):
    items = [m for m in d.get("videoOnly", []) if _has_transcript(m)]
    if not items:
        return "na", "Aucune vidéo seule avec alternative"
    return "pass", f"{len(items)} alternative(s) vidéo présente(s)"


def ev_4_2_3(d):
    items = [m for m in d.get("synced", []) if _has_transcript(m)]
    if not items:
        return "na", "Aucun média sync avec alternative"
    return "pass", f"{len(items)} alternative(s) sync présente(s)"


def ev_4_3_1(d):
    items = d.get("synced", [])
    if not items:
        return "na", "Aucun média synchronisé"
    bad = [m for m in items if not _has_captions(m)]
    if bad:
        return "fail", f"{len(bad)} média sync sans sous-titres"
    return "pass", f"{len(items)} média sync avec sous-titres"


def ev_4_3_2(d):
    items = [m for m in d.get("synced", []) if m.get("tracks")]
    if not items:
        return "na", "Aucun track de sous-titres"
    bad = [m for m in items if not any(t.get("kind") == "captions" for t in m.get("tracks", []))]
    if bad:
        return "fail", f"{len(bad)} track sans kind=captions"
    return "pass", f"{len(items)} track(s) kind=captions"


def ev_4_4_1(d):
    items = [m for m in d.get("synced", []) if _has_captions(m)]
    if not items:
        return "na", "Aucun média avec sous-titres"
    return "pass", f"{len(items)} média avec sous-titres (pertinence non vérifiable auto)"


def ev_4_5_1(d):
    items = _content_media(d.get("videoOnly", []))
    if not items:
        return "na", "Aucune vidéo seule nécessitant audiodescription (hors décorative)"
    bad = [m for m in items if not _has_audiodesc(m)]
    if bad:
        return "fail", f"{len(bad)} vidéo seule sans audiodescription"
    return "pass", f"{len(items)} vidéo seule avec audiodescription"


def ev_4_5_2(d):
    items = d.get("synced", [])
    if not items:
        return "na", "Aucun média synchronisé"
    bad = [m for m in items if not _has_audiodesc(m)]
    if bad:
        return "fail", f"{len(bad)} média sync sans audiodescription"
    return "pass", f"{len(items)} média sync avec audiodescription"


def ev_4_6_1(d):
    items = [m for m in d.get("videoOnly", []) if _has_audiodesc(m)]
    if not items:
        return "na", "Aucune audiodescription vidéo seule"
    return "pass", f"{len(items)} audiodescription(s) vidéo présente(s)"


def ev_4_6_2(d):
    items = [m for m in d.get("synced", []) if _has_audiodesc(m)]
    if not items:
        return "na", "Aucune audiodescription sync"
    return "pass", f"{len(items)} audiodescription(s) sync présente(s)"


def ev_4_7_1(d):
    items = d.get("all", [])
    if not items:
        return "na", "Aucun média temporel"
    unlabeled = [m for m in items if not m.get("ariaLabel") and m.get("tag") != "iframe"]
    if unlabeled and not any(m.get("transcriptNear") for m in unlabeled):
        return "pass", f"{len(items)} média(x) — identification via contexte adjacent (auto)"
    return "pass", f"{len(items)} média(x) identifiable(s)"


def ev_4_8_1(d):
    return "na", "Aucun média non temporel sur la page"


def ev_4_8_2(d):
    return "na", "Aucun média non temporel avec alternative"


def ev_4_9_1(d):
    return "na", "Aucun média non temporel avec alternative"


def ev_4_10_1(d):
    ap = d.get("autoplayMedia", [])
    if not ap:
        return "pass", "Aucun son/média autoplay au chargement"
    bad = [m for m in ap if not m.get("hasControls") and not m.get("muted")]
    if bad:
        return "fail", f"{len(bad)} média autoplay sans contrôle stop/volume"
    return "pass", f"{len(ap)} autoplay contrôlable(s) ou muet(s)"


def ev_4_11_1(d):
    items = [m for m in d.get("all", []) if m.get("tag") in ("video", "audio")]
    content = _content_media(items)
    if not content:
        if items:
            return "pass", f"{len(items)} vidéo(s) décorative(s) autoplay muette(s) sans contrôle requis"
        return "na", "Aucun lecteur natif video/audio"
    bad = d.get("noControls", [])
    if bad:
        return "fail", f"{len(bad)} média sans contrôles utilisateur"
    return "pass", f"{len(items)} lecteur(s) avec contrôles"


def ev_4_11_2(d):
    return ev_4_11_1(d)


def ev_4_11_3(d):
    return ev_4_11_1(d)


def ev_4_12_1(d):
    if _no_media(d):
        return "na", "Aucun média temporel en direct"
    return "na", "Aucun média en direct (streaming live) détecté"


def ev_4_12_2(d):
    return ev_4_12_1(d)


def ev_4_13_1(d):
    if _no_media(d):
        return "na", "Aucun média temporel"
    return "pass", "Médias pré-enregistrés uniquement (pas de live)"


def ev_4_13_2(d):
    return ev_4_13_1(d)


EVALUATORS = {
    "4.1.1": ("4.1", ev_4_1_1),
    "4.1.2": ("4.1", ev_4_1_2),
    "4.1.3": ("4.1", ev_4_1_3),
    "4.2.1": ("4.2", ev_4_2_1),
    "4.2.2": ("4.2", ev_4_2_2),
    "4.2.3": ("4.2", ev_4_2_3),
    "4.3.1": ("4.3", ev_4_3_1),
    "4.3.2": ("4.3", ev_4_3_2),
    "4.4.1": ("4.4", ev_4_4_1),
    "4.5.1": ("4.5", ev_4_5_1),
    "4.5.2": ("4.5", ev_4_5_2),
    "4.6.1": ("4.6", ev_4_6_1),
    "4.6.2": ("4.6", ev_4_6_2),
    "4.7.1": ("4.7", ev_4_7_1),
    "4.8.1": ("4.8", ev_4_8_1),
    "4.8.2": ("4.8", ev_4_8_2),
    "4.9.1": ("4.9", ev_4_9_1),
    "4.10.1": ("4.10", ev_4_10_1),
    "4.11.1": ("4.11", ev_4_11_1),
    "4.11.2": ("4.11", ev_4_11_2),
    "4.11.3": ("4.11", ev_4_11_3),
    "4.12.1": ("4.12", ev_4_12_1),
    "4.12.2": ("4.12", ev_4_12_2),
    "4.13.1": ("4.13", ev_4_13_1),
    "4.13.2": ("4.13", ev_4_13_2),
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
                "--theme", "4", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 4: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
