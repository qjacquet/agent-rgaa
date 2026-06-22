# Exemple — audit RGAA réduit

Scénario : 2 échantillons, 3 critères (1.1, 8.9, 12.7).

## Entrée utilisateur

```
Site : https://exemple.fr
Échantillons :
- https://exemple.fr/ (accueil)
- https://exemple.fr/contact (formulaire)
Contexte : desktop
Auth : non
```

## Phase 1 — Validation

```
audit-log.jsonl :
{"event":"sample_validate","url":"https://exemple.fr/","http":200,"status":"ok"}
{"event":"sample_validate","url":"https://exemple.fr/contact","http":200,"status":"ok"}
```

## Phase 2 — Extrait critère 1.1 sur accueil

Test 1.1.1 — méthodologie :
1. Retrouver `<img>` et `role="img"` → `browser_evaluate` (snippet images)
2. Déterminer si porteuse d'info → si ambigu : `nt`
3. Vérifier alt / aria-label / aria-labelledby / title
4. Résultat : `fail` si logo header sans alt

```json
{"sample":"https://exemple.fr/","criterion":"1.1","test":"1.1.1","result":"fail","evidence":"img.logo src=/logo.svg alt absent"}
```

## Phase 3 — Notation partielle

| Critère | Accueil | Contact | Site |
| ------- | ------- | ------- | ---- |
| 1.1 | NC | C | NC |
| 8.9 | C | NT | NT |
| 12.7 | NA | C | C |

## Phase 2 — Extrait 7.3.1 (agent conclut)

```json
{"sample":"https://exemple.fr/","criterion":"7.3","test":"7.3.1","agent_scope":"full","agent_result":"pass","criterion_status_agent":"C","human_complement_required":true,"evidence":"12 contrôles Tab+Enter OK"}
```

## Phase 4 — Complément humain 7.3.1 (interactif)

```json
{
  "event": "human_complement",
  "sample": "accueil",
  "criterion": "7.3",
  "test": "7.3.1",
  "human_result": "pass",
  "comment": "Tab menu OK, skip link OK, pas de click-only",
  "source": "interactive_keyboard"
}
```

## Phase 4 — Auto-confirm structurel

```bash
python3 scripts/audit/auto-confirm-human.py audits/exemple-fr/2026-01-15/ --dry-run
python3 scripts/audit/auto-confirm-human.py audits/exemple-fr/2026-01-15/
python3 scripts/audit/aggregate-grid.py audits/exemple-fr/2026-01-15/
```

Entrée produite :

```json
{
  "event": "human_complement",
  "test": "12.7.1",
  "human_result": "pass",
  "agent_result": "pass",
  "source": "auto_confirmed_agent",
  "policy": "all_except_at_judgment",
  "comment": "Auto-confirmé : reprend le résultat agent (hors AT/jugement)"
}
```

## Phase 4 — Extrait 7.1.2 (partial, tier AT)

**Résultat agent** : **NT** (étape AT non réalisée)

**Pour noter C** : VoiceOver + Safari — le composant X annonce son nom et son état…
**Cas NC** : le composant est muet ou annonce un nom incohérent…

## Phase 5 — Livrables finaux

- `pre-report.md` — remis en phase 4 (audit non finalisé)
- `grid.csv` — grille mise à jour après complément humain
- `report.md` — rapport final avec mention des NT résolus
