# Registre des risques — audit RGAA

> Seuls les risques **v1** ont un comportement défini dans `SKILL.md`. Les autres sont documentés pour évolution.

## Phase 0 — Initialisation

| Risque | v1 | Action |
| ------ | -- | ------ |
| `rgaa-rules.json` absent | oui | Exécuter `python3 scripts/extract-rules.py` |
| Échantillons non représentatifs | oui | Rappeler le kit d'audit ; accepter si l'utilisateur confirme |
| Périmètre desktop/mobile flou | oui | Question bloquante |
| Credentials en clair | oui | Avertir ; ne pas committer ; recommander saisie locale |

## Phase 1 — Validation des échantillons

| Risque | v1 | Action |
| ------ | -- | ------ |
| **404** | oui | Demander URL de remplacement (même type) |
| **401 / 403** | oui | Flux auth : page login + credentials + connexion même onglet |
| **500 / 502 / 503** | oui | **Stop** ; **demander procédure humaine** (pas de contournement) ; attendre réponse |
| Redirection vers login | oui | Flux auth |
| Timeout | oui | 1 retry puis escalade |
| Bandeau cookies / modale | oui | Fermer si repéré au snapshot |
| CAPTCHA / anti-bot | oui | Stop ; intervention humaine |
| SPA DOM vide | oui | Attendre chargement avant validation |
| Géo-restriction / VPN | non | Documenter ; demander accès réseau |
| Iframe cross-origin | oui | NT sur critères concernés |

## Flux d'authentification (v1)

1. Stop sur échantillon bloqué
2. Demander URL page login + identifiants
3. `browser_navigate` vers login sur **le même onglet**
4. `browser_fill` + `browser_click` ; vérifier succès
5. Reprendre validation puis audit sur **le même onglet**
6. **Interdit** : `browser_tabs` new / fermer l'onglet

**Hors v1** : 2FA, SSO externe (Google/Microsoft), magic link

## Phase 2 — Tests

| Risque | v1 | Action |
| ------ | -- | ------ |
| Contexte saturé | oui | `audit-log.jsonl` incrémental ; 1 critère à la fois |
| Jugement subjectif | oui | NT + question ciblée |
| Tests AT (NVDA, etc.) | oui | NT systématique |
| Contraste fond image | oui | NT si incertain |
| Lazy-load / scroll | oui | Scroll + attente avant tests |
| Shadow DOM | oui | CDP `Runtime.evaluate` ; sinon NT |
| États JS non atteints | oui | Activer avant test si méthodologie l'impose |
| Session expirée | oui | Détecter login ; reconnexion même onglet ; checkpoint |
| Utilisation Playwright / autre MCP | oui | **Interdit** — `cursor-ide-browser` seul |
| Omettre CDP (AX, contrastes) | oui | **Interdit** — voir chromium-cdp-tools.md |
| NT par défaut sans test MCP | oui | **Interdit** — tests `full` = C/NC/NA obligatoires |
| Nouvel onglet par erreur | oui | Revenir à l'onglet de session |
| MCP crash | oui | Reprendre depuis `audit-log.jsonl` |
| Parcours multi-étapes | oui | 1 URL = 1 état ; signaler si incomplet |

## Phase 3 — Notation

| Risque | v1 | Action |
| ------ | -- | ------ |
| NA abusif | oui | Justification + preuve obligatoires |
| Agrégation site incorrecte | oui | NC si NC sur ≥1 échantillon applicable |
| C avec NT restant | oui | Interdit |

## Phase 4 — Relais humain

| Risque | v1 | Action |
| ------ | -- | ------ |
| Liste NT trop longue | oui | Grouper par thématique |
| Réponse incomplète | oui | Pas de reporting final |
| Contradiction humain/agent | oui | Documenter les deux |

## Phase 5 — Reporting

| Risque | v1 | Action |
| ------ | -- | ------ |
| Audit présenté complet avec NT | oui | Mention « audit partiel » obligatoire |
| CSV / MD désynchronisés | oui | Même source de vérité |
| Preuves non reliées | oui | Lien par NC dans report.md |

## Transverse

| Risque | v1 | Action |
| ------ | -- | ------ |
| `rules.html` mis à jour | oui | Re-run extract ; valider 106/258 |
| Environnement ≠ production | oui | Documenter dans rapport |
