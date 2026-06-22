/**
 * Collecte accessibilité DOM — exécuté via browser_cdp Runtime.evaluate
 * Retourne un objet JSON sérialisable pour scoring RGAA.
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const accName = (el) => {
    const labelledby = el.getAttribute('aria-labelledby');
    if (labelledby) {
      const t = labelledby.split(/\s+/).map(id => document.getElementById(id)).filter(Boolean).map(textOf).join(' ');
      if (t) return t;
    }
    const al = el.getAttribute('aria-label');
    if (al) return al.trim();
    if (el.alt) return el.alt.trim();
    if (el.title) return el.title.trim();
    return textOf(el).slice(0, 120);
  };

  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({
    tag: h.tagName, level: +h.tagName[1], text: textOf(h).slice(0, 100), visible: visible(h)
  }));
  const h1s = headings.filter(h => h.tag === 'H1' && h.visible);

  const images = [...document.querySelectorAll('img,[role="img"]')].map(el => ({
    tag: el.tagName, role: el.getAttribute('role'), alt: el.getAttribute('alt'),
    ariaLabel: el.getAttribute('aria-label'), ariaLabelledby: el.getAttribute('aria-labelledby'),
    title: el.getAttribute('title'), src: (el.src || '').slice(-80), visible: visible(el),
    decorative: el.getAttribute('alt') === '' || el.getAttribute('role') === 'presentation' || el.getAttribute('role') === 'none'
  }));

  const links = [...document.querySelectorAll('a[href]')].map(a => ({
    text: textOf(a).slice(0, 80), href: a.href.slice(0, 120),
    ariaLabel: a.getAttribute('aria-label'), title: a.getAttribute('title'),
    hasImgOnly: !textOf(a) && a.querySelector('img,svg'), visible: visible(a)
  }));
  const linksNoText = links.filter(l => l.visible && !l.text && !l.ariaLabel && !l.title);

  const iframes = [...document.querySelectorAll('iframe')].map(f => ({
    title: f.getAttribute('title'), src: (f.src || '').slice(0, 80), visible: visible(f)
  }));

  const skipLink = [...document.querySelectorAll('a[href^="#"]')].find(a =>
    /aller au contenu|skip|contenu principal/i.test(accName(a))
  );

  const lang = document.documentElement.lang || document.documentElement.getAttribute('xml:lang') || '';
  const pageTitle = document.title;

  const forms = [...document.querySelectorAll('form')].map(form => {
    const fields = [...form.querySelectorAll('input,select,textarea')].filter(i => i.type !== 'hidden' && i.type !== 'submit');
    return {
      action: (form.action || '').slice(0, 80),
      fields: fields.map(f => {
        const id = f.id;
        const label = id ? form.querySelector(`label[for="${id}"]`) || document.querySelector(`label[for="${id}"]`) : null;
        const ariaLabel = f.getAttribute('aria-label');
        const ariaLabelledby = f.getAttribute('aria-labelledby');
        const placeholder = f.getAttribute('placeholder');
        const name = f.name || f.id || f.type;
        return {
          tag: f.tagName, type: f.type || '', name, id,
          hasLabel: !!(label && textOf(label)), labelText: label ? textOf(label).slice(0, 60) : null,
          ariaLabel, ariaLabelledby, placeholder, visible: visible(f)
        };
      })
    };
  });
  const fieldsNoLabel = forms.flatMap(f => f.fields.filter(x => x.visible && !x.hasLabel && !x.ariaLabel && !x.ariaLabelledby));

  const focusable = [...document.querySelectorAll(
    'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"]),[contenteditable="true"]'
  )].filter(visible).map(el => ({
    tag: el.tagName, role: el.getAttribute('role'), tabindex: el.tabIndex,
    name: accName(el).slice(0, 80), type: el.type || ''
  }));

  const tabindexPositive = [...document.querySelectorAll('[tabindex]')].filter(el => {
    const t = parseInt(el.getAttribute('tabindex'), 10);
    return t > 0 && visible(el);
  }).map(el => ({ tag: el.tagName, tabindex: el.getAttribute('tabindex'), name: accName(el).slice(0, 60) }));

  const landmarks = [...document.querySelectorAll('main,nav,header,footer,aside,[role="main"],[role="navigation"],[role="banner"],[role="contentinfo"]')]
    .map(el => ({ tag: el.tagName, role: el.getAttribute('role') || el.tagName.toLowerCase(), visible: visible(el) }));

  const tables = [...document.querySelectorAll('table')].map(t => {
    const th = t.querySelectorAll('th').length;
    const caption = t.querySelector('caption');
    return { hasCaption: !!caption, captionText: caption ? textOf(caption).slice(0, 80) : null, thCount: th, visible: visible(t) };
  });

  const media = [...document.querySelectorAll('video,audio')].map(m => ({
    tag: m.tagName, hasControls: m.hasAttribute('controls'), visible: visible(m)
  }));

  // Heading hierarchy jumps
  const visibleHeadings = headings.filter(h => h.visible);
  const headingJumps = [];
  for (let i = 1; i < visibleHeadings.length; i++) {
    const diff = visibleHeadings[i].level - visibleHeadings[i - 1].level;
    if (diff > 1) headingJumps.push({ from: visibleHeadings[i - 1], to: visibleHeadings[i] });
  }

  return {
    url: location.href,
    title: pageTitle,
    lang,
    skipLink: skipLink ? { text: accName(skipLink), href: skipLink.getAttribute('href') } : null,
    h1Count: h1s.length,
    h1Texts: h1s.map(h => h.text),
    headings: visibleHeadings,
    headingJumps,
    images: { total: images.length, decorative: images.filter(i => i.decorative).length, withoutAlt: images.filter(i => i.visible && !i.decorative && i.alt === null && !i.ariaLabel && !i.ariaLabelledby).length },
    imagesDetail: images.filter(i => i.visible),
    linksNoText,
    iframesNoTitle: iframes.filter(f => f.visible && !f.title),
    fieldsNoLabel,
    tabindexPositive,
    landmarks,
    tables,
    media,
    focusableCount: focusable.length
  };
}
