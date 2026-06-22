#!/usr/bin/env python3
"""Sauvegarde un échantillon repasse + log audit."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parent.parent / "audits/cmvmediforce-fr/2026-06-22"

PAGES = [
    ("accueil", "https://www.cmvmediforce.fr/"),
    ("tresorerie", "https://www.cmvmediforce.fr/nos-solutions/tresorerie/"),
    ("simulation", "https://www.cmvmediforce.fr/simulation/"),
    ("redirection-formulaire", "https://www.cmvmediforce.fr/redirection-formulaire/"),
    ("publications", "https://www.cmvmediforce.fr/publications/"),
    ("article-fiscalite", "https://www.cmvmediforce.fr/publications/par-themes/fiscalite/vehicule-professionnel-frais-reels-ou-indemnites-kilometriques/"),
    ("mentions-legales", "https://www.cmvmediforce.fr/mentions-legales/"),
    ("faq", "https://www.cmvmediforce.fr/faq/"),
    ("mes-demarches", "https://www.cmvmediforce.fr/mes-demarches-client/"),
    ("plan-du-site", "https://www.cmvmediforce.fr/plan-du-site/"),
    ("contacts", "https://www.cmvmediforce.fr/contacts/"),
]


def save_sample(slug: str, payload: dict, audit_dir: Path = AUDIT):
    out = {
        "slug": slug,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "tools": ["browser_navigate", "Runtime.evaluate:repasse-collect.js"],
        **payload,
    }
    (audit_dir / "samples" / f"{slug}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log = audit_dir / "audit-log.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "event": "cdp_collect",
            "sample": slug,
            "tools": ["collect", "contrast", "meta"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False) + "\n")
    c = payload.get("collect", {})
    print(f"OK {slug}: h1={c.get('h1Count')} linksNoText={len(c.get('linksNoText', []))} contrastFails={payload.get('contrast', {}).get('failCount')}")


if __name__ == "__main__":
    slug, json_path = sys.argv[1], Path(sys.argv[2])
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    val = raw.get("result", {}).get("value", raw)
    save_sample(slug, val)
