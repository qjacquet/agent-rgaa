#!/usr/bin/env python3
"""Save CDP collect and log themes 9-11 only (skip already logged)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_SCRIPTS = ROOT / "scripts" / "audit"


def logged_tests(audit_dir: Path) -> set[tuple[str, str, str]]:
    log = audit_dir / "audit-log.jsonl"
    done: set[tuple[str, str, str]] = set()
    if not log.exists():
        return done
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("event") == "test_result" and e.get("theme_id") in ("9", "10", "11"):
            done.add((e["theme_id"], e["test"], e["sample"]))
    return done


THEME_TESTS = {
        "9": ["9.1.1", "9.1.2", "9.1.3", "9.2.1", "9.3.1", "9.3.2", "9.3.3", "9.4.1", "9.4.2"],
        "10": [
            "10.1.1", "10.1.2", "10.1.3", "10.2.1", "10.3.1", "10.4.1", "10.4.2",
            "10.5.1", "10.5.2", "10.5.3", "10.6.1", "10.7.1", "10.8.1",
            "10.9.1", "10.9.2", "10.9.3", "10.9.4", "10.10.1", "10.10.2", "10.10.3", "10.10.4",
            "10.11.1", "10.11.2", "10.12.1", "10.13.1", "10.13.2", "10.13.3", "10.14.1", "10.14.2",
        ],
        "11": [
            "11.1.1", "11.1.2", "11.1.3", "11.2.1", "11.2.2", "11.2.3", "11.2.4", "11.2.5", "11.2.6",
            "11.3.1", "11.3.2", "11.4.1", "11.4.2", "11.4.3", "11.5.1", "11.6.1", "11.7.1",
            "11.8.1", "11.8.2", "11.8.3", "11.9.1", "11.9.2", "11.10.1", "11.10.2", "11.10.3",
            "11.10.4", "11.10.5", "11.10.6", "11.10.7", "11.11.1", "11.11.2", "11.12.1", "11.12.2", "11.13.1",
        ],
}


def skip_for_sample(done: set[tuple[str, str, str]], sample: str, theme: str) -> str:
    return ",".join(t for t in THEME_TESTS[theme] if (theme, t, sample) in done)


def extract(raw: dict) -> dict:
    if "exceptionDetails" in raw:
        raise SystemExit(f"CDP error: {raw['exceptionDetails']}")
    r = raw.get("result", raw)
    if isinstance(r, dict) and "value" in r:
        return r["value"]
    if "value" in raw:
        return raw["value"]
    raise SystemExit(f"No value in {list(raw.keys())}")


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: run-theme911-only.py <audit_dir> <sample> <url> <mcp_cdp.json>", file=sys.stderr)
        sys.exit(1)
    audit_dir = Path(sys.argv[1])
    sample, url, mcp_path = sys.argv[2], sys.argv[3], sys.argv[4]
    done = logged_tests(audit_dir)
    data = extract(json.loads(Path(mcp_path).read_text(encoding="utf-8")))

    ev_dir = audit_dir / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    combined = ev_dir / f"{sample}-theme911-combined.json"
    combined.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for theme in ("9", "10", "11"):
        skip = skip_for_sample(done, sample, theme)
        if len(skip.split(",")) == len(THEME_TESTS[theme]) and skip:
            print(f"Theme {theme} @{sample}: all skipped")
            continue
        theme_path = ev_dir / f"{sample}-theme{theme}.json"
        key = f"theme{theme}"
        theme_path.write_text(
            json.dumps(data.get(key, data), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        cmd = [
            sys.executable,
            str(AUDIT_SCRIPTS / f"eval-theme{theme}-batch.py"),
            str(audit_dir),
            "--sample", sample,
            "--url", url,
            "--collect", str(theme_path),
        ]
        if skip:
            cmd.extend(["--skip", skip])
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
