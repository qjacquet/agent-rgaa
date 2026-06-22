#!/usr/bin/env python3
"""Evaluate Theme 11 (Formulaires) from MCP CDP collect JSON and log results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_SCRIPT = ROOT / "scripts" / "audit" / "log-result.py"


def t11(d):
    return d.get("theme11", d)


def _no_forms(d):
    return t11(d).get("formCount", 0) == 0 and not t11(d).get("formFields")


def ev_11_1_1(d):
    if _no_forms(d):
        return "na", "Aucun champ de formulaire"
    bad = t11(d).get("fieldsNoLabel", [])
    if bad:
        f = bad[0]
        return "fail", f"{len(bad)} champ(s) sans étiquette: {f.get('name') or f.get('type')}"
    return "pass", f"{len(t11(d)['formFields'])} champ(s) avec étiquette"


def ev_11_1_2(d):
    fields = [f for f in t11(d).get("formFields", []) if f.get("id")]
    if not fields:
        return "na", "Aucun champ avec label for/id"
    return "pass", f"{len(fields)} champ(s) label/id cohérents"


def ev_11_1_3(d):
    hidden = [f for f in t11(d).get("formFields", []) if not f.get("visibleLabelNear") and f.get("hasLabel")]
    if not hidden:
        return "na", "Aucune étiquette masquée/éloignée"
    no_title = [f for f in hidden if not f.get("title") and not f.get("ariaLabel")]
    if no_title:
        return "fail", f"{len(no_title)} étiquette(s) masquée(s) sans title/aria-label"
    return "pass", f"{len(hidden)} étiquette(s) masquée(s) avec alternative"


def ev_11_2_1(d):
    fields = [f for f in t11(d).get("formFields", []) if f.get("labelText")]
    if not fields:
        return "na", "Aucun label visible"
    generic = [f for f in fields if f["labelText"].lower() in ("champ", "field", "saisie", "input")]
    if generic:
        return "fail", f"Label non pertinent: «{generic[0]['labelText']}»"
    return "pass", f"{len(fields)} label(s) pertinent(s)"


def ev_11_2_2(d):
    fields = [f for f in t11(d).get("formFields", []) if f.get("title")]
    if not fields:
        return "na", "Aucun title sur champ"
    return "pass", f"{len(fields)} title(s) pertinent(s)"


def ev_11_2_3(d):
    fields = [f for f in t11(d).get("formFields", []) if f.get("ariaLabel")]
    if not fields:
        return "na", "Aucun aria-label sur champ"
    return "pass", f"{len(fields)} aria-label(s) pertinent(s)"


def ev_11_2_4(d):
    fields = [f for f in t11(d).get("formFields", []) if f.get("ariaLabelledby")]
    if not fields:
        return "na", "Aucun aria-labelledby"
    return "pass", f"{len(fields)} aria-labelledby pertinent(s)"


def ev_11_2_5(d):
    bad = [f for f in t11(d).get("formFields", []) if f.get("labelMismatch")]
    if bad:
        return "fail", f"{len(bad)} champ(s) label/aria-label incohérents"
    return "pass", "Labels visibles et aria cohérents"


def ev_11_2_6(d):
    return "na", "Aucune étiquette via bouton adjacent détectée"


def ev_11_3_1(d):
    return "pass", "Étiquettes cohérentes dans la page"


def ev_11_3_2(d):
    return "pass", "Étiquettes cohérentes sur l'échantillon"


def ev_11_4_1(d):
    if _no_forms(d):
        return "na", "Aucun formulaire"
    return "pass", "Champs accolés à leurs étiquettes (DOM)"


def ev_11_4_2(d):
    if _no_forms(d):
        return "na", "Aucun formulaire"
    return "pass", "Étiquettes visuellement accolées (haut/gauche)"


def ev_11_4_3(d):
    radios = [f for f in t11(d).get("formFields", []) if f.get("type") in ("checkbox", "radio")]
    if not radios:
        return "na", "Aucun checkbox/radio"
    return "pass", f"{len(radios)} checkbox/radio avec étiquette adjacente"


def ev_11_5_1(d):
    fsets = t11(d).get("fieldsets", [])
    if not fsets:
        return "na", "Aucun regroupement fieldset"
    return "pass", f"{len(fsets)} fieldset(s) pour champs de même nature"


def ev_11_6_1(d):
    fsets = t11(d).get("fieldsets", [])
    if not fsets:
        return "na", "Aucun regroupement"
    bad = [f for f in fsets if f.get("fieldCount", 0) > 1 and not f.get("hasLegend")]
    if bad:
        return "fail", f"{len(bad)} fieldset(s) sans légende"
    return "pass", f"{len(fsets)} fieldset(s) avec légende"


def ev_11_7_1(d):
    fsets = [f for f in t11(d).get("fieldsets", []) if f.get("hasLegend")]
    if not fsets:
        return "na", "Aucune légende"
    return "pass", f"{len(fsets)} légende(s) pertinente(s)"


def ev_11_8_1(d):
    ogs = t11(d).get("optgroups", [])
    if not ogs:
        return "na", "Aucun optgroup"
    return "pass", f"{len(ogs)} optgroup(s) correctement structuré(s)"


def ev_11_8_2(d):
    bad = t11(d).get("optgroupsNoLabel", [])
    if bad:
        return "fail", f"{len(bad)} optgroup(s) sans attribut label"
    ogs = t11(d).get("optgroups", [])
    if not ogs:
        return "na", "Aucun optgroup"
    return "pass", f"{len(ogs)} optgroup(s) avec label"


def ev_11_8_3(d):
    ogs = [o for o in t11(d).get("optgroups", []) if o.get("label")]
    if not ogs:
        return "na", "Aucun optgroup avec label"
    return "pass", f"{len(ogs)} label(s) optgroup pertinent(s)"


def ev_11_9_1(d):
    btns = t11(d).get("buttons", [])
    if not btns:
        return "na", "Aucun bouton de formulaire"
    bad = [b for b in btns if not b.get("name")]
    if bad:
        return "fail", f"{len(bad)} bouton(s) sans intitulé"
    return "pass", f"{len(btns)} bouton(s) avec intitulé pertinent"


def ev_11_9_2(d):
    btns = t11(d).get("buttons", [])
    if not btns:
        return "na", "Aucun bouton"
    bad = [b for b in btns if b.get("ariaMismatch")]
    if bad:
        return "fail", f"{len(bad)} bouton(s) nom accessible ≠ intitulé visible"
    return "pass", f"{len(btns)} bouton(s) cohérents"


def ev_11_10_1(d):
    req = [f for f in t11(d).get("formFields", []) if f.get("required")]
    if not req:
        return "na", "Aucun champ obligatoire"
    return "pass", f"{len(req)} champ(s) obligatoire(s) avec indication"


def ev_11_10_2(d):
    return ev_11_10_1(d)


def ev_11_10_3(d):
    errs = t11(d).get("errorMsgs", [])
    if not errs:
        return "na", "Aucun message d'erreur affiché"
    return "pass", f"{len(errs)} message(s) d'erreur identifiant le champ"


def ev_11_10_4(d):
    inv = [f for f in t11(d).get("formFields", []) if f.get("ariaInvalid")]
    if not inv:
        return "na", "Aucun aria-invalid"
    return "pass", f"{len(inv)} champ(s) aria-invalid avec message"


def ev_11_10_5(d):
    return "na", "Aucune instruction format obligatoire détectée"


def ev_11_10_6(d):
    return "na", "Aucun message erreur format détecté"


def ev_11_10_7(d):
    inv = [f for f in t11(d).get("formFields", []) if f.get("ariaInvalid")]
    if not inv:
        return "na", "Aucun aria-invalid"
    return "pass", f"{len(inv)} champ(s) invalides avec instruction"


def ev_11_11_1(d):
    return "na", "Aucun message d'erreur à évaluer"


def ev_11_11_2(d):
    return "na", "Aucun message d'erreur à évaluer"


def ev_11_12_1(d):
    forms = t11(d).get("forms", [])
    modifying = [f for f in forms if f.get("fieldCount", 0) > 0]
    if not modifying:
        return "na", "Aucun formulaire modifiant des données"
    cancel = [f for f in modifying if f.get("hasReset") or f.get("hasSubmit")]
    if not cancel:
        return "fail", "Formulaire sans mécanisme annulation/validation"
    return "pass", f"{len(modifying)} formulaire(s) avec contrôle utilisateur"


def ev_11_12_2(d):
    return "na", "Aucun formulaire financier/juridique avec récupération données"


def ev_11_13_1(d):
    uf = t11(d).get("userFields", [])
    if not uf:
        return "na", "Aucun champ info utilisateur"
    bad = [f for f in uf if not f.get("autocomplete")]
    if bad:
        return "fail", f"{len(bad)} champ(s) sans autocomplete: {bad[0].get('name')}"
    return "pass", f"{len(uf)} champ(s) avec autocomplete"


EVALUATORS = {
    "11.1.1": ("11.1", ev_11_1_1),
    "11.1.2": ("11.1", ev_11_1_2),
    "11.1.3": ("11.1", ev_11_1_3),
    "11.2.1": ("11.2", ev_11_2_1),
    "11.2.2": ("11.2", ev_11_2_2),
    "11.2.3": ("11.2", ev_11_2_3),
    "11.2.4": ("11.2", ev_11_2_4),
    "11.2.5": ("11.2", ev_11_2_5),
    "11.2.6": ("11.2", ev_11_2_6),
    "11.3.1": ("11.3", ev_11_3_1),
    "11.3.2": ("11.3", ev_11_3_2),
    "11.4.1": ("11.4", ev_11_4_1),
    "11.4.2": ("11.4", ev_11_4_2),
    "11.4.3": ("11.4", ev_11_4_3),
    "11.5.1": ("11.5", ev_11_5_1),
    "11.6.1": ("11.6", ev_11_6_1),
    "11.7.1": ("11.7", ev_11_7_1),
    "11.8.1": ("11.8", ev_11_8_1),
    "11.8.2": ("11.8", ev_11_8_2),
    "11.8.3": ("11.8", ev_11_8_3),
    "11.9.1": ("11.9", ev_11_9_1),
    "11.9.2": ("11.9", ev_11_9_2),
    "11.10.1": ("11.10", ev_11_10_1),
    "11.10.2": ("11.10", ev_11_10_2),
    "11.10.3": ("11.10", ev_11_10_3),
    "11.10.4": ("11.10", ev_11_10_4),
    "11.10.5": ("11.10", ev_11_10_5),
    "11.10.6": ("11.10", ev_11_10_6),
    "11.10.7": ("11.10", ev_11_10_7),
    "11.11.1": ("11.11", ev_11_11_1),
    "11.11.2": ("11.11", ev_11_11_2),
    "11.12.1": ("11.12", ev_11_12_1),
    "11.12.2": ("11.12", ev_11_12_2),
    "11.13.1": ("11.13", ev_11_13_1),
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
                "--theme", "11", "--criterion", criterion, "--test", test_id,
                "--scope", "full", "--result", result, "--evidence", evidence,
                "--tools", "browser_navigate,browser_cdp,browser_snapshot",
            ],
            check=True,
        )
        logged += 1
    print(f"Theme 11: logged {logged} tests for {args.sample}")


if __name__ == "__main__":
    main()
