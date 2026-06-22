/**
 * Scan contrastes texte — substitut Colour Contrast Analyser / WCAG Contrast Checker
 * Exécuter via browser_cdp → Runtime.evaluate
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const parseRgb = (c) => {
    const m = c.match(/[\d.]+/g);
    if (!m || m.length < 3) return null;
    return m.slice(0, 3).map(Number);
  };
  const lum = ([r, g, b]) => {
    const a = [r, g, b].map((v) => {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
  };
  const ratio = (fg, bg) => {
    const L1 = lum(fg);
    const L2 = lum(bg);
    return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
  };
  const bgOf = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const bg = parseRgb(getComputedStyle(n).backgroundColor);
      if (bg && bg.some((x) => x > 0) && getComputedStyle(n).backgroundColor !== 'rgba(0, 0, 0, 0)') {
        return { rgb: bg, source: n.tagName };
      }
      n = n.parentElement;
    }
    return { rgb: parseRgb(getComputedStyle(document.body).backgroundColor), source: 'body-fallback' };
  };

  const selectors = 'p,span,a,button,h1,h2,h3,h4,h5,h6,label,li,td,th,input,textarea';
  const fails = [];
  const nt = [];
  let checked = 0;

  for (const el of [...document.querySelectorAll(selectors)].filter(visible)) {
    const text = (el.innerText || '').trim();
    if (!text || text.length < 2) continue;
    const fg = parseRgb(getComputedStyle(el).color);
    const bgInfo = bgOf(el);
    if (!fg || !bgInfo.rgb) {
      nt.push({ tag: el.tagName, text: text.slice(0, 40), reason: 'couleur non parseable' });
      continue;
    }
    const r = ratio(fg, bgInfo.rgb);
    checked++;
    const large = parseFloat(getComputedStyle(el).fontSize) >= 18 || (parseFloat(getComputedStyle(el).fontSize) >= 14 && (getComputedStyle(el).fontWeight === 'bold' || parseInt(getComputedStyle(el).fontWeight, 10) >= 700));
    const min = large ? 3 : 4.5;
    if (r < min) {
      fails.push({
        tag: el.tagName,
        text: text.slice(0, 50),
        ratio: Math.round(r * 100) / 100,
        min,
        fg: getComputedStyle(el).color,
        bg: bgInfo.source,
      });
    }
  }

  return {
    checked,
    failCount: fails.length,
    ntCount: nt.length,
    fails: fails.slice(0, 30),
    nt: nt.slice(0, 10),
  };
};
