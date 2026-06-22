#!/usr/bin/env python3
"""Batch-save theme234 collects from JSON files and log all audit results."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "scripts" / "audit"


def process_sample(audit_dir: Path, sample: str, url: str, payload: dict) -> None:
    ev_dir = audit_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    for theme in ("2", "3", "4"):
        key = f"theme{theme}"
        data = payload.get(key)
        if not data:
            continue
        path = ev_dir / f"{sample}-theme{theme}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(AUDIT / f"eval-theme{theme}-batch.py"),
                str(audit_dir),
                "--sample", sample,
                "--url", url,
                "--collect", str(path),
            ],
            check=True,
        )


def main() -> None:
    audit_dir = Path(sys.argv[1])
    batch = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    for item in batch:
        process_sample(audit_dir, item["sample"], item["url"], item["data"])
        print(f"OK {item['sample']}")


if __name__ == "__main__":
    main()
