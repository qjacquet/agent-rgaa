# Scripts CDP — helpers par test

Ces fichiers sont exécutés via **`browser_cdp` → `Runtime.evaluate`** pendant l'exécution d'un **test** RGAA.

**Interdit** : lancer une collecte bulk sur toutes les pages puis scorer en Python (`score-from-collect.py`, `run-theme-audit.py` — supprimés).

| Fichier | Quand l'appeler |
| ------- | --------------- |
| `query-dom.js` | Étapes « retrouver / vérifier présence » (images, liens, titres, formulaires…) |
| `contrast-scan.js` | Critères 3.1, 3.2, 3.3 |
| `keyboard-map.js` | Avant parcours Tab — 7.3, 12.8, 11.x |

Les anciens fichiers à la racine `scripts/` (`page-audit-collect.js`, `enrich-collect.js`) restent pour compatibilité evidence ; préférer `query-dom.js`.
