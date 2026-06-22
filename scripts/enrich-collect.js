(() => {
  const btn = [...document.querySelectorAll('button')].find(b => /accepter|refuser tout/i.test(b.textContent || ''));
  if (btn) btn.click();

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
    const al = el.getAttribute('aria-label');
    if (al) return al.trim();
    if (el.alt) return el.alt.trim();
    if (el.title) return el.title.trim();
    return textOf(el).slice(0, 120);
  };

  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(h => ({
    tag: h.tagName, level: +h.tagName[1], text: textOf(h).slice(0, 100)
  }));
  const h1s = headings.filter(h => h.tag === 'H1');
  const jumps = [];
  for (let i = 1; i < headings.length; i++) {
    if (headings[i].level - headings[i - 1].level > 1) jumps.push({ from: headings[i - 1], to: headings[i] });
  }

  const imgs = [...document.querySelectorAll('img,[role=img]')].filter(visible);
  const imagesDetail = imgs.map(el => ({
    tag: el.tagName, role: el.getAttribute('role'), alt: el.getAttribute('alt'),
    ariaLabel: el.getAttribute('aria-label'), ariaLabelledby: el.getAttribute('aria-labelledby'),
    title: el.getAttribute('title'), decorative: el.getAttribute('alt') === '' || ['presentation','none'].includes(el.getAttribute('role'))
  }));
  const noAlt = imagesDetail.filter(i => !i.decorative && i.alt === null && !i.ariaLabel && !i.ariaLabelledby);

  const areas = [...document.querySelectorAll('area')].map(a => ({ alt: a.getAttribute('alt'), ariaLabel: a.getAttribute('aria-label') }));
  const inputImages = [...document.querySelectorAll('input[type=image]')].map(i => ({ alt: i.getAttribute('alt'), ariaLabel: i.getAttribute('aria-label') }));
  const svgs = [...document.querySelectorAll('svg')].filter(visible).map(s => ({ role: s.getAttribute('role'), ariaLabel: s.getAttribute('aria-label') }));
  const ismaps = [...document.querySelectorAll('img[ismap]')].map(i => ({ src: (i.src||'').slice(-60) }));

  const linksNoText = [...document.querySelectorAll('a[href]')].filter(visible).filter(a => !textOf(a) && !a.getAttribute('aria-label') && !a.title)
    .map(a => ({ href: a.href.slice(0, 120), hasImg: !!a.querySelector('img,svg') }));

  const newWindowLinks = [...document.querySelectorAll('a[target=_blank], a[rel*=external]')].filter(visible).map(a => ({
    href: a.href.slice(0, 80), text: accName(a).slice(0, 60),
    warned: !!(a.getAttribute('title') || /nouvelle fen|new window|externe/i.test(accName(a) + (a.getAttribute('aria-label')||'')))
  }));

  const skipLink = [...document.querySelectorAll('a[href^="#"]')].find(a => /aller au contenu|skip/i.test(textOf(a) + (a.getAttribute('aria-label') || '')));

  const fieldsNoLabel = [...document.querySelectorAll('input,select,textarea')].filter(f => f.type !== 'hidden' && visible(f))
    .filter(f => {
      const id = f.id;
      const lb = id ? document.querySelector(`label[for="${id}"]`) : null;
      return !lb && !f.getAttribute('aria-label') && !f.getAttribute('aria-labelledby');
    }).map(f => ({ name: f.name || f.id || f.type, type: f.type || f.tagName }));

  const tabindexPositive = [...document.querySelectorAll('[tabindex]')].filter(el => parseInt(el.getAttribute('tabindex'), 10) > 0 && visible(el))
    .map(el => ({ tag: el.tagName, tabindex: el.getAttribute('tabindex') }));

  const landmarks = {
    main: !!document.querySelector('main,[role=main]'),
    nav: document.querySelectorAll('nav,[role=navigation]').length,
    header: document.querySelectorAll('header,[role=banner]').length,
    footer: document.querySelectorAll('footer,[role=contentinfo]').length
  };

  const tables = [...document.querySelectorAll('table')].filter(visible).map(t => ({
    hasCaption: !!t.querySelector('caption'), thCount: t.querySelectorAll('th').length, visible: true
  }));

  const media = [...document.querySelectorAll('video,audio')].filter(visible).map(m => ({
    tag: m.tagName, hasControls: m.hasAttribute('controls')
  }));

  const langChanges = [...document.querySelectorAll('[lang]')].filter(el => el !== document.documentElement).map(el => ({
    tag: el.tagName, lang: el.getAttribute('lang'), text: textOf(el).slice(0, 40)
  }));

  const presentationTags = [...document.querySelectorAll('b,i,u,s,strike,font,center')].filter(visible).slice(0, 10).map(el => el.tagName);

  const clickOnly = [...document.querySelectorAll('[onclick]')].filter(visible).filter(el => {
    const tag = el.tagName;
    if (['A','BUTTON','INPUT'].includes(tag)) return false;
    return !el.hasAttribute('onkeydown') && !el.hasAttribute('onkeypress') && el.getAttribute('tabindex') !== '0';
  }).map(el => ({ tag: el.tagName, onclick: !!el.getAttribute('onclick'), name: accName(el).slice(0, 50) }));

  const lists = { badStructure: [] };
  for (const ul of document.querySelectorAll('ul,ol')) {
    for (const li of ul.querySelectorAll(':scope > li')) {
      if (li.querySelector(':scope > ul, :scope > ol') && !li.querySelector(':scope > ul > li, :scope > ol > li')) {
        lists.badStructure.push({ tag: ul.tagName, text: textOf(li).slice(0, 40) });
      }
    }
  }

  const quotes = [...document.querySelectorAll('blockquote,q')].filter(visible).map(q => ({ tag: q.tagName, text: textOf(q).slice(0, 60) }));

  const meta = {
    doctype: document.doctype?.name || null,
    charset: document.characterSet,
    viewport: document.querySelector('meta[name=viewport]')?.content || null,
    hasSearch: !!document.querySelector('input[type=search], [role=search], form[action*=search], button[name*=search i]'),
    stylesheetCount: document.styleSheets.length,
    hasStylesheets: document.querySelectorAll('link[rel=stylesheet], style').length > 0 || document.styleSheets.length > 0
  };

  const parseRgb = (c) => { const m = c.match(/[\d.]+/g); return m && m.length >= 3 ? m.slice(0, 3).map(Number) : null; };
  const lum = ([r,g,b]) => { const a=[r,g,b].map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}); return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2]; };
  const ratio = (fg,bg) => { const L1=lum(fg),L2=lum(bg); return (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05); };
  const bgOf = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const bg = parseRgb(getComputedStyle(n).backgroundColor);
      if (bg && (bg[0]+bg[1]+bg[2]>0) && getComputedStyle(n).backgroundColor !== 'rgba(0, 0, 0, 0)') return bg;
      n = n.parentElement;
    }
    return parseRgb(getComputedStyle(document.body).backgroundColor) || [255,255,255];
  };
  const contrastFails = []; let contrastChecked = 0;
  for (const el of [...document.querySelectorAll('p,span,a,button,h1,h2,h3,h4,h5,h6,label,li')].filter(visible)) {
    const text = textOf(el); if (text.length < 2) continue;
    const fg = parseRgb(getComputedStyle(el).color); const bg = bgOf(el);
    if (!fg || !bg) continue;
    const r = ratio(fg,bg); contrastChecked++;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const bold = parseInt(getComputedStyle(el).fontWeight,10) >= 700;
    const min = (fs >= 18 || (fs >= 14 && bold)) ? 3 : 4.5;
    if (r < min) contrastFails.push({ tag: el.tagName, text: text.slice(0,50), ratio: Math.round(r*100)/100, min });
  }

  return {
    collect: {
      url: location.href, title: document.title, lang: document.documentElement.lang || '',
      h1Count: h1s.length, h1Texts: h1s.map(h => h.text), headings, headingJumps: jumps,
      images: { total: imgs.length, withoutAlt: noAlt.length }, imagesDetail, noAlt,
      areas, inputImages, svgs, ismaps, linksNoText, newWindowLinks, skipLink: skipLink ? { text: textOf(skipLink), href: skipLink.getAttribute('href') } : null,
      fieldsNoLabel, tabindexPositive, landmarks, tables, media, langChanges, presentationTags,
      scriptsA11y: { clickOnly }, lists, quotes,
      hasStylesheets: meta.hasStylesheets,
      focusableCount: [...document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(visible).length,
      iframesNoTitle: [...document.querySelectorAll('iframe')].filter(visible).filter(f => !f.title).length,
      iframesDetail: [...document.querySelectorAll('iframe')].map(f => ({ title: f.getAttribute('title'), visible: visible(f) }))
    },
    contrast: { checked: contrastChecked, failCount: contrastFails.length, fails: contrastFails.slice(0, 25) },
    meta
  };
})()
