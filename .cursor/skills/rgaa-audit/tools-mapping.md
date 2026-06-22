# Outils MCP — équivalents à la méthodologie de test RGAA

Référence : [Méthodologie de test RGAA](https://accessibilite.numerique.gouv.fr/ressources/methodologie-de-test/)

> **Document principal** : [chromium-cdp-tools.md](chromium-cdp-tools.md) — liste complète, vérification, suite obligatoire.

> **MCP unique** : `cursor-ide-browser` **uniquement**. Ne pas utiliser `user-playwright` ni autre MCP navigateur.

> **Extensions Chrome** : **non disponibles** dans le navigateur Cursor. Utiliser les substituts CDP — **obligatoire**, pas optionnel.

> **VoiceOver, NVDA, JAWS, TalkBack** : l'agent **ne les utilise pas**. Voir [test-environment.md](test-environment.md).

## MCP `cursor-ide-browser` (seul autorisé)

| Besoin | Commande | Obligatoire phase 2 |
| ------ | -------- | ------------------- |
| Navigation, session | `browser_navigate`, `browser_tabs` (list uniquement) | ✅ |
| Interaction | `browser_click`, `browser_fill`, `browser_type`, `browser_press_key`, `browser_select_option`, `browser_scroll` | Si méthodologie |
| Structure page | `browser_snapshot` | ✅ par échantillon |
| Capture | `browser_take_screenshot` | Si NC |
| Arbre d'accessibilité | `browser_cdp` → `Accessibility.getFullAXTree` | ✅ par échantillon |
| DOM, styles, JS | `browser_cdp` → `DOM.querySelector`, `CSS.getComputedStyleForNode`, `Runtime.evaluate` | ✅ par échantillon |
| Attente chargement | Boucle snapshot / CDP | ✅ |

## Substituts par outil RGAA (plugins Chromium → CDP)

| Outil RGAA (extension / plugin) | Substitut agent MCP | Script | Limite |
| ------------------------------- | ------------------- | ------ | ------ |
| Inspecteur navigateur | `browser_snapshot` + `DOM.*` | — | — |
| Arbre d'accessibilité | `Accessibility.getFullAXTree` | — | Pas restitution sonore |
| Web Developer Toolbar | `Runtime.evaluate` | `scripts/cdp/query-dom.js` | — |
| **WAVE** | Scan programmatique DOM | `scripts/cdp/query-dom.js` | Pas overlay visuel |
| **HeadingsMap** | `h1–h6` + sauts | `scripts/cdp/query-dom.js` | — |
| **WCAG Contrast Checker** | Luminance JS + `CSS.getComputedStyleForNode` | `scripts/cdp/contrast-scan.js` | Fond image → NT |
| Validateur W3C | `Runtime.evaluate` → `outerHTML` / doctype | inline | Optionnel |
| Navigation clavier | `browser_press_key` | — | 7.3 : complément humain possible |
| NVDA / VoiceOver / JAWS | **Humain** phase 4 | — | NT si AT requis |

## Snippets via `browser_cdp` (`Runtime.evaluate`)

Voir `scripts/cdp/query-dom.js` et `scripts/cdp/contrast-scan.js`.

### Hiérarchie des titres (HeadingsMap)

```javascript
() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({tag: h.tagName, text: h.innerText.trim().slice(0,80), level: +h.tagName[1]}))
```

### Images et alternatives (WAVE)

```javascript
() => [...document.querySelectorAll('img,[role="img"]')].map(el => ({
  tag: el.tagName, alt: el.getAttribute('alt'), ariaLabel: el.getAttribute('aria-label'),
  ariaLabelledby: el.getAttribute('aria-labelledby'), title: el.getAttribute('title'), src: el.src?.slice(0,60)
}))
```

## Environnement de test

Voir [test-environment.md](test-environment.md) et [Environnement de test RGAA](https://accessibilite.numerique.gouv.fr/methode/environnement-de-test/).
