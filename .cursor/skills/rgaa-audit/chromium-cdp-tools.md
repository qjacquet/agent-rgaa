# Outils RGAA → CDP Chromium (cursor-ide-browser)

> **Important** : le MCP `cursor-ide-browser` **n’installe pas** d’extensions Chrome (WAVE, HeadingsMap, Web Developer, etc.).  
> Les « plugins » de la méthodologie RGAA sont des **substituts CDP obligatoires** listés ci-dessous.

Vérification effectuée le **2026-06-22** sur https://www.cmvmediforce.fr/ (onglet Cursor `05947d`).

## Extensions Chrome — indisponibles

| Extension / outil RGAA classique | Chargement extension MCP | Statut |
| -------------------------------- | ------------------------ | ------ |
| WAVE Evaluation Tool | `Extensions.loadUnpacked` | **Refusé / indisponible** |
| HeadingsMap | idem | **Indisponible** |
| Web Developer Toolbar | idem | **Indisponible** |
| Colour Contrast Analyser (extension) | idem | **Indisponible** |
| Validateur HTML W3C (extension) | idem | **Indisponible** |

**Règle** : ne jamais marquer NT au motif « extension absente ». Utiliser le substitut CDP documenté.

## Substituts CDP — vérifiés opérationnels

| Outil RGAA | Substitut MCP / CDP | Méthode | Vérifié | Notes |
| ---------- | ------------------- | ------- | ------- | ----- |
| Inspecteur / DOM | `browser_snapshot` | snapshot YAML | ✅ | Arbre interactif + rôles |
| Inspecteur / DOM | `browser_cdp` | `DOM.getDocument`, `DOM.querySelector` | ✅ | `nodeId` pour styles |
| Arbre d'accessibilité | `browser_cdp` | `Accessibility.enable` + `Accessibility.getFullAXTree` | ✅ | ~570 Ko / page — sauver en fichier si trop gros |
| JavaScript / Web Dev Toolbar | `browser_cdp` | `Runtime.evaluate` | ✅ | Collectes custom (headings, liens, formulaires…) |
| HeadingsMap | `Runtime.evaluate` | `h1–h6` + sauts hiérarchie | ✅ | Voir `scripts/page-audit-collect.js` |
| WAVE (scan erreurs) | `Runtime.evaluate` | images sans alt, liens vides, champs sans label | ✅ | Scan programmatique, pas overlay visuel |
| WCAG Contrast Checker | `Runtime.evaluate` | calcul ratio Luminance sur `getComputedStyle` | ✅ | Ex. lien « Aller au contenu » → ratio 4.35 |
| WCAG Contrast Checker | `browser_cdp` | `CSS.enable` + `CSS.getComputedStyleForNode` | ✅ | Nécessite `nodeId` via `DOM.querySelector` ; pas sur `#document` seul |
| Navigation clavier | `browser_press_key` | Tab, Enter, Escape, flèches | ✅ | Compléter par `browser_snapshot` après focus |
| Capture preuve | `browser_take_screenshot` | PNG | ✅ | NC / preuves |
| Focus / bounding box | `browser_highlight`, `browser_get_bounding_box` | coordonnées | ✅ | Diagnostic focus visible |

## Substituts CDP — limites connues

| Situation | Comportement | Action agent |
| --------- | ------------ | ------------ |
| Contraste sur fond image / dégradé | `backgroundColor` souvent `transparent` | Remonter ancêtres ou **NT** avec preuve |
| `CSS.getComputedStyleForNode` sur `#document` | Erreur « Node does not have an owner document » | Toujours `DOM.querySelector` → `nodeId` élément |
| Réponses CDP > 25 Ko | Sauvegarde fichier `.cursor/browser-logs/` | Lire extrait ciblé, pas tout inline |
| Restitution sonore AT | AX tree ≠ VoiceOver/NVDA | Agent : AX tree ; humain : phase 4 |
| `Input.*` CDP | Interdit (focus UI Cursor) | `browser_press_key`, `browser_click` |
| Extensions Chrome | Non chargeables | Substituts JS/CDP uniquement |

## Suite CDP obligatoire par échantillon (phase 2)

Exécuter **dans l’ordre** sur chaque URL `ok` :

```
1. browser_navigate(url)
2. browser_snapshot                    → structure + rôles
3. browser_cdp Accessibility.enable
4. browser_cdp Accessibility.getFullAXTree   → sauver extrait si gros
5. browser_cdp Runtime.evaluate(collect)     → scripts/page-audit-collect.js
6. browser_cdp Runtime.evaluate(contrast-scan) → textes + ratios (scripts/cdp-contrast-scan.js)
7. browser_press_key (Tab × N si critère 7.3 / 12.8) + snapshots
8. browser_take_screenshot si NC
```

Logger chaque étape dans `audit-log.jsonl` : `{ "event": "cdp_collect", "sample", "tools": [...] }`.

## Interdictions (causes de faux NT)

- ❌ Marquer NT sans avoir exécuté les `agent_steps` pour les tests `agent_scope: full`
- ❌ Utiliser un script Python hors navigateur (`requests`, `curl`) pour noter des critères DOM
- ❌ Remplacer la phase 2 par `score-from-collect.py` seul (10 critères) — script **agrégation uniquement** après collecte MCP complète
- ❌ Ignorer `Accessibility.getFullAXTree` et `CSS.getComputedStyleForNode`
- ❌ Utiliser `user-playwright` ou nouvel onglet

## Fichiers scripts associés

| Fichier | Rôle |
| ------- | ---- |
| `scripts/page-audit-collect.js` | Collecte DOM (headings, images, liens, forms, landmarks…) |
| `scripts/cdp-contrast-scan.js` | Scan contrastes texte (à créer / utiliser en repasse) |
| `scripts/verify-cdp-capabilities.md` | Journal de vérification MCP |
