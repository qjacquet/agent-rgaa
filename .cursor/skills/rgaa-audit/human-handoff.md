# Gabarit — Relais humain (NT)

Générer `nt-handoff.md` dans le dossier d'audit quand des tests restent en **NT**.

Pour les tests `human_complement_required` (agent a déjà noté C/NC/NA), voir **[human-complement.md](human-complement.md)** — workflow distinct du NT pur.

## Template

```markdown
# Points non testés — audit humain requis

**Site** : {site_url}
**Date** : {date}
**Échantillons** : {liste_urls}

## Synthèse

- NT total : {count}
- Par thématique : {tableau}

## Détail par critère

### {criterion_id} — {criterion_title}

**Échantillon** : {sample_url}
**Statut actuel** : NT

**Tests concernés** :

| Test | Méthodologie restante | Preuves agent | Question pour l'humain |
| ---- | --------------------- | ------------- | ---------------------- |
| {test_id} | {steps_non_realisables} | {lien_capture / extrait} | {question_precise} |

**Résultat humain attendu** (à remplir) :
- [ ] C — {commentaire}
- [ ] NC — {commentaire + localisation}
- [ ] NA — {justification}

---

(répéter pour chaque NT)
```

## Format de réponse attendu de l'utilisateur

```
{criterion_id} | {sample_url} | {test_id} | {C|NC|NA} | {commentaire}
```

Exemple :
```
7.3 | https://exemple.fr/compte | 7.3.1 | C | Tab atteint tous les contrôles, Entrée active les boutons
1.1 | https://exemple.fr/accueil | 1.1.1 | NC | Logo header : alternative non pertinente
```

L'agent enregistre en `human_complement` dans `audit-log.jsonl` puis relance `aggregate-grid.py`.

## Règles

1. Grouper les NT par thématique pour faciliter la reprise.
2. Chaque NT doit avoir une **question précise**, pas une demande vague.
3. Pour les NT **restitution AT**, indiquer la combinaison attendue (ex. « VoiceOver + Safari » ou « NVDA + Firefox ») — voir [test-environment.md](test-environment.md).
4. Ne pas passer en phase 5 (reporting final) tant que les NT critiques ne sont pas résolus ou explicitement acceptés comme « audit partiel » par l'utilisateur.
