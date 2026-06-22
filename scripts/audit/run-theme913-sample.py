#!/usr/bin/env python3
"""Save theme 9-13 CDP collects and batch-log results for one sample."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_SCRIPTS = ROOT / "scripts" / "audit"


def save_and_eval(audit_dir: Path, sample: str, url: str, theme: str, data: dict, skip: str = "") -> None:
    ev_dir = audit_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    path = ev_dir / f"{sample}-theme{theme}.json"
    key = f"theme{theme}"
    payload = data.get(key, data) if key in data else data
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    eval_script = AUDIT_SCRIPTS / f"eval-theme{theme}-batch.py"
    cmd = [
        sys.executable, str(eval_script), str(audit_dir),
        "--sample", sample, "--url", url, "--collect", str(path),
    ]
    if skip:
        cmd.extend(["--skip", skip])
    if theme == "12":
        cmd.extend(["--sample-slug", sample])
    subprocess.run(cmd, check=True)


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: run-theme913-sample.py <audit_dir> <sample> <url> <collect_json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    sample, url = sys.argv[2], sys.argv[3]
    payload = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
    skip = sys.argv[5] if len(sys.argv) > 5 else ""
    combined = audit_dir / "evidence" / f"{sample}-theme913-combined.json"
    combined.parent.mkdir(parents=True, exist_ok=True)
    combined.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for theme in ("9", "10", "11", "12", "13"):
        save_and_eval(audit_dir, sample, url, theme, payload, skip)


if __name__ == "__main__":
    main()
