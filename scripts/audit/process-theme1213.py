#!/usr/bin/env python3
"""Process MCP CDP collect JSON -> save evidence + log themes 12-13 only."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_SCRIPTS = ROOT / "scripts" / "audit"


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    raise SystemExit(f"No value in {list(raw.keys())}")


def save_and_eval(audit_dir: Path, sample: str, url: str, payload: dict) -> None:
    ev_dir = audit_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    combined = ev_dir / f"{sample}-theme1213-combined.json"
    combined.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for theme in ("12", "13"):
        path = ev_dir / f"{sample}-theme{theme}.json"
        key = f"theme{theme}"
        theme_data = payload.get(key, payload)
        path.write_text(json.dumps(theme_data, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [
            sys.executable,
            str(AUDIT_SCRIPTS / f"eval-theme{theme}-batch.py"),
            str(audit_dir),
            "--sample",
            sample,
            "--url",
            url,
            "--collect",
            str(path),
        ]
        if theme == "12":
            cmd.extend(["--sample-slug", sample])
        subprocess.run(cmd, check=True)


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: process-theme1213.py <audit_dir> <sample> <url> <mcp_cdp.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    sample, url, mcp_path = sys.argv[2], sys.argv[3], Path(sys.argv[4])
    raw = json.loads(mcp_path.read_text(encoding="utf-8"))
    payload = extract(raw)
    save_and_eval(audit_dir, sample, url, payload)
    print(f"Theme 12+13 logged for {sample}")


if __name__ == "__main__":
    main()
