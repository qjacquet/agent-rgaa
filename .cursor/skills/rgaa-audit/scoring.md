# Notation RGAA — C / NC / NA / NT

## Niveau test

Chaque test d'un critère reçoit un statut interne :

| Statut interne | Signification |
| -------------- | ------------- |
| `pass` | Méthodologie appliquée, test validé |
| `fail` | Méthodologie appliquée, test en échec |
| `na` | Test non applicable sur cet échantillon |
| `nt` | Test non réalisable ou ambigu |

## Niveau critère (par échantillon)

| Statut | Règle |
| ------ | ----- |
| **C** (Conforme) | Tous les tests applicables sont `pass` |
| **NC** (Non conforme) | Au moins un test applicable est `fail` |
| **NA** (Non applicable) | Tous les tests sont `na`, avec justification documentée |
| **NT** (Non testé) | Au moins un test est `nt`, aucun `fail` |

**Interdit** : noter **C** si un test applicable est encore `nt`.

## Niveau site (agrégation)

Un critère est **NC au niveau site** s'il est **NC sur au moins un échantillon** où il est applicable (statut ≠ NA).

Un critère est **C au niveau site** s'il est **C ou NA** sur tous les échantillons et **C** sur au moins un échantillon où il était applicable.

Un critère est **NA au niveau site** s'il est **NA sur tous les échantillons**.

Un critère est **NT au niveau site** s'il reste au moins un **NT** non résolu et aucun **NC**.

## Règles pour NA

Le NA exige :
1. Une **justification** explicite (ex. « aucune image sur la page »)
2. Une **preuve** : constat DOM, capture, ou entrée `audit-log.jsonl`

Ne pas utiliser NA pour éviter un test difficile.

## Règles pour NT

| Situation | Statut test | Statut critère (provisoire) |
| --------- | ----------- | --------------------------- |
| `agent_scope: full`, agent conclut | C / NC / NA | Agrégé depuis tests |
| `agent_scope: full` + `human_complement_required` (ex. 7.3) | C / NC / NA agent + complément dans pré-rapport | C / NC agent ; mention « à confirmer » dans pré-rapport |
| `agent_scope: partial`, `human_steps` restantes | NT ou C/NC partiel + NT | **NT** jusqu'à humain |
| `agent_scope: at_only` | **NT** | **NT** |

Ne pas marquer **NC** sur une hypothèse non vérifiée — préférer **NT**.

## Pré-rapport : rubriques obligatoires

Pour tout test listé dans le pré-rapport, documenter :
- **Pour noter C** : conditions de succès (depuis `success_criterion` du JSON)
- **Cas NC** : conditions d'échec (depuis `failure_criterion` du JSON)

## Priorité en cas de conflit

`fail` > `nt` > `pass` > `na` pour déterminer le statut critère.

## Compléments humains (`human_complement`)

Phase 4 : entrées `event: "human_complement"` dans `audit-log.jsonl`.

| Champ | Valeurs | Rôle |
| ----- | ------- | ---- |
| `human_result` | `pass` \| `fail` \| `na` | Résultat final après complément |
| `source` | `interactive_keyboard` \| `interactive_at` \| `auto_confirmed_agent` | Traçabilité |
| `comment` | texte libre | Justification (focus invisible, click-only, etc.) |

**Agrégation** (`aggregate-grid.py`) : pour chaque triplet `(criterion, sample, test)`, la **dernière** valeur l'emporte — `human_complement` écrase `test_result.agent_result`.

**NA agent** : pas de `human_complement` attendu.

### Politique zéro NT (phase 2)

Sur `agent_scope: full`, l'agent note **pass/fail/na** — pas NT par défaut. Le complément humain **confirme ou infirme**, il ne comble pas un NT évité.

### Auto-confirmation

`scripts/audit/auto-confirm-human.py` écrit des `human_complement` avec `human_result` = `agent_result` pour les tests hors tiers **AT** et **jugement** (cf. [human-complement.md](human-complement.md)).

**Exclure** de l'auto-confirm : `7.3.x` (validation clavier interactive obligatoire).
