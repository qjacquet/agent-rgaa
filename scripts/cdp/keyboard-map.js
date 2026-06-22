/**
 * Cartographie focusables pour tests clavier (7.3, 12.8).
 * Après browser_press_key Tab, comparer avec browser_snapshot.
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
  const accName = (el) => el.getAttribute('aria-label') || el.getAttribute('alt') || textOf(el);

  const focusable = [...document.querySelectorAll(
    'a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"]),[contenteditable=true]'
  )].filter(visible);

  return {
    count: focusable.length,
    order: focusable.map((el, i) => ({
      index: i,
      tag: el.tagName,
      type: el.type || '',
      name: accName(el),
      tabindex: el.tabIndex,
      href: el.href ? el.href.slice(0, 80) : null,
    })),
    tabindexPositive: [...document.querySelectorAll('[tabindex]')].filter(el => parseInt(el.getAttribute('tabindex'), 10) > 0 && visible(el)).map(el => ({
      tag: el.tagName, tabindex: el.getAttribute('tabindex'), name: accName(el),
    })),
  };
}
