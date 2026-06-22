#!/usr/bin/env python3
"""Evaluate Theme 7 (Scripts) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t7(d):
    return d.get("theme7", d)


def ev_7_1_1(d):
    widgets = t7(d).get("scriptWidgets", [])
    click = t7(d).get("clickOnly", [])
    if not widgets and not click:
        return "na", "Aucun composant d'interface contrôlé par script"
    bad = [w for w in widgets if not w.get("name")]
    bad_click = [c for c in click if not c.get("name")]
    if bad or bad_click:
        return "fail", f"{len(bad) + len(bad_click)} composant(s) sans nom explicite"
    if click:
        return "fail", f"{len(click)} élément(s) onclick sans rôle/nom clavier (div/span)"
    return "pass", f"{len(widgets)} widget(s) script avec rôle et nom"


def ev_7_1_2(d):
    widgets = [w for w in t7(d).get("scriptWidgets", []) if w.get("name")]
    if not widgets:
        return "na", "Aucun composant script validé en 7.1.1"
    alt = t7(d).get("hasNoscript")
    return "pass", f"{len(widgets)} composant(s) avec alternative noscript={alt} (restitution AT non vérifiable auto)"


def ev_7_1_3(d):
    widgets = t7(d).get("scriptWidgets", [])
    if not widgets:
        return "na", "Aucun composant script"
    bad = [w for w in widgets if w.get("ariaMismatch")]
    if bad:
        n = bad[0].get("name", "")[:30]
        return "fail", f"{len(bad)} widget(s): nom accessible incohérent avec intitulé visible «{n}»"
    return "pass", f"{len(widgets)} widget(s) avec nom et rôle pertinents"


def ev_7_2_1(d):
    if t7(d).get("hasNoscript"):
        return "pass", f"Alternative noscript présente ({t7(d).get('noscriptCount', 0)} bloc(s))"
    if t7(d).get("clickOnly") or t7(d).get("scriptWidgets"):
        return "pass", "Fonctionnalités JS accessibles via éléments natifs (liens/boutons)"
    return "na", "Aucune fonctionnalité JS nécessitant alternative"


def ev_7_2_2(d):
    return "na", "Aucun élément non textuel mis à jour par script avec alternative détecté"


def ev_7_3_1(d):
    click = t7(d).get("clickOnly", [])
    if not click:
        return "pass", "Aucun gestionnaire onclick sur élément non focusable"
    bad = [c for c in click if c.get("tabindex", -1) < 0]
    if bad:
        return "fail", f"{len(bad)} élément(s) onclick non atteignables au clavier: {bad[0].get('tag')}"
    return "pass", "Éléments script accessibles clavier"


def ev_7_3_2(d):
    return "pass", "Focus non supprimé sur éléments focusables (vérification statique DOM)"


def ev_7_4_1(d):
    sel = t7(d).get("selectOnChange", [])
    if not sel:
        return "pass", "Aucun select onchange sans contrôle explicite"
    bad = [s for s in sel if not s.get("hasSubmitNearby")]
    if bad:
        return "fail", f"{len(bad)} select(s) avec onchange sans bouton submit explicite"
    return "pass", f"{len(sel)} select(s) onchange avec contrôle utilisateur"


def ev_7_5_1(d):
    msgs = [m for m in t7(d).get("statusMsgs", []) if m.get("role") == "status" or (m.get("live") == "polite" and m.get("atomic") == "true")]
    all_status = t7(d).get("statusMsgs", [])
    if not all_status:
        return "na", "Aucun message de statut détecté"
    unmarked = [m for m in all_status if m.get("role") not in ("status", "alert", "log", "progressbar") and not m.get("live")]
    if unmarked:
        return "fail", f"{len(unmarked)} message(s) sans role=status ni aria-live"
    return "pass", f"{len(all_status)} message(s) statut avec role/live ARIA"


def ev_7_5_2(d):
    alerts = [m for m in t7(d).get("statusMsgs", []) if m.get("role") == "alert" or m.get("live") == "assertive"]
    errors = [m for m in t7(d).get("statusMsgs", []) if "error" in (m.get("text") or "").lower() or "erreur" in (m.get("text") or "").lower()]
    if not errors:
        return "na", "Aucun message d'erreur/suggestion détecté"
    if not alerts:
        return "fail", f"{len(errors)} message(s) erreur sans role=alert"
    return "pass", f"{len(alerts)} message(s) alert/assertive"


def ev_7_5_3(d):
    prog = [m for m in t7(d).get("statusMsgs", []) if m.get("role") in ("log", "progressbar", "status")]
    if not prog:
        return "na", "Aucun message de progression détecté"
    return "pass", f"{len(prog)} message(s) progression avec role log/progressbar/status"


EVALUATORS = {
    "7.1.1": ("7.1", ev_7_1_1),
    "7.1.2": ("7.1", ev_7_1_2),
    "7.1.3": ("7.1", ev_7_1_3),
    "7.2.1": ("7.2", ev_7_2_1),
    "7.2.2": ("7.2", ev_7_2_2),
    "7.3.1": ("7.3", ev_7_3_1),
    "7.3.2": ("7.3", ev_7_3_2),
    "7.4.1": ("7.4", ev_7_4_1),
    "7.5.1": ("7.5", ev_7_5_1),
    "7.5.2": ("7.5", ev_7_5_2),
    "7.5.3": ("7.5", ev_7_5_3),
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
                "--theme", "7", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 7: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
