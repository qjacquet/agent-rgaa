# Architecture audit RGAA — exécution MCP test par test

## Principe

```
rgaa-rules.json  →  agent (test_result)  →  humain/auto (human_complement)  →  audit-log.jsonl  →  grid.csv
```

**Aucune heuristique Python** ne note C/NC/NA en phase 2. Seules les entrées `test_result` (agent) et `human_complement` (phase 4) dans `audit-log.jsonl` comptent pour la grille.

## Interdit

| ❌ | Pourquoi |
| -- | -------- |
| `run-theme-audit.py`, `score-from-collect.py`, `rgaa-score-enriched.py` | Devinent C/NC sans MCP |
| Collecte bulk → scoring Python | Contourne la méthodologie test par test |
| NT sur test `full` sans exécuter `agent_steps` | Faux NT |
| `user-playwright` | Session incohérente |

## Pipeline

### 1. Initialisation (phase 0–1)

- `audits/{site}/{date}/` — `samples-status.json`, `audit-log.jsonl`

### 2. Passe MCP (phase 2) — 13 sous-agents thématiques

Pour chaque thématique `1…13` :

```bash
python3 scripts/audit/plan-theme.py {theme_id} audits/{site}/{date}/
```

Produit `work-queue/theme-{id}.json` : liste des tests × échantillons pending.

**Sous-agent** (un par thème) :

1. Lire `work-queue/theme-N.json`
2. Pour chaque item :
   - `browser_navigate(sample_url)` — **un seul onglet**
   - `browser_snapshot` (cookies)
   - Pour chaque `agent_step` : outils indiqués dans `mcp_hints`
     - DOM → `browser_cdp` + `scripts/cdp/query-dom.js`
     - Contraste → `scripts/cdp/contrast-scan.js`
     - Clavier → `browser_press_key` (Tab, Enter, Space) + `browser_snapshot`
     - Clic → `browser_click` puis vérifier équivalent clavier
   - Si `at_handoff: true` → `log-result --result nt` (VoiceOver/NVDA seulement)
   - Sinon → `log-result --result pass|fail|na` + `--evidence`
3. `python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/`

### 3. Logger chaque test

```bash
python3 scripts/audit/log-result.py audits/{site}/{date}/ \
  --sample accueil --url "https://..." \
  --theme 1 --criterion 1.1 --test 1.1.1 \
  --scope full --result pass \
  --evidence "12 img, alt/aria ok" \
  --tools browser_navigate,browser_cdp
```

### 4. Agrégation (phase 3)

```bash
python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/
```

Règles : [`scoring.md`](scoring.md) — `fail > nt > pass > na`. Lit `test_result` puis applique les `human_complement` par-dessus.

### 5. Compléments humains (phase 4)

Voir [`human-complement.md`](human-complement.md).

```bash
# Auto-confirm structurel (hors AT/jugement, hors 7.3.x déjà fait)
python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/ --dry-run
python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/

# Puis régénérer
python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/
```

### 6. Reprise

```bash
python3 scripts/audit/resume.py audits/{site}/{date}/
```

## NT légitimes (agent)

| Cas | Action |
| --- | ------ |
| `at_handoff` — restitution VoiceOver/NVDA | `result: nt` + pré-rapport |
| Test `partial` avec `human_steps` AT non exécutées | `result: nt` |
| Impossible techniquement (CAPTCHA, 2FA) | Stop + humain |

Tout le reste (DOM, clavier simulé, contraste, structure) → **pass/fail/na via MCP**.

## Fichiers

| Chemin | Rôle |
| ------ | ---- |
| `scripts/audit/plan-theme.py` | File de travail par thème |
| `scripts/audit/log-result.py` | Écrit `test_result` |
| `scripts/audit/aggregate-grid.py` | `audit-log.jsonl` → `grid.csv` (test_result + human_complement) |
| `scripts/audit/auto-confirm-human.py` | Compléments en lot hors AT/jugement |
| `scripts/audit/resume.py` | Checkpoint |
| `scripts/audit/mcp-hints.py` | Infère outils MCP par étape |
| `scripts/cdp/*.js` | Helpers CDP (pas scoring) |
| `data/rgaa-rules.json` | Référentiel + `agent_steps` |
