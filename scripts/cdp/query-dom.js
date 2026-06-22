/**
 * Helpers CDP — appelés PENDANT l'exécution d'un test MCP, pas en collecte bulk.
 * Usage: browser_cdp → Runtime.evaluate(readFile('query-dom.js'))
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const accName = (el) => {
    const lb = el.getAttribute('aria-labelledby');
    if (lb) {
      const t = lb.split(/\s+/).map(id => document.getElementById(id)).filter(Boolean).map(textOf).join(' ');
      if (t) return t;
    }
    return el.getAttribute('aria-label') || el.getAttribute('alt') || el.getAttribute('title') || textOf(el).slice(0, 80);
  };

  return {
    url: location.href,
    title: document.title,
    lang: document.documentElement.lang || '',
    doctype: document.doctype?.name || null,
    charset: document.characterSet,
    viewport: document.querySelector('meta[name=viewport]')?.content || null,
    stylesheetCount: document.styleSheets.length,
    images: [...document.querySelectorAll('img,[role=img]')].filter(visible).map(el => ({
      tag: el.tagName, alt: el.getAttribute('alt'), ariaLabel: el.getAttribute('aria-label'),
      ariaLabelledby: el.getAttribute('aria-labelledby'), title: el.getAttribute('title'),
      src: (el.src || '').slice(-80),
    })),
    areas: [...document.querySelectorAll('area')].map(a => ({ alt: a.getAttribute('alt'), ariaLabel: a.getAttribute('aria-label') })),
    inputImages: [...document.querySelectorAll('input[type=image]')].map(i => ({ alt: i.getAttribute('alt'), ariaLabel: i.getAttribute('aria-label') })),
    svgs: [...document.querySelectorAll('svg')].filter(visible).map(s => ({ role: s.getAttribute('role'), ariaLabel: s.getAttribute('aria-label') })),
    links: [...document.querySelectorAll('a[href]')].filter(visible).map(a => ({
      text: textOf(a).slice(0, 80), href: a.href.slice(0, 120),
      ariaLabel: a.getAttribute('aria-label'), title: a.getAttribute('title'),
      target: a.getAttribute('target'),
    })),
    iframes: [...document.querySelectorAll('iframe')].filter(visible).map(f => ({ title: f.getAttribute('title'), src: (f.src || '').slice(0, 80) })),
    headings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(h => ({
      tag: h.tagName, level: +h.tagName[1], text: textOf(h).slice(0, 100),
    })),
    forms: [...document.querySelectorAll('form')].map(form => ({
      fields: [...form.querySelectorAll('input,select,textarea')].filter(f => f.type !== 'hidden').map(f => {
        const id = f.id;
        const label = id ? document.querySelector(`label[for="${CSS.escape(id)}"]`) : null;
        return {
          name: f.name || f.id || f.type, type: f.type || f.tagName,
          hasLabel: !!(label && textOf(label)), ariaLabel: f.getAttribute('aria-label'),
        };
      }),
    })),
    tables: [...document.querySelectorAll('table')].filter(visible).map(t => ({
      hasCaption: !!t.querySelector('caption'), thCount: t.querySelectorAll('th').length,
    })),
    media: [...document.querySelectorAll('video,audio')].filter(visible).map(m => ({ tag: m.tagName, hasControls: m.hasAttribute('controls') })),
    focusable: [...document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(visible).map(el => ({
      tag: el.tagName, role: el.getAttribute('role'), tabindex: el.tabIndex, name: accName(el).slice(0, 80),
    })),
    skipLink: [...document.querySelectorAll('a[href^="#"]')].find(a => /aller au contenu|skip/i.test(accName(a))),
    clickOnly: [...document.querySelectorAll('[onclick]')].filter(visible).filter(el => !['A','BUTTON','INPUT'].includes(el.tagName)).map(el => ({
      tag: el.tagName, name: accName(el).slice(0, 50),
    })),
  };
}
