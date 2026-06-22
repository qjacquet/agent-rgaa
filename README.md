# agent-rgaa

Skill Cursor pour auditer l'accessibilité web selon le **RGAA 4.1.2**.

## Architecture

**Exécution MCP test par test** — pas de heuristiques Python.

Voir [`.cursor/skills/rgaa-audit/architecture.md`](.cursor/skills/rgaa-audit/architecture.md).

```
plan-theme.py → sous-agent MCP (×13 thèmes) → log-result.py → aggregate-grid.py
                                                      ↓
                              human-complement (interactif / auto-confirm) → aggregate-grid.py
```

Phase 4 : voir [human-complement.md](.cursor/skills/rgaa-audit/human-complement.md).

## Contenu

| Fichier | Rôle |
| ------- | ---- |
| [`rules.html`](rules.html) | Référentiel source (106 critères, 258 tests) |
| [`data/rgaa-rules.json`](data/rgaa-rules.json) | Référentiel structuré + `agent_steps` |
| [`scripts/audit/`](scripts/audit/) | Pipeline (plan, log, aggregate, auto-confirm-human, resume) |
| [`scripts/cdp/`](scripts/cdp/) | Helpers JS appelés pendant un test |
| [`.cursor/skills/rgaa-audit/`](.cursor/skills/rgaa-audit/) | Skill d'audit |

## Prérequis

- Cursor avec MCP **`cursor-ide-browser` uniquement**
- Python 3 + `beautifulsoup4` pour régénérer le JSON

```bash
python3 -m pip install -r requirements.txt
python3 scripts/extract-rules.py rules.html -o data/rgaa-rules.json
```

## Utilisation

```
/rgaa-audit
```

L'agent exécute chaque test via MCP (DOM, CDP, **clavier simulé** `browser_press_key`). VoiceOver/NVDA : **NT** + pré-rapport uniquement (~6 tests AT).

## Scripts principaux

```bash
# File de travail thème N
python3 scripts/audit/plan-theme.py 7 audits/{site}/{date}/

# Après chaque test MCP
python3 scripts/audit/log-result.py audits/{site}/{date}/ \
  --sample accueil --url "https://..." --theme 1 --criterion 1.1 --test 1.1.1 \
  --scope full --result pass --evidence "..." --tools browser_navigate,browser_cdp

# Grille
python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/

# Reprise
python3 scripts/audit/resume.py audits/{site}/{date}/
```

## Sorties d'audit

`audits/{site-slug}/{date}/` : `audit-log.jsonl`, `grid.csv`, `work-queue/`, `pre-report.md`, `report.md`

## Références

- [Méthodologie de test RGAA](https://accessibilite.numerique.gouv.fr/ressources/methodologie-de-test/)
- [Critères et tests](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/)
