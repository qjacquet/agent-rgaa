# Environnement de test — agent vs humain

Référence officielle : [Environnement de test RGAA](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/)

## Ce que l'agent ne fait PAS

L'agent **n'utilise pas** et **ne peut pas utiliser** :

- VoiceOver (macOS / iOS)
- NVDA ou JAWS (Windows)
- TalkBack (Android)
- ZoomText, Dragon Naturally Speaking

Un navigateur MCP (Cursor, Playwright) **n'exécute pas** de lecteur d'écran. L'arbre d'accessibilité exposé via CDP (`Accessibility.getFullAXTree`) est une **représentation technique** de ce que le navigateur expose aux AT — ce n'est **pas** une restitution sonore, pas un parcours utilisateur réel au clavier + oreille.

**Ne jamais prétendre** qu'un test de restitution AT est validé sur la seule base de l'AX tree.

## Répartition des responsabilités

| Type de vérification | Qui | Outil |
| -------------------- | --- | ----- |
| Code HTML, attributs, structure DOM | Agent | `browser_cdp`, `browser_evaluate`, `browser_snapshot` |
| Arbre d'accessibilité (noms, rôles, états exposés) | Agent | `Accessibility.getFullAXTree` |
| Navigation clavier simulée (Tab, Enter, focus visible partiel) | Agent | `browser_press_key`, CDP |
| Contraste couleurs (cas simples) | Agent | `CSS.getComputedStyleForNode` |
| **Restitution par technologies d'assistance** | **Humain** | NVDA, JAWS, VoiceOver, TalkBack… |
| **Compatibilité fonctionnelle AT** (scripts, ARIA live, changements de contexte annoncés) | **Humain** | Combinaisons RGAA ci-dessous |
| Jugements subjectifs (image porteuse d'info, pertinence d'alternative) | **Humain** (ou NT) | — |

## Tests concernés par les AT (exemples)

Marquer **NT** dès que la méthodologie mentionne :

- « correctement restitué par les technologies d'assistance »
- « compatible avec les technologies d'assistance »
- « lecteur d'écran »
- messages de statut ARIA (`aria-live`, `role="status"`, `role="alert"`)
- thématiques **JavaScript** (7.x), **Médias** (4.13), parties de **Images** (1.3, 1.6), **Tableaux** / **Formulaires** selon cas

L'agent peut faire une **pré-analyse technique** (présence des attributs, rôles, propriétés ARIA) puis noter **NT** pour la restitution réelle.

## Combinaisons officielles — pour l'auditeur humain (phase 4)

L'humain doit tester sur **au moins une** des combinaisons ci-dessous pour valider les NT de restitution.

### Desktop (environnement non maîtrisé)

**Combinaison 1** — au moins une ligne suffit :

| Technologie d'assistance | Navigateur |
| ------------------------ | ---------- |
| NVDA (dernière version FR) | Firefox |
| JAWS (version précédente) | Firefox ou Internet Explorer |
| VoiceOver (dernière version) | Safari |

**Combinaison 2** — alternative :

| Technologie d'assistance | Navigateur |
| ------------------------ | ---------- |
| JAWS (version précédente) | Firefox |
| NVDA (dernière version) | Firefox ou Internet Explorer |
| VoiceOver (dernière version) | Safari |

### Mobile

**Combinaison 1** :

| OS | AT | Navigateur |
| -- | -- | ---------- |
| Android | TalkBack (dernière version FR) | Chrome |

**Combinaison 2** :

| OS | AT | Navigateur |
| -- | -- | ---------- |
| iOS | VoiceOver (dernière version) | Safari |

Site mobile grand public : **fortement conseillé** de tester les deux.

### Environnement maîtrisé

Si le site est diffusé dans un environnement maîtrisé (intranet, postes standardisés, GNU/Linux interne…), l'humain utilise les **configurations réellement déployées** chez les utilisateurs — elles **remplacent** les combinaisons ci-dessus.

## Phase 0 — questions à poser

1. **Périmètre** : desktop / mobile / les deux ?
2. **Environnement maîtrisé** : oui / non ? Si oui, quelles combinaisons AT + navigateur + OS ?
3. **Qui réalise les tests AT** : l'utilisateur, un auditeur dédié, ou audit partiel accepté ?

Consigner dans `report.md` :

- Combinaison AT prévue pour la phase humaine
- Tests restés NT faute d'audit AT

## Ce que l'agent fait à la place (limites assumées)

| Besoin RGAA | Substitut agent | Suffisant pour noter C ? |
| ----------- | --------------- | ------------------------ |
| Présence `alt`, `aria-label`, `aria-labelledby` | DOM / AX tree | Oui pour tests **présence** d'alternative |
| Restitution de l'alternative | AX tree (nom accessible) | **Non** → NT si méthodologie exige restitution AT |
| `aria-hidden`, `role="presentation"` | AX tree + DOM | Oui si critère = code uniquement |
| Ignoré par les AT (décoration) | AX tree (`ignored: true`) | Partiel — NT si doute |
| Focus clavier | `browser_press_key` | Partiel — NT si restitution focus requise |
| Annonce changement de contexte | — | **Non** → NT, humain avec VoiceOver/NVDA |

## Tests exclus de la passe agent (`agent_scope`)

Le JSON classe chaque test :

| Scope | Exemple | Agent | Humain (pré-rapport) |
| ----- | ------- | ----- | -------------------- |
| `full` | 1.2.1, 7.3.1 | C / NC / NA | Complément si `human_complement_required` |
| `partial` | 7.1.2 | C / NC sur `agent_steps` | `human_steps` AT + **Pour C / Cas NC** |
| `at_only` | (rare) | NT + pré-analyse | Procédure complète |

~55 tests ont `human_complement_required` (dont **7.3.x**). L'agent **note C/NC** sur 7.3 ; le pré-rapport indique comment **confirmer C** ou **requalifier en NC**.

## Formulation dans `pre-report.md` et `nt-handoff.md`

Pour chaque NT AT, préciser :

```markdown
**Test AT requis** : restitution VoiceOver + Safari (ou NVDA + Firefox selon environnement choisi)
**Pré-analyse agent** : {ce qui a été vérifié techniquement}
**À vérifier humainement** : {étapes de la méthodologie restantes}
```
