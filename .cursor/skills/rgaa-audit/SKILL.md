---
name: rgaa-audit
description: >
  Réalise un audit d'accessibilité RGAA 4.1.2 sur des pages web : échantillonnage,
  tests critère par critère selon rules.html, notation C/NC/NA, compléments humains
  (interactif, auto-confirm, AT), relais humain pour les points non testables,
  reporting CSV et Markdown. Utiliser quand l'utilisateur demande un audit RGAA,
  une conformité accessibilité, ou cite les critères/tests RGAA.
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

- [architecture.md](architecture.md) — **pipeline MCP test par test** (obligatoire)
- [chromium-cdp-tools.md](chromium-cdp-tools.md) — **substituts CDP obligatoires** (liste, vérification, interdictions)
- [scoring.md](scoring.md) — notation C / NC / NA / NT
- [tools-mapping.md](tools-mapping.md) — outils MCP et substituts
- [test-environment.md](test-environment.md) — **agent vs humain, VoiceOver/NVDA, combinaisons RGAA**
- [risks.md](risks.md) — registre des risques par phase
- [human-handoff.md](human-handoff.md) — gabarit relais humain (condensé)
- [human-complement.md](human-complement.md) — **phase 4 : tiers AT/jugement/auto, AskQuestion, auto-confirm**
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

Consigner la procédure fournie dans `samples-status.json` (`notes`, `human_procedure`).

**Pages multi-étapes** : une URL peut nécessiter une navigation préalable (formulaire, assistant). L'humain fournit la procédure ; l'agent la rejoue sur le même onglet avant d'auditer.

Enregistrer dans `samples-status.json` : `{ "url": "...", "status": "ok|blocked|replaced", "http_code": 200, "notes": "" }`

Fermer bandeaux cookies/modales repérés au snapshot avant de valider.

**Règle** : aucun critère noté tant qu'un échantillon est `blocked`. Reprendre quand tous sont `ok` ou exclus/remplacés par l'utilisateur.

## Phase 2 — Première passe (MCP test par test)

Voir **[architecture.md](architecture.md)** — aucune heuristique Python.

**Session** : même onglet que l'auth. Si page login réapparaît → session expirée : Stop, reconnexion, `scripts/audit/resume.py`.

### Découpage — 13 sous-agents (un par thématique)

```bash
python3 scripts/audit/plan-theme.py {1..13} audits/{site}/{date}/
```

Chaque sous-agent :

1. Lit `work-queue/theme-N.json`
2. Pour chaque test × échantillon : exécute **toutes** les `agent_steps` via MCP
3. Loggue via `scripts/audit/log-result.py`
4. Ne marque **NT** que si `at_handoff` (VoiceOver/NVDA) ou `human_steps` AT — sinon **pass/fail/na obligatoire** (politique zéro NT sur `agent_scope: full`)

### Outils MCP par type d'étape

| Besoin | MCP |
| ------ | --- |
| DOM, attributs | `browser_cdp` → `Runtime.evaluate(scripts/cdp/query-dom.js)` |
| Contraste | `scripts/cdp/contrast-scan.js` |
| **Clavier** | **`browser_press_key`** (Tab, Enter, Space, Escape) + `browser_snapshot` |
| Clic / formulaire | `browser_click`, `browser_fill` |
| Arbre AX | `Accessibility.getFullAXTree` |
| Preuve NC | `browser_take_screenshot` |

**Interdit** : `score-from-collect.py`, `run-theme-audit.py`, `rgaa-score-enriched.py` (supprimés — heuristiques).

### Suite CDP par échantillon (avant tests du thème)

Sur chaque nouvelle page naviguée :

1. `browser_navigate(url)` 2. `browser_snapshot` 3. cookies fermés
4. `Accessibility.getFullAXTree` si arbre AX requis par le test
5. Exécuter les `agent_steps` du test en cours

Optionnel : `scripts/audit/save-evidence.py` pour archiver un snapshot DOM (preuve), **pas pour scorer**.

Logger : `{ "event": "test_result", ... }` via `log-result.py`.

**Collecte multi-échantillons** : déléguer à un **subagent par thématique** (`generalPurpose`) — MCP `cursor-ide-browser` uniquement.

**Interdit en phase 2** :

- Noter **NT** sur un test `agent_scope: full` sans avoir exécuté ses `agent_steps` via MCP
- Générer la grille via Python sans entrées `test_result` dans `audit-log.jsonl`
- Scripts heuristiques (`if h1Count > 1 then NC`)

**Ordre** : thématiques 1→13 ; au sein de chaque thème, critères et tests dans l'ordre du JSON ; pour chaque test, les 11 échantillons.

Pour chaque test :

| `agent_scope` | Action agent | Résultat |
| ------------- | ------------ | -------- |
| **`full`** | Exécuter toutes les `agent_steps` via MCP | **pass / fail / na** → C/NC/NA |
| **`partial`** | Exécuter `agent_steps` ; `human_steps` AT → nt | C/NC/NA ou nt |
| **`at_only`** | — | **nt** (VoiceOver/NVDA) |

5. Logger :

```bash
python3 scripts/audit/log-result.py audits/.../ \
  --sample {slug} --url {url} --theme {id} --criterion {cid} --test {tid} \
  --scope full --result pass|fail|na|nt --evidence "..." --tools browser_navigate,browser_cdp,browser_press_key
```

6. **7.3** : parcourir les focusables avec `browser_press_key` Tab + Enter ; noter **pass/fail** ; pré-rapport pour confirmation humaine si `human_complement_required`.

Entre échantillons : `browser_navigate` sur le même onglet.

## Phase 3 — Notation provisoire

```bash
python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/
```

Appliquer [scoring.md](scoring.md). Source : `test_result` + `human_complement` (si présent) dans `audit-log.jsonl`.

## Phase 4 — Pré-rapport et compléments humains

Voir **[human-complement.md](human-complement.md)** pour le détail complet.

Générer **`pre-report.md`** (obligatoire si `human_complement_required` ou NT) via [pre-report-template.md](pre-report-template.md).

Pour **chaque** test concerné, inclure obligatoirement :
- **Résultat agent** (C / NC / NA / NT)
- **Pour noter C** — critères de succès explicites (`success_criterion` + `human_steps`)
- **Cas NC** — conditions d'échec explicites (`failure_criterion`)

### Ordre de traitement recommandé

1. **7.3.x** — complément interactif (AskQuestion, clavier réel) sur chaque page applicable ; logger `human_complement` avec `source: interactive_keyboard`
2. **Auto-confirm** — `python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/ --dry-run` puis exécution ; reprend le résultat agent hors AT/jugement
3. **AT + jugement** — humain avec lecteur d'écran ou requalification (thématique images, `3.1`, `4.2`, tests `partial` AT)
4. **NA agent** — ne pas redemander de complément

### Collecte des réponses

Format texte : `{critère} | {url} | {test_id} | C|NC|NA | commentaire`

Ou entrées directes dans `audit-log.jsonl` :

```json
{"event":"human_complement","criterion":"7.3","test":"7.3.1","human_result":"pass","source":"interactive_keyboard",...}
```

Après chaque lot : `aggregate-grid.py`.

1. **Stopper** après le pré-rapport initial — audit non finalisé
2. Traiter les compléments (interactif → auto-confirm → AT/jugement)
3. Régénérer grille ; phase 5 si complet ou audit partiel accepté

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

- [ ] Toutes les pages `ok` ou exclus documentées (`samples-status.json`, `human_procedure` si besoin)
- [ ] 106 critères traités par page (ou NA justifié)
- [ ] `pre-report.md` généré et remis si compléments ou NT
- [ ] Compléments 7.3.x traités interactivement (non auto-confirmés)
- [ ] Auto-confirm exécuté pour tier structurel (si accepté par l'utilisateur)
- [ ] Compléments AT/jugement renseignés ou audit partiel documenté
- [ ] `grid.csv` final + `report.md` générés et cohérents
- [ ] Preuves (captures) liées aux NC
