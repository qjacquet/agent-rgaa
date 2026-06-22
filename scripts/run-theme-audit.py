#!/usr/bin/env python3
"""DEPRECATED — supprimé. Utiliser scripts/audit/plan-theme.py + MCP."""
import sys

print(
    "DEPRECATED: run-theme-audit.py devinait C/NC sans MCP.\n"
    "Voir scripts/audit/plan-theme.py et architecture.md",
    file=sys.stderr,
)
sys.exit(1)
