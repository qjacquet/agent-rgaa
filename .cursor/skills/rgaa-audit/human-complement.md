# Compléments humains — phase 4

Après la passe agent (phase 2) et l'agrégation provisoire (phase 3), certains tests portent le flag `human_complement_required` dans `rgaa-rules.json`. L'agent a **déjà noté** C/NC/NA ; la phase 4 **confirme ou infirme** ce résultat — ce n'est pas un second audit complet.

## Politique zéro NT (passe agent)

Sur les tests `agent_scope: full`, l'agent **doit** conclure `pass`, `fail` ou `na` via MCP. **NT n'est pas une échappatoire** pour éviter un test difficile.

Les seuls NT légitimes en phase 2 :
- `agent_scope: partial` ou `at_only` avec `human_steps` AT non réalisables par MCP
- blocage technique documenté (CAPTCHA, iframe inaccessible, etc.)

## Ce que l'agent ne peut pas remplacer

| Limite | Conséquence typique |
| ------ | ------------------- |
| Pas de lecteur d'écran réel | Faux positifs sur restitution AT ; complément humain obligatoire |
| Clavier simulé ≠ clavier réel | Focus peu visible, sauts de focus, click-only non détectés (ex. 7.3.x) |
| AX tree ≠ oreille | Annonces `aria-live`, messages de statut, contenu masqué |
| Jugement subjectif | Pertinence d'une alternative, image porteuse d'info, couleur informative |

**Enseignement** : sur les tests clavier/focus, l'agent peut être correct ~80 % du temps mais **sous-estime** les problèmes de focus visible et de contrôlabilité réelle. Le complément humain sur 7.3.x est donc à traiter en priorité interactive, pas en auto-confirm.

## Trois tiers de complément

Classer chaque test `human_complement_required` avant de choisir le mode de traitement :

| Tier | Critères de détection | Mode recommandé |
| ---- | --------------------- | --------------- |
| **AT** | `AT_ONLY_TEST_IDS` dans `config.py`, `agent_scope: at_only`, ou `human_steps` mentionnant la restitution AT | Humain avec VoiceOver/NVDA (cf. [test-environment.md](test-environment.md)) |
| **Jugement** | Thématique images (critère `1.x`), critères `3.1` / `4.2`, test `7.1.3` (nom/rôle « pertinent ») | Humain ; requalification si besoin |
| **Auto-confirmable** | Tout le reste (structure DOM, clavier structurel déjà vérifié, skip links, listes, rôles ARIA…) | `auto-confirm-human.py` ou confirmation humaine légère |

### Tests auto-confirmables typiques

- `7.4.1`, `8.9.x`, `9.3.x`, `10.7.1`, `11.2.5`, `11.9.x`, `12.7.x`, `7.5.1` (présence rôles ARIA)
- **Exclus** de l'auto-confirm : `7.3.x` (clavier/focus réel validé interactivement)

## Événements `audit-log.jsonl`

### `test_result` (phase 2 — agent)

```json
{
  "event": "test_result",
  "sample": "{slug}",
  "sample_url": "{url}",
  "criterion": "7.3",
  "test": "7.3.1",
  "agent_scope": "full",
  "agent_result": "pass",
  "human_complement_required": true,
  "evidence": "…",
  "mcp_tools_used": ["browser_navigate", "browser_cdp", "browser_press_key"],
  "timestamp": "…"
}
```

### `human_complement` (phase 4 — humain ou auto)

```json
{
  "event": "human_complement",
  "sample": "{slug}",
  "sample_url": "{url}",
  "criterion": "7.3",
  "test": "7.3.1",
  "human_result": "pass",
  "agent_result": "pass",
  "comment": "Tab atteint tous les contrôles ; pas de click-only",
  "source": "interactive_keyboard",
  "timestamp": "…"
}
```

| Champ `source` | Signification |
| -------------- | ------------- |
| `interactive_keyboard` | Validation humaine pas à pas (clavier / AT) |
| `interactive_at` | Validation lecteur d'écran |
| `auto_confirmed_agent` | Reprise du résultat agent (politique hors AT/jugement) |

**Règle d'agrégation** : `human_complement.human_result` **écrase** `test_result.agent_result` pour le même triplet `(criterion, sample, test)` — voir [scoring.md](scoring.md).

### NA agent — pas de complément

Si l'agent a noté `na`, **ne pas** demander de complément humain sur ce test pour cet échantillon.

## Workflow interactif (AskQuestion)

Pour les tests à **forte valeur** (7.3.x, NC agent, AT, jugement), mener l'utilisateur **critère par critère**, une combinaison test × page à la fois.

### Format obligatoire

Chaque question doit inclure le **contexte complet** :
- numéro d'étape / total
- critère et test (`7.3.1`)
- identifiant de page (`slug` ou URL)
- résultat agent et preuve courte

**Titre AskQuestion** (exemple) :
```
Étape 3/24 · Critère 7.3.1 · Page {slug}
```

**Corps** : tableau ou liste avec critère, test, URL, résultat agent, points d'attention (accordéons, formulaires, médias…).

### Questions types — 7.3.1 (contrôlabilité)

1. Tab atteint-il menu et tous les contrôles interactifs ?
2. Le lien d'évitement fonctionne-t-il au clavier ?
3. Les composants repliables s'ouvrent/ferment avec Entrée ou Espace ?
4. Existe-t-il un élément souris sans équivalent clavier ?

### Questions types — 7.3.2 (focus)

1. Le focus est-il clairement visible à chaque Tab ?
2. Le focus disparaît-il tout seul ?
3. Le focus saute-t-il de façon imprévisible après une interaction ?

Adapter les questions au type de page (formulaire, liste paginée, assistant multi-étapes, FAQ accordéon…).

## Auto-confirmation en lot

Script : `scripts/audit/auto-confirm-human.py`

```bash
# Simulation
python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/ --dry-run

# Exécution + régénération grille
python3 scripts/audit/auto-confirm-human.py audits/{site}/{date}/
```

**Politique par défaut** (`all_except_at_judgment`) :
- Confirme automatiquement (`human_result` = `agent_result`) les tests **non AT** et **non jugement**
- Ignore les `na` et les entrées `human_complement` déjà présentes
- Régénère `grid.csv` via `aggregate-grid.py`

**Quand l'utiliser** : après validation que les tests structurels auto-confirmables n'exigent pas de spot-check AT. **Ne pas** l'appliquer à `7.3.x` ni aux tests AT/jugement.

## Réduction du volume humain

Le nombre brut de combinaisons `human_complement_required` × échantillons est souvent **trompeur** (plusieurs centaines). Stratégies :

| Stratégie | Effet |
| --------- | ----- |
| Exclure les `na` agent | −30 à 60 % |
| Auto-confirm hors AT/jugement | −50 % du reste |
| Échantillonnage par type de page | Composants communs (header, footer, skip link) testés une fois |
| Cibler les NC agent | Humain prioritaire sur `fail` agent |
| Spot-check AT | 2–3 pages représentatives au lieu de toutes |

Ordre recommandé :
1. Complément **interactif** sur 7.3.x (toutes les pages applicables)
2. **Auto-confirm** le reste structurel
3. Humain sur **AT + jugement** restants
4. `aggregate-grid.py` → rapport final

## Pages inaccessibles en HTTP direct

Si une URL renvoie **500** ou un état non auditable, **stopper** et demander à l'humain la **procédure** pour atteindre l'état (navigation préalable, formulaire, paramètres). Consigner dans `samples-status.json` :

```json
{
  "slug": "{slug}",
  "url": "{url}",
  "status": "ok",
  "notes": "Accès direct impossible — procédure requise",
  "human_procedure": "1. Naviguer vers …\n2. Remplir …\n3. Soumettre → URL cible"
}
```

L'agent rejoue la procédure sur le même onglet MCP avant d'auditer.

## Mise à jour après compléments

```bash
# Après chaque lot de human_complement (manuel ou auto)
python3 scripts/audit/aggregate-grid.py audits/{site}/{date}/
```

Puis générer `report.md` uniquement quand :
- tous les compléments **AT** et **jugement** sont renseignés, **ou**
- l'utilisateur accepte un **audit partiel** documenté

## Format de réponse utilisateur (texte libre)

```
{critère} | {url} | {test_id} | C|NC|NA | {commentaire}
```

L'agent convertit en entrée `human_complement` avec `human_result` : `pass` / `fail` / `na`.
