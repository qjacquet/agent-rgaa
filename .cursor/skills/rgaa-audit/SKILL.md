---
name: rgaa-audit
description: >
  Réalise un audit d'accessibilité RGAA 4.1.2 sur des pages web : échantillonnage,
  tests critère par critère selon rules.html, notation C/NC/NA/NT, relais humain
  pour les points non testables, reporting CSV et Markdown. Utiliser quand
  l'utilisateur demande un audit RGAA, une conformité accessibilité, ou cite
  les critères/tests RGAA.
disable-model-invocation: true
---

# Audit RGAA 4.1.2

Auditeur automatisé RGAA. Référentiel : [`data/rgaa-rules.json`](../../../data/rgaa-rules.json) (généré depuis [`rules.html`](../../../rules.html)).

## MCP navigateur — règle absolue

**Utiliser exclusivement le MCP `cursor-ide-browser`.**

- **Interdit** : `user-playwright` ou tout autre MCP navigateur (ouvre un navigateur séparé, session perdue, incohérent avec l'audit).
- **Un seul onglet** Cursor pour tout l'audit : `browser_navigate`, jamais `browser_tabs` « new ».
- **Outils RGAA** : pas d'extensions Chrome installables — substituts **CDP obligatoires** (voir [chromium-cdp-tools.md](chromium-cdp-tools.md)).
- JS / DOM / AX / contrastes : `browser_cdp` (`Runtime.evaluate`, `Accessibility.getFullAXTree`, `CSS.getComputedStyleForNode`, `DOM.querySelector`).
- Clavier : `browser_press_key` + `browser_snapshot` (pas `Input.*` CDP).
- Attente chargement : polling via `browser_snapshot` ou `browser_cdp`, pas d'autre MCP.

### Vérification CDP avant phase 2

Sur le **premier échantillon** de l'audit :

1. Exécuter la suite documentée dans [chromium-cdp-tools.md](chromium-cdp-tools.md) § « Suite CDP obligatoire ».
2. Sauver le résultat dans `audits/{site}/{date}/cdp-verification.json`.
3. **Stop** si `Accessibility.getFullAXTree` ou `Runtime.evaluate` échouent — ne pas continuer avec des faux NT.

## Ressources (lire à la demande)

- [chromium-cdp-tools.md](chromium-cdp-tools.md) — **substituts CDP obligatoires** (liste, vérification, interdictions)
- [scoring.md](scoring.md) — notation C / NC / NA / NT
- [tools-mapping.md](tools-mapping.md) — outils MCP et substituts
- [test-environment.md](test-environment.md) — **agent vs humain, VoiceOver/NVDA, combinaisons RGAA**
- [risks.md](risks.md) — registre des risques par phase
- [human-handoff.md](human-handoff.md) — gabarit relais humain (condensé)
- [pre-report-template.md](pre-report-template.md) — **pré-rapport NT (livrable obligatoire)**
- [report-template.md](report-template.md) — gabarit rapport final
- [examples.md](examples.md) — exemple de déroulé

## Phase 0 — Initialisation

1. Charger `data/rgaa-rules.json` ; si absent : `python3 scripts/extract-rules.py rules.html -o data/rgaa-rules.json`
2. **Exiger** de l'utilisateur :
   - URL de base du site
   - **Liste d'URLs d'échantillons** (minimum 1)
   - Contexte : desktop / mobile / les deux
   - Environnement maîtrisé ou non (cf. [test-environment.md](test-environment.md))
   - **Qui réalise les tests AT** (VoiceOver, NVDA, TalkBack…) : l'utilisateur en phase 4, ou audit partiel accepté
   - Si site protégé : **URL page d'authentification**, identifiants, instructions (champs non standards)
3. Créer `audits/{site-slug}/{YYYY-MM-DD}/`
4. Initialiser `audit-log.jsonl`, `samples-status.json`, `grid.csv` (vide)
5. Si auth requise : exécuter le flux d'authentification **avant** la validation des échantillons

## Phase 1 — Validation des échantillons

### Flux d'authentification (si 401/403 ou redirection login)

1. **Stop** l'échantillon bloqué
2. Demander : URL page login, login, mot de passe, instructions complémentaires
3. Sur **le même onglet** : `browser_navigate` → login → `browser_snapshot` → `browser_fill` → `browser_click`
4. Vérifier succès (URL, contenu, pas de message d'erreur) ; logger `auth_success` ou `auth_failed` dans `audit-log.jsonl`
5. **Tout l'audit** utilise ce même onglet (`browser_navigate` uniquement, jamais nouvel onglet)
6. Reprendre la validation de l'échantillon bloqué

Hors périmètre v1 : 2FA, CAPTCHA, SSO externe → escalade humaine.

### Validation par URL

Pour chaque échantillon sur l'onglet de session :

| Code / situation | Action |
| ---------------- | ------ |
| **404** | **Stop** ; demander URL de remplacement (même type de page) |
| **401 / 403** | **Stop** → flux auth |
| **500 / 502 / 503** | **Stop immédiat** ; marquer `blocked` ; **demander à l'humain la procédure** pour atteindre un état auditable (étapes formulaire, URL intermédiaire, données de test, exclusion de l'échantillon). **Ne pas deviner** — attendre la réponse avant de continuer |
| **302 → login** | **Stop** → flux auth |
| **200 vide / erreur métier** | **Stop** ; demander instructions |
| **Timeout** | 1 retry puis **Stop** |

### Erreur 500 — message type à l'humain

> L'échantillon `{url}` renvoie **HTTP 500**. Je ne peux pas l'auditer dans cet état.
>
> Merci d'indiquer **la procédure** pour y accéder (ex. remplir le formulaire de simulation puis valider, URL avec paramètres, autre page équivalente) **ou** confirmer l'**exclusion** de cet échantillon.

Consigner la procédence fournie dans `samples-status.json` (`notes`, `human_procedure`).

Enregistrer dans `samples-status.json` : `{ "url": "...", "status": "ok|blocked|replaced", "http_code": 200, "notes": "" }`

Fermer bandeaux cookies/modales repérés au snapshot avant de valider.

**Règle** : aucun critère noté tant qu'un échantillon est `blocked`. Reprendre quand tous sont `ok` ou exclus/remplacés par l'utilisateur.

## Phase 2 — Première passe

**Session** : même onglet que l'auth. Si page login réapparaît → session expirée : Stop, reconnexion, reprendre au dernier checkpoint dans `audit-log.jsonl`.

### Suite CDP obligatoire par échantillon

Avant de noter le moindre critère sur une page, exécuter **tous** les outils de [chromium-cdp-tools.md](chromium-cdp-tools.md) :

| # | Action MCP | Script / méthode |
| - | ---------- | ---------------- |
| 1 | `browser_navigate` | URL échantillon |
| 2 | `browser_snapshot` | Fermer cookies si présents |
| 3 | `Accessibility.getFullAXTree` | Arbre AX complet |
| 4 | `Runtime.evaluate` | `scripts/repasse-collect.js` |
| 5 | `browser_press_key` | Si critères 7.3 / 12.8 applicables |
| 6 | Sauver | `audits/.../samples/{slug}.json` enrichi |

Logger : `{ "event": "cdp_collect", "sample", "tools": ["snapshot","axtree","collect","contrast",...] }`.

**Collecte multi-échantillons** : déléguer à un **subagent** (`generalPurpose`) qui utilise **uniquement** le MCP `cursor-ide-browser` (navigate + CDP + Write). **Interdit** : scripts shell/CLI (`curl`, `requests`, Playwright, Python hors sauvegarde JSON) pour parcourir ou tester les pages.

**Interdit en phase 2** :

- Noter **NT** sur un test `agent_scope: full` sans avoir exécuté ses `agent_steps` via MCP.
- Générer la grille uniquement via `score-from-collect.py` sans collecte MCP préalable.
- Omettre `Accessibility.getFullAXTree` ou le scan contrastes.

**Ordre** : pour chaque échantillon `ok`, parcourir les **106 critères** (thématiques 1→13) dans l'ordre du JSON.

Pour chaque critère :

1. Lire titre + tests dans `rgaa-rules.json`
2. Pré-qualifier **NA** si hors périmètre manifeste (justification + preuve)
3. Pour chaque test applicable, selon `agent_scope` dans le JSON :

| `agent_scope` | Action agent | Résultat agent |
| ------------- | ------------ | -------------- |
| **`full`** | Exécuter toutes les `agent_steps` (ou `methodology_steps` si pas de split) | **C / NC / NA** |
| **`partial`** | Exécuter uniquement `agent_steps` | **C / NC / NA** sur la partie auto ; test **NT** si `human_steps` non satisfaites |
| **`at_only`** | Pré-analyse DOM/AX (`pre_analysis`) uniquement | **NT** — pas de C/NC agent |

4. L'agent **n'utilise jamais** VoiceOver, NVDA, JAWS ni TalkBack pour les `human_steps`.

5. Logger dans `audit-log.jsonl` :

```json
{
  "sample": "{url}",
  "criterion": "7.3",
  "test": "7.3.1",
  "agent_scope": "full",
  "agent_result": "pass|fail|na|nt",
  "criterion_status_agent": "C|NC|NA|NT",
  "human_complement_required": true,
  "pre_analysis": "...",
  "evidence": "...",
  "timestamp": "..."
}
```

6. Exemple **7.3** : l'agent parcourt les gestionnaires d'événements (`browser_press_key` Tab/Enter, `browser_click` pour pointage), note **C** ou **NC**, puis le pré-rapport documente **Pour noter C** / **Cas NC** pour confirmation humaine clavier/pointage réel.

Entre échantillons : `browser_navigate` sur le même onglet.

## Phase 3 — Notation provisoire

Appliquer [scoring.md](scoring.md). Remplir `grid.csv` avec statuts **provisoires** (les NT ne sont pas des C).

## Phase 4 — Pré-rapport et relais humain

Générer **`pre-report.md`** (obligatoire si `human_complement_required` ou NT) via [pre-report-template.md](pre-report-template.md).

Pour **chaque** test concerné, inclure obligatoirement :
- **Résultat agent** (C / NC / NA / NT)
- **Pour noter C** — critères de succès explicites (`success_criterion` + `human_steps`)
- **Cas NC** — conditions d'échec explicites (`failure_criterion`)

Inclure notamment les tests **7.3.x** : l'agent a déjà noté C/NC ; le pré-rapport demande la **confirmation humaine** clavier/pointage réel.

1. **Stopper** ; remettre le pré-rapport — audit non finalisé
2. Collecter réponses : `{critère} | {url} | {test_id} | C|NC|NA | commentaire`
3. Mettre à jour grille ; phase 5 si complet ou audit partiel accepté

## Phase 5 — Rapport final

Générer depuis la même source (`audit-log.jsonl` + grille) :

- `report.md` — via [report-template.md](report-template.md), mentionnant que le pré-rapport a été complété
- `grid.csv` — version **finale**

Mentionner obligatoirement : périmètre, limites, statut complet/partiel, méthodologie, références RGAA 4.1.2.

## Reprise après interruption

1. Lire `audit-log.jsonl` ; identifier dernier `{sample, criterion, test}` complété
2. Rouvrir le même onglet navigateur ; ré-authentifier si nécessaire
3. Reprendre au critère/test suivant

## Checklist finale

- [ ] Tous échantillons `ok` ou exclus documentés
- [ ] 106 critères traités par échantillon (ou NA justifié)
- [ ] `pre-report.md` généré et remis si NT (procédures humaines explicites)
- [ ] NT listés et traités (humain ou audit partiel accepté)
- [ ] `grid.csv` final + `report.md` générés et cohérents
- [ ] Preuves (captures) liées aux NC
