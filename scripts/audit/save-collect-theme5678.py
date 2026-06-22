#!/usr/bin/env python3
"""Save combined theme5678 collect JSON and run batch eval for themes 5-8."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    if len(sys.argv) < 5:
        print("Usage: save-collect-theme5678.py <audit_dir> <sample> <url> <collect_json_path>", file=sys.stderr)
        sys.exit(1)
    audit_dir, sample, url, collect_path = sys.argv[1:5]
    run_script = ROOT / "scripts" / "audit" / "run-theme5678-sample.py"
    subprocess.run(
        [sys.executable, str(run_script), audit_dir, sample, url, collect_path],
        check=True,
    )


if __name__ == "__main__":
    main()
