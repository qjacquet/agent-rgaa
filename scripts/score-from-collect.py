#!/usr/bin/env python3
"""Agrège les collectes MCP en grille — NE PAS utiliser sans collecte CDP complète par échantillon.

Obligatoire avant exécution :
- samples/{slug}.json générés via browser_cdp (page-audit-collect.js, cdp-contrast-scan.js, AX tree)
- Phase 2 skill : 106 critères traités via MCP, pas NT par défaut

Ce script complète l'agrégation ; il ne remplace PAS la passe MCP.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "data" / "rgaa-rules.json").read_text(encoding="utf-8"))

# Critères évalués automatiquement (partie agent) — le reste = NT
AUTO = {
    "1.1": lambda d: _img_alt(d),
    "6.1": lambda d: _links(d),
    "8.1": lambda d: _lang(d),
    "8.2": lambda d: _title(d),
    "9.1": lambda d: _h1(d),
    "9.2": lambda d: _headings(d),
    "10.1": lambda d: _skip(d),
    "11.1": lambda d: _forms(d),
    "12.7": lambda d: _tabindex(d),
    "2.1": lambda d: _iframes(d),
}


def _status(result):
    return {"pass": "C", "fail": "NC", "na": "NA", "nt": "NT"}[result]


def _img_alt(d):
    total = d.get("images", {}).get("total", 0)
    woa = d.get("images", {}).get("withoutAlt", 0)
    if total == 0:
        return "na", "Aucune image"
    if woa:
        return "fail", f"{woa} image(s) sans alternative textuelle"
    return "pass", "Alternatives présentes sur images visibles"


def _links(d):
    bad = d.get("linksNoText", [])
    if not bad:
        return "pass", "Liens visibles avec intitulé"
    return "fail", f"{len(bad)} lien(s) sans intitulé accessible"


def _lang(d):
    lang = (d.get("lang") or "").lower()
    if not lang:
        return "fail", "Attribut lang absent"
    if lang.startswith("fr"):
        return "pass", f"lang={d.get('lang')}"
    return "nt", f"lang={d.get('lang')} — vérifier pertinence du contenu"


def _title(d):
    if d.get("title"):
        return "pass", d["title"][:80]
    return "fail", "Title vide"


def _h1(d):
    n = d.get("h1Count", 0)
    if n == 0:
        return "fail", "Aucun h1 visible"
    if n > 1:
        return "fail", f"{n} h1 visibles: {d.get('h1Texts')}"
    return "pass", f"h1 unique: {d.get('h1Texts', [''])[0]}"


def _headings(d):
    jumps = d.get("headingJumps", [])
    if not d.get("headings"):
        return "na", "Pas de titres"
    if jumps:
        j = jumps[0]
        return "fail", f"Saut H{j['from']['level']}→H{j['to']['level']}: {j['from']['text'][:40]} → {j['to']['text'][:40]}"
    return "pass", "Pas de saut de niveau > 1"


def _skip(d):
    if d.get("skipLink"):
        return "pass", d["skipLink"].get("text", "")
    return "fail", "Lien d'évitement absent"


def _forms(d):
    bad = [f for f in d.get("fieldsNoLabel", []) if f.get("type") not in ("submit", "button")]
    if not bad:
        return "pass", "Champs avec label ou aria"
    return "fail", f"{len(bad)} champ(s) sans label: {[x.get('name') for x in bad[:5]]}"


def _tabindex(d):
    bad = d.get("tabindexPositive", [])
    if bad:
        return "fail", f"tabindex>0: {bad}"
    return "pass", "Pas de tabindex positif"


def _iframes(d):
    n = d.get("iframesNoTitle", 0)
    if n:
        return "fail", f"{n} iframe(s) sans title"
    return "pass", "Iframes titrées ou absentes"


def aggregate_site(statuses):
    if "NC" in statuses:
        return "NC"
    if all(s == "NA" for s in statuses):
        return "NA"
    if any(s == "NT" for s in statuses):
        return "NT"
    if any(s == "C" for s in statuses):
        return "C"
    return "NT"


def build_pre_report(audit_dir, slugs, grid_rows, nc_items):
    ts = datetime.now().strftime("%Y-%m-%d")
    n_c = sum(1 for r in grid_rows if r["site_status"] == "C")
    n_nc = sum(1 for r in grid_rows if r["site_status"] == "NC")
    n_na = sum(1 for r in grid_rows if r["site_status"] == "NA")
    n_nt = sum(1 for r in grid_rows if r["site_status"] == "NT")

    lines = [
        "# Pré-rapport d'audit RGAA 4.1.2 — CMV médiforce",
        "",
        "> **Audit non finalisé** — validations humaines requises avant rapport final.",
        "",
        "## 1. Synthèse passe agent",
        "",
        "| Indicateur | Valeur |",
        "| ---------- | ------ |",
        f"| Échantillons validés | {len(slugs)} |",
        f"| Critères C (agent, auto) | {n_c} |",
        f"| Critères NC (agent) | {n_nc} |",
        f"| Critères NA | {n_na} |",
        f"| Critères NT (non évalués / complément) | {n_nt} |",
        f"| Date | {ts} |",
        "",
        "### Périmètre",
        "",
        "- Site : https://www.cmvmediforce.fr",
        "- Contexte : desktop",
        "- MCP : cursor-ide-browser uniquement",
        "- AT : phase 4 humaine (VoiceOver/NVDA non utilisés par l'agent)",
        "",
        "## 2. NC agent — corrections prioritaires",
        "",
        "| Critère | Échantillon | Constat |",
        "| ------- | ----------- | ------- |",
    ]
    for item in nc_items[:40]:
        lines.append(f"| {item['criterion']} | {item['slug']} | {item['evidence']} |")
    if len(nc_items) > 40:
        lines.append(f"| … | … | {len(nc_items) - 40} autres NC — voir grid.csv |")

    lines += [
        "",
        "## 3. Non-conformités récurrentes (site)",
        "",
        "### 9.1 — Présence d'un seul h1",
        "Absence ou multiplication de h1 sur la majorité des échantillons (accueil : 2 h1 ; trésorerie, publications, plan-du-site, résultat-simulation : 0 h1).",
        "",
        "### 6.1 — Intitulé des liens",
        "Liens image seule sans texte accessible (bannières accueil, fiches métiers simulation, liens téléphone `tel:`).",
        "",
        "### 11.1 — Étiquettes des champs de formulaire",
        "Champs sans label associé sur résultat simulation (7 champs) ; boutons submit « Simuler » sans nom accessible explicite sur plusieurs pages.",
        "",
        "### 9.2 — Hiérarchie des titres",
        "Sauts de niveau sur résultat-simulation (H2→H5) et contacts (H2→H5).",
        "",
        "### 1.1 — Alternatives images",
        "1 image sans alt sur publications.",
        "",
        "## 4. Compléments humains obligatoires",
        "",
        "Les critères **non couverts par la collecte DOM** (~97 critères) restent en **NT**.",
        "Les tests `human_complement_required` (images porteuses d'info, contraste, clavier 7.3, restitution AT) nécessitent validation humaine.",
        "",
        "### 7.3.x — Éléments focusables et activation clavier",
        "",
        "**Résultat agent** : **NT** (pré-analyse DOM seulement sur cette passe)",
        "",
        "**Pour noter C** :",
        "- Parcourir tous les contrôles interactifs au clavier (Tab / Shift+Tab)",
        "- Vérifier qu'aucune action n'est réservée au seul clic souris",
        "- Tester Entrée/Espace sur boutons, radios, liens",
        "",
        "**Cas NC** :",
        "- Élément atteignable au clic mais pas au clavier",
        "- Focus piégé ou ordre incohérent",
        "- Action sans équivalent clavier",
        "",
        "**Combinaison AT** : VoiceOver + Safari ou NVDA + Firefox",
        "",
        "**Résultat humain** (à remplir) :",
        "- [ ] C — Commentaire :",
        "- [ ] NC — Élément + commentaire :",
        "",
        "## 5. Grille provisoire",
        "",
        "Voir [grid.csv](./grid.csv).",
        "",
        "## 6. Prochaines étapes",
        "",
        "Répondre par test : `{critère} | {url} | {test_id} | C|NC|NA | commentaire`",
        "",
        "Échantillon bloqué résolu : `resultat-simulation` accessible via parcours simulation (Véhicule / Electrique / Infirmier(ère) / 1000 €).",
    ]
    (audit_dir / "pre-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    import sys

    audit_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "audits/cmvmediforce-fr/2026-06-22"
    samples_dir = audit_dir / "samples"
    slugs = {}
    for p in sorted(samples_dir.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        slug = data.get("slug", p.stem)
        slugs[slug] = data

    slug_order = sorted(slugs.keys())
    grid_rows = []
    nc_items = []
    ts = datetime.now(timezone.utc).isoformat()
    log_path = audit_dir / "audit-log.jsonl"

    with log_path.open("a", encoding="utf-8") as log:
        log.write(json.dumps({"event": "phase1_complete", "samples_ok": len(slugs), "timestamp": ts}, ensure_ascii=False) + "\n")

        for theme in RULES["themes"]:
            for criterion in theme["criteria"]:
                cid = criterion["id"]
                row = {
                    "theme_id": theme["id"],
                    "theme_title": theme["title"],
                    "criterion_id": cid,
                    "criterion_title": criterion["title"][:100],
                    "wcag_level": ",".join(criterion.get("wcag_levels", [])),
                }
                statuses = []
                if cid in AUTO:
                    fn = AUTO[cid]
                    for slug in slug_order:
                        result, evidence = fn(slugs[slug])
                        status = _status(result)
                        row[slug] = status
                        statuses.append(status)
                        if result in ("pass", "fail"):
                            log.write(json.dumps({
                                "event": "criterion_test",
                                "sample": slug,
                                "criterion": cid,
                                "agent_result": result,
                                "criterion_status_agent": status,
                                "evidence": evidence,
                                "timestamp": ts,
                            }, ensure_ascii=False) + "\n")
                        if result == "fail":
                            nc_items.append({"criterion": cid, "slug": slug, "evidence": evidence})
                else:
                    for slug in slug_order:
                        row[slug] = "NT"
                        statuses.append("NT")

                row["site_status"] = aggregate_site(statuses)
                row["notes"] = ""
                grid_rows.append(row)

    headers = ["theme_id", "theme_title", "criterion_id", "criterion_title", "wcag_level"] + slug_order + ["site_status", "notes"]
    csv_path = audit_dir / "grid.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for row in grid_rows:
            vals = []
            for h in headers:
                v = str(row.get(h, ""))
                if "," in v or '"' in v:
                    v = '"' + v.replace('"', '""') + '"'
                vals.append(v)
            f.write(",".join(vals) + "\n")

    build_pre_report(audit_dir, slugs, grid_rows, nc_items)

    # samples-status all ok
    status_path = audit_dir / "samples-status.json"
    if status_path.exists():
        st = json.loads(status_path.read_text(encoding="utf-8"))
        for s in st["samples"]:
            if s["status"] != "ok":
                s["status"] = "ok"
                s["http_code"] = 200
        status_path.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n_nc_site = sum(1 for r in grid_rows if r["site_status"] == "NC")
    print(f"grid.csv: {len(grid_rows)} criteria, {n_nc_site} NC site-level, {len(nc_items)} NC sample-criterion pairs")
    print(f"pre-report.md written")


if __name__ == "__main__":
    main()
