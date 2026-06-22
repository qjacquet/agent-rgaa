# Sous-agent — thématique RGAA (prompt type)

Copier-coller en lançant un subagent `generalPurpose` par thème.

---

## Mission

Exécuter la thématique **{theme_id} — {theme_title}** sur le site CMV médiforce.

**MCP exclusivement** : `cursor-ide-browser` (un seul onglet, `browser_navigate` only).

**Interdit** : heuristiques Python, `run-theme-audit.py`, Playwright.

## Fichiers

- File de travail : `audits/cmvmediforce-fr/2026-06-22/work-queue/theme-{theme_id}.json`
- Logger : `python3 scripts/audit/log-result.py audits/cmvmediforce-fr/2026-06-22/ ...`
- Référentiel : `data/rgaa-rules.json`
- Helpers CDP : `scripts/cdp/query-dom.js`, `contrast-scan.js`, `keyboard-map.js`

## Pour chaque item dans `work-queue/theme-{theme_id}.json`

1. Si `at_handoff: true` → log `--result nt` avec evidence « restitution AT requise »
2. Sinon :
   - `browser_navigate(sample_url)`
   - `browser_snapshot` — fermer cookies
   - Pour chaque étape dans `agent_steps` :
     - DOM → `browser_cdp` Runtime.evaluate(`scripts/cdp/query-dom.js`)
     - Contraste → `contrast-scan.js`
     - Clavier → `browser_press_key` Tab/Enter/Space + `browser_snapshot` après chaque focus
     - Clic requis → `browser_click` puis vérifier équivalent clavier
   - Décider `pass|fail|na` selon `success_criterion` / `failure_criterion`
   - `browser_take_screenshot` si fail
3. `log-result.py` avec `--tools` listant les MCP utilisés

## Fin

```bash
python3 scripts/audit/aggregate-grid.py audits/cmvmediforce-fr/2026-06-22/
```

Retourner : nombre de tests pass/fail/na/nt pour ce thème.
