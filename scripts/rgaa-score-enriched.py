#!/usr/bin/env python3
"""Score critères RGAA depuis collectes MCP enrichies (collect + contrast).

Préserve les validations humaines de audit-log.jsonl (human_validation).
Ne marque NT que pour tests non couverts par heuristiques DOM + humain déjà fait.
"""

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "data" / "rgaa-rules.json").read_text(encoding="utf-8"))

# Validations humaines à préserver (écrasent heuristique agent)
HUMAN_OVERRIDES = {}  # filled from audit-log


def load_human_overrides(audit_dir: Path):
    overrides = {}
    log = audit_dir / "audit-log.jsonl"
    if not log.exists():
        return overrides
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") != "human_validation":
            continue
        c = e.get("criterion")
        scope = e.get("scope", "sample")
        sample = e.get("sample")
        result = e.get("human_result", "")
        status = "NC" if result in ("NC", "partial_C") and c in ("7.3", "7.4", "7.1") else (
            "C" if result == "C" else "NC" if result == "NC" else None
        )
        if scope == "all_samples":
            overrides.setdefault(c, {})["*"] = ("NC" if result == "NC" else status, e.get("evidence", ""))
        elif sample and status:
            overrides.setdefault(c, {})[sample] = (status, e.get("evidence", ""))
    return overrides


def dget(data, *keys, default=None):
    cur = data
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default


def get_collect(data):
    if "collect" in data:
        return data["collect"]
    return data  # legacy flat format


def score_criterion(cid, slug, data, all_slugs_data, human):
    c = get_collect(data)
    contrast = data.get("contrast", {})

    # Human override
    if cid in human:
        h = human[cid]
        if "*" in h:
            return h["*"][0], h["*"][1]
        if slug in h:
            return h[slug][0], h[slug][1]

    # --- Heuristiques par critère ---
    if cid == "1.1":
        woa = dget(c, "images", "withoutAlt", default=0)
        total = dget(c, "images", "total", default=0)
        if total == 0:
            return "NA", "Aucune image"
        return ("NC", f"{woa} sans alt") if woa else ("C", "alt/aria présents")

    if cid == "2.1":
        n = c.get("iframesNoTitle", 0)
        if isinstance(n, list):
            n = len(n)
        return ("NC", f"{n} iframe sans title") if n else ("C", "ok")

    if cid == "3.1" or cid == "3.2":
        fc = contrast.get("failCount", 0)
        if contrast.get("checked", 0) == 0:
            return "NT", "scan contrastes non exécuté"
        return ("NC", f"{fc} textes sous ratio") if fc else ("C", f"{contrast.get('checked')} textes ok")

    if cid == "4.1":
        media = c.get("media", [])
        if not media:
            return "NA", "Pas de média temporel"
        return "NT", "Média présent — vérification transcription/sous-titres non automatisée"

    if cid == "5.1":
        tables = c.get("tables", [])
        if not tables:
            return "NA", "Pas de tableau"
        return "NT", "Tableaux présents — headers/caption à vérifier manuellement"

    if cid == "6.1":
        bad = c.get("linksNoText", [])
        return ("NC", f"{len(bad)} liens sans intitulé") if bad else ("C", "ok")

    if cid == "8.1":
        lang = c.get("lang", "")
        return ("NC", "lang absent") if not lang else ("C", lang)

    if cid == "8.2":
        return ("C", c.get("title", "")[:60]) if c.get("title") else ("NC", "title vide")

    if cid == "8.5":
        # viewport in collect if added; check via landmarks/collect
        return "NT", "viewport — vérifier via collect enrichi"

    if cid == "9.1":
        n = c.get("h1Count", 0)
        if n == 0:
            return "NC", "pas de h1"
        if n > 1:
            return "NC", f"{n} h1: {c.get('h1Texts')}"
        return "C", c.get("h1Texts", [""])[0]

    if cid == "9.2":
        jumps = c.get("headingJumps", [])
        return ("NC", str(jumps[0])) if jumps else ("C", "ok")

    if cid == "9.3":
        lm = c.get("landmarks", 0)
        if isinstance(lm, dict):
            has = lm.get("main") and lm.get("nav", 0) >= 1
        else:
            has = lm >= 3
        return ("C", "landmarks") if has else ("NC", "landmarks incomplets")

    if cid == "10.1":
        return ("C", "skip") if c.get("skipLink") else ("NC", "pas de lien évitement")

    if cid == "10.7":
        return "NT", "focus visible — complément humain (accueil C)"

    if cid == "11.1":
        bad = c.get("fieldsNoLabel", [])
        bad = [f for f in bad if f.get("type") not in ("submit", "button")]
        return ("NC", str(bad[:3])) if bad else ("C", "ok")

    if cid == "12.1":
        # site-level: menu + search + plan du site across samples
        has_nav = any(get_collect(all_slugs_data[s]).get("landmarks") for s in all_slugs_data)
        has_plan = "plan-du-site" in all_slugs_data
        has_search = any(
            dget(get_collect(all_slugs_data[s]), "focusableCount", default=0) > 0 for s in all_slugs_data
        )
        if has_nav and has_plan:
            return "C", "menu + plan du site échantillons"
        return "NT", "vérifier moteur recherche + menu + plan"

    if cid == "12.7":
        bad = c.get("tabindexPositive", [])
        return ("NC", str(bad)) if bad else ("C", "ok")

    if cid in ("7.1", "7.3", "7.4"):
        return "NT", "voir human_validation audit-log"

    return "NT", "heuristique non implémentée — revue MCP critère par critère requise"


def aggregate(statuses):
    if "NC" in statuses:
        return "NC"
    if all(s == "NA" for s in statuses):
        return "NA"
    if any(s == "NT" for s in statuses):
        return "NT"
    if any(s == "C" for s in statuses):
        return "C"
    return "NT"


def main():
    import sys

    audit_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "audits/cmvmediforce-fr/2026-06-22"
    samples_dir = audit_dir / "samples"
    human = load_human_overrides(audit_dir)

    slugs_data = {}
    for p in sorted(samples_dir.glob("*.json")):
        slugs_data[p.stem] = json.loads(p.read_text(encoding="utf-8"))

  # Apply human global
    for cid, mp in human.items():
        if "*" in mp and mp["*"][0] == "NC":
            for slug in slugs_data:
                pass  # scored per sample below

    rows = []
    ts = datetime.now(timezone.utc).isoformat()
    slug_order = sorted(slugs_data.keys())

    with (audit_dir / "audit-log.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"event": "repasse_score_start", "timestamp": ts}, ensure_ascii=False) + "\n")

        for theme in RULES["themes"]:
            for criterion in theme["criteria"]:
                cid = criterion["id"]
                row = {
                    "theme_id": theme["id"],
                    "criterion_id": cid,
                    "criterion_title": criterion["title"][:80],
                    "wcag_level": ",".join(criterion.get("wcag_levels", [])),
                }
                statuses = []
                for slug in slug_order:
                    if cid in human and "*" in human[cid]:
                        st, ev = human[cid]["*"]
                        row[slug] = st
                        statuses.append(st)
                    elif cid in human and slug in human[cid]:
                        st, ev = human[cid][slug]
                        row[slug] = st
                        statuses.append(st)
                    else:
                        st, ev = score_criterion(cid, slug, slugs_data[slug], slugs_data, human)
                        row[slug] = st
                        statuses.append(st)
                        if st in ("C", "NC", "NA"):
                            log.write(json.dumps({
                                "event": "criterion_test",
                                "sample": slug,
                                "criterion": cid,
                                "agent_result": "pass" if st == "C" else "fail" if st == "NC" else "na",
                                "criterion_status_agent": st,
                                "evidence": ev,
                                "source": "repasse_mcp",
                                "timestamp": ts,
                            }, ensure_ascii=False) + "\n")
                row["site_status"] = aggregate(statuses)
                row["notes"] = ""
                rows.append(row)

    headers = ["theme_id", "criterion_id", "criterion_title", "wcag_level"] + slug_order + ["site_status", "notes"]
    with (audit_dir / "grid-repasse.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    c = Counter(r["site_status"] for r in rows)
    print(f"grid-repasse.csv: {dict(c)}")


if __name__ == "__main__":
    main()
