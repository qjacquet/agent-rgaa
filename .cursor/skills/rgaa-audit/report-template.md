# Gabarit — Rapport d'audit RGAA

## Structure `report.md`

```markdown
# Rapport d'audit RGAA 4.1.2 — {site_name}

## 1. Contexte

| Élément | Valeur |
| ------- | ------ |
| Site audité | {base_url} |
| Date | {date} |
| Référentiel | RGAA 4.1.2 |
| Auditeur agent | Cursor (skill rgaa-audit) |
| Compléments humains | {oui/non — détail} |
| Environnement | {desktop / mobile} |
| Périmètre | {nombre échantillons} pages |
| Statut global | {complet / partiel — NT restants} |

### Échantillons

| # | URL | Type de page | Statut validation |
| - | --- | ------------ | ----------------- |
| 1 | {url} | {type} | ok |

### Limites de l'audit

- **Technologies d'assistance** : non testées par l'agent (VoiceOver, NVDA, JAWS, TalkBack). Tests de restitution → NT, complétés par un humain selon [environnement de test RGAA](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/) — combinaison utilisée : {ex. VoiceOver + Safari}
- {autres limites : auth, préprod, etc.}

## 2. Synthèse

### Par thématique

| Thématique | C | NC | NA | NT |
| ---------- | - | -- | -- | -- |
| 1. Images | | | | |

### Score global (hors NA)

- Conformité : {X}% ({nb_C} C sur {nb_applicables} critères applicables)
- Non conformités : {nb_NC}
- Non testés : {nb_NT}

## 3. Non-conformités (NC)

### {criterion_id} — {title}

- **Échantillon** : {url}
- **Test en échec** : {test_id} — {test_title}
- **Méthodologie appliquée** : {résumé étapes}
- **Constat** : {description}
- **Preuve** : {screenshot_path ou sélecteur}
- **Recommandation** : {action corrective}

(répéter)

## 4. Non testés (NT)

| Critère | Échantillon | Raison | Résolution |
| ------- | ----------- | ------ | ---------- |
| {id} | {url} | {raison} | {humain / en attente} |

## 5. Méthodologie

- Référentiel : `data/rgaa-rules.json` extrait de `rules.html`
- Outils : `cursor-ide-browser` uniquement (voir tools-mapping.md)
- [Méthodologie de test RGAA](https://accessibilite.numerique.gouv.fr/ressources/methodologie-de-test/)
- [Environnement de test](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/)
```

## Structure `grid.csv`

```csv
theme_id,theme_title,criterion_id,criterion_title,wcag_level,{sample_slug_1},{sample_slug_2},...,site_status,notes
1,Images,1.1,"Chaque image porteuse d'information...",A,C,NC,...,NC,"Test 1.1.1 fail sur accueil"
```

**Règle** : générer CSV et Markdown à partir de la même source (`audit-log.jsonl` + grille consolidée) pour éviter les désynchronisations.
