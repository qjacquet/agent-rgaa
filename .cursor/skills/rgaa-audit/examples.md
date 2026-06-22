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

## Phase 4 — Pré-rapport 7.3.1

```markdown
#### 7.3.1 — Gestionnaires d'événements clavier/pointage

**Résultat agent** : **C**

**Pour noter C** (confirmation) :
- Vérifier au clavier réel chaque contrôle listé par l'agent
- Toute action au clic doit avoir un équivalent clavier

**Cas NC** :
- Contrôle atteignable à la souris mais pas au Tab
- Action déclenchée au clic sans Entrée/Espace
- Pas d'alternative pour un dispositif de pointage
```

## Phase 4 — Extrait 7.1.2 (partial)

**Résultat agent** : **NT** (étape AT non réalisée)

**Pour noter C** : VoiceOver + Safari — le composant X annonce son nom et son état…
**Cas NC** : le composant est muet ou annonce un nom incohérent…

## Phase 5 — Livrables finaux

- `pre-report.md` — remis en phase 4 (audit non finalisé)
- `grid.csv` — grille mise à jour après complément humain
- `report.md` — rapport final avec mention des NT résolus
