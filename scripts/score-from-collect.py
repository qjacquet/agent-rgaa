#!/usr/bin/env python3
"""DEPRECATED — supprimé. Utiliser scripts/audit/aggregate-grid.py."""
import sys

print(
    "DEPRECATED: score-from-collect.py utilisait des heuristiques Python.\n"
    "Exécuter les tests via MCP, logger avec scripts/audit/log-result.py,\n"
    "puis agréger avec scripts/audit/aggregate-grid.py\n"
    "Voir .cursor/skills/rgaa-audit/architecture.md",
    file=sys.stderr,
)
sys.exit(1)
