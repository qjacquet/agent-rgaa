# Gabarit — Pré-rapport d'audit (`pre-report.md`)

Livrable **obligatoire** après la passe agent, **avant** le rapport final.

## Quand le générer

Générer `pre-report.md` si au moins une de ces conditions :
- un test a `human_complement_required: true` (ex. 7.3, 7.1.2)
- un test est en **NT**
- un critère **partial** a des `human_steps` non couverts

Puis **Stop** — remettre le pré-rapport à l'utilisateur.

## Trois profils de test (champ `agent_scope` dans le JSON)

| Scope | Comportement agent | Notation agent | Pré-rapport |
| ----- | ------------------ | -------------- | ----------- |
| `full` | Exécute toutes les `agent_steps` | **C / NC / NA** | Complément humain si `human_complement_required` (ex. 7.3) |
| `partial` | Exécute `agent_steps` uniquement | **C / NC / NA** sur la partie automatisée ; test **NT** tant que `human_steps` non faites | Section obligatoire avec étapes humaines + rubrique C/NC |
| `at_only` | Pré-analyse DOM/AX seulement | **NT** (pas de C/NC agent) | Procédure humaine complète |

## Bloc standard par test (à répéter)

Chaque entrée du pré-rapport **doit** contenir :

```markdown
#### {test_id} — {test_title}

**Échantillon** : [{url}]({url})
**Scope** : {full|partial|at_only} | Complément humain : {oui|non}

**Résultat agent** : **{C|NC|NA|NT}**
{résumé une ligne + preuve}

**Étapes réalisées par l'agent** :
1. {agent_steps exécutées et constat}

**Pour noter C** :
- {reformuler `success_criterion` du JSON + étapes `human_steps` si partial}
- {étapes concrètes : ex. Tab atteint le bouton, Entrée active l'action, VoiceOver annonce…}

**Cas NC** :
- {reformuler `failure_criterion` + conditions d'échec explicites}
- {ex. : élément click-only sans équivalent clavier ; focus supprimé après réception ; message non annoncé}

**Combinaison AT** (si `human_steps` ou restitution) : {NVDA+Firefox | VoiceOver+Safari | TalkBack+Chrome}

**Résultat humain** (à remplir) :
- [ ] **C** — Commentaire :
- [ ] **NC** — Élément + commentaire :
- [ ] **NA** — Justification :
- [ ] **Confirme l'agent** / **Infirme l'agent** (si complément sur test déjà noté C/NC)
```

## Template complet `pre-report.md`

```markdown
# Pré-rapport d'audit RGAA 4.1.2 — {site_name}

> **Audit non finalisé** — validations humaines listées ci-dessous avant rapport final.

## 1. Synthèse passe agent

| Indicateur | Valeur |
| ---------- | ------ |
| Critères C (agent) | {n} |
| Critères NC (agent) | {n} |
| Critères NA | {n} |
| Tests NT (inachevés) | {n} |
| Compléments humains à réaliser | {n_human_complement} |

## 2. NC agent — corrections prioritaires

| Critère | Échantillon | Test | Constat | Preuve |
| ------- | ----------- | ---- | ------- | ------ |

## 3. Compléments et validations humaines

> Tests où l'agent a noté **C / NC / NA** mais un contrôle humain est requis (ex. **7.3** clavier/pointage réel), **ou** où seules les étapes automatisées sont faites (**partial**).

{blocs standard — un par test `human_complement_required` ou partial}

### Exemple 7.3.1 (agent a noté C — complément clavier/pointage)

**Résultat agent** : **C** — Tous les éléments avec gestionnaire d'événement atteints au Tab ; Entrée active les actions simples.

**Pour noter C** (confirmation humaine) :
- Parcourir chaque contrôle interactif identifié par l'agent au clavier réel
- Vérifier qu'aucune action n'est réservée au seul clic souris sans équivalent clavier
- Vérifier l'usage au doigt/stylet sur mobile si périmètre mobile

**Cas NC** :
- Un élément réagit au clic mais n'est pas atteignable ou actionnable au clavier
- Aucun substitut clavier pour une action scriptée
- Élément inaccessible au pointage sans alternative

## 4. Tests NT — non conclus par l'agent

{blocs standard — tests restés NT, souvent `human_steps` AT non réalisables par MCP}

## 5. Grille provisoire

Voir [grid.csv](./grid.csv).

## 6. Prochaines étapes

Répondre : `{critère} | {url} | {test_id} | C|NC|NA | commentaire`
```

## Règles

1. **Toujours** renseigner **Pour noter C** et **Cas NC** — jamais une procédure sans critères de décision.
2. Utiliser `success_criterion` et `failure_criterion` du JSON quand présents.
3. Pour `partial`, lister séparément ce que l'agent a fait et ce que l'humain doit encore faire (`human_steps`).
4. Si l'agent a noté **NC**, le complément humain confirme ou infirme — le cas NC est déjà actionnable côté dev.
5. Si l'agent a noté **C** sur 7.3, le complément humain est une **confirmation** ; documenter ce qui invaliderait le C.
