# agent-rgaa

Skill Cursor pour auditer l'accessibilité web selon le **RGAA 4.1.2**.

## Contenu

| Fichier | Rôle |
| ------- | ---- |
| [`rules.html`](rules.html) | Référentiel source (106 critères, 258 tests) |
| [`data/rgaa-rules.json`](data/rgaa-rules.json) | Référentiel structuré pour l'agent |
| [`.cursor/skills/rgaa-audit/`](.cursor/skills/rgaa-audit/) | Skill d'audit |

## Prérequis

- Cursor avec MCP **`cursor-ide-browser` uniquement** (ne pas activer `user-playwright` pour l'audit)
- Python 3 + `beautifulsoup4` pour régénérer le JSON

```bash
python3 -m pip install -r requirements.txt
python3 scripts/extract-rules.py rules.html -o data/rgaa-rules.json
```

## Utilisation

Invoquer le skill explicitement dans Cursor :

```
/rgaa-audit
```

ou mentionner « audit RGAA » en attachant le skill.

L'agent automatise la **vérification technique** (DOM, arbre d'accessibilité via CDP, clavier simulé). Il **n'exécute pas** VoiceOver, NVDA, JAWS ni TalkBack — les tests de restitution AT sont en **NT**, complétés par un humain en phase 4. Voir [test-environment.md](.cursor/skills/rgaa-audit/test-environment.md).

Fournir obligatoirement :

- URL de base du site
- Liste d'URLs d'échantillons
- Si site protégé : URL de login + identifiants
- Qui réalisera les tests AT (VoiceOver, NVDA…) en phase 4

## Sorties d'audit

Générées dans `audits/{site-slug}/{date}/` :

- **`pre-report.md`** — pré-rapport avec NT en exergue et procédures de test humain (avant finalisation)
- `grid.csv` — grille critères × échantillons (provisoire puis finale)
- `report.md` — rapport final (après complément humain)
- `nt-handoff.md` — points nécessitant un audit humain
- `audit-log.jsonl` — trace détaillée test par test
- `samples-status.json` — statut de validation des URLs

## Références

- [Méthodologie de test RGAA](https://accessibilite.numerique.gouv.fr/ressources/methodologie-de-test/)
- [Environnement de test RGAA](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/)
- [Kit d'audit RGAA](https://accessibilite.numerique.gouv.fr/ressources/kit-d-audit/)
