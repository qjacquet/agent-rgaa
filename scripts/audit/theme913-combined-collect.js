(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  [...document.querySelectorAll('button')].find((b) => /accepter|tout accepter|refuser tout/i.test(b.textContent || ''))?.click();

  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el?.innerText || el?.textContent || '').trim().replace(/\s+/g, ' ');
  const accName = (el) => {
    const lb = el.getAttribute('aria-labelledby');
    if (lb) {
      const t = lb.split(/\s+/).map((id) => document.getElementById(id)).filter(Boolean).map(textOf).join(' ');
      if (t) return t;
    }
    return el.getAttribute('aria-label') || el.getAttribute('alt') || el.getAttribute('title') || textOf(el);
  };

  // --- Theme 9: Structuration ---
  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter(visible).map((h) => ({
    tag: h.tagName,
    role: h.getAttribute('role'),
    level: h.tagName.match(/^H(\d)$/) ? +h.tagName[1] : +(h.getAttribute('aria-level') || 0),
    text: textOf(h).slice(0, 100),
    empty: !textOf(h),
  }));
  const headingJumps = [];
  for (let i = 1; i < headings.length; i++) {
    if (headings[i].level && headings[i - 1].level && headings[i].level - headings[i - 1].level > 1) {
      headingJumps.push({ from: headings[i - 1], to: headings[i] });
    }
  }
  const emptyHeadings = headings.filter((h) => h.empty);
  const navEls = [...document.querySelectorAll('nav,[role=navigation]')];
  const navOutsideNav = [...document.querySelectorAll('ul,ol')].filter((l) => {
    const links = l.querySelectorAll('a[href]');
    return links.length >= 3 && !l.closest('nav,[role=navigation],header,footer,aside') && visible(l);
  }).slice(0, 5).map((l) => ({ tag: l.tagName, linkCount: l.querySelectorAll('a[href]').length }));

  const landmarks = {
    hasHeader: !!document.querySelector('header,[role=banner]'),
    navCount: navEls.length,
    hasMain: !!document.querySelector('main,[role=main]'),
    hasFooter: !!document.querySelector('footer,[role=contentinfo]'),
    navMisuse: [...document.querySelectorAll('nav')].filter((n) => !n.querySelector('a[href],button') && textOf(n).length < 5).length,
    asideCount: document.querySelectorAll('aside,[role=complementary]').length,
  };

  const lists = {
    ul: document.querySelectorAll('ul,[role=list]').length,
    ol: document.querySelectorAll('ol').length,
    dl: document.querySelectorAll('dl').length,
    badUlOl: [],
    badDl: [],
  };
  for (const ul of document.querySelectorAll('ul,ol')) {
    const directLi = ul.querySelectorAll(':scope > li');
    if (directLi.length === 0 && ul.querySelectorAll('li').length > 0) {
      lists.badUlOl.push({ tag: ul.tagName, reason: 'li not direct child' });
    }
  }
  for (const dl of document.querySelectorAll('dl')) {
    const dts = dl.querySelectorAll('dt');
    const dds = dl.querySelectorAll('dd');
    if ((dts.length || dds.length) && (dts.length !== dds.length)) {
      lists.badDl.push({ dts: dts.length, dds: dds.length });
    }
  }

  const quotes = {
    blockquote: [...document.querySelectorAll('blockquote')].filter(visible).map((q) => ({ text: textOf(q).slice(0, 60) })),
    q: [...document.querySelectorAll('q')].filter(visible).map((q) => ({ text: textOf(q).slice(0, 60) })),
    inlineCitations: [...document.querySelectorAll('p,li,td')].filter(visible).filter((el) => /[«""].{10,}[»""]/.test(textOf(el)) && !el.querySelector('q,blockquote')).slice(0, 5).map((el) => textOf(el).slice(0, 60)),
    blockCitations: [...document.querySelectorAll('p,div')].filter(visible).filter((el) => el.classList.contains('quote') || el.classList.contains('citation')).slice(0, 5).map((el) => ({ tag: el.tagName, text: textOf(el).slice(0, 60), hasBlockquote: !!el.closest('blockquote') || el.tagName === 'BLOCKQUOTE' })),
  };

  // --- Theme 10: Présentation ---
  const deprecatedTags = ['basefont', 'big', 'blink', 'center', 'font', 'marquee', 's', 'strike'];
  const presentationTags = deprecatedTags.flatMap((tag) => [...document.querySelectorAll(tag)].filter(visible).map((el) => ({ tag: el.tagName, text: textOf(el).slice(0, 40) })));
  const presentationAttrs = [];
  const presAttrNames = ['align', 'alink', 'background', 'bgcolor', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff', 'clear', 'compact', 'height', 'hspace', 'language', 'link', 'text', 'vlink', 'vspace', 'width'];
  for (const el of document.querySelectorAll('*')) {
    for (const a of presAttrNames) {
      if (el.hasAttribute(a)) presentationAttrs.push({ tag: el.tagName, attr: a });
    }
  }
  const nbspAbuse = [...document.querySelectorAll('p,td,th,span,div')].filter(visible).filter((el) => {
    const raw = el.textContent || '';
    return /\u00a0{2,}/.test(raw) || /(\s{3,})/.test(raw.replace(/\u00a0/g, ' '));
  }).slice(0, 10).map((el) => ({ tag: el.tagName, text: textOf(el).slice(0, 40) }));

  const parseRgb = (c) => { const m = c.match(/[\d.]+/g); return m && m.length >= 3 ? m.slice(0, 3).map(Number) : null; };
  const lum = ([r, g, b]) => { const a = [r, g, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]; };
  const ratio = (fg, bg) => { const L1 = lum(fg), L2 = lum(bg); return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05); };
  const bgOf = (el) => {
    let n = el;
    while (n && n !== document.documentElement) {
      const bg = parseRgb(getComputedStyle(n).backgroundColor);
      if (bg && bg.some((x) => x > 0) && getComputedStyle(n).backgroundColor !== 'rgba(0, 0, 0, 0)') return bg;
      n = n.parentElement;
    }
    return parseRgb(getComputedStyle(document.body).backgroundColor) || [255, 255, 255];
  };
  const contrastFails = [];
  let contrastChecked = 0;
  for (const el of [...document.querySelectorAll('p,span,a,button,h1,h2,h3,h4,h5,h6,label,li,td,th')].filter(visible)) {
    const text = textOf(el);
    if (text.length < 2) continue;
    const fg = parseRgb(getComputedStyle(el).color);
    const bg = bgOf(el);
    if (!fg || !bg) continue;
    const r = ratio(fg, bg);
    contrastChecked++;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const bold = parseInt(getComputedStyle(el).fontWeight, 10) >= 700;
    const min = (fs >= 18 || (fs >= 14 && bold)) ? 3 : 4.5;
    if (r < min) contrastFails.push({ tag: el.tagName, text: text.slice(0, 50), ratio: Math.round(r * 100) / 100, min });
  }

  const coloredTextNoBg = [];
  for (const el of [...document.querySelectorAll('p,span,li,td,th,label,h1,h2,h3,h4,h5,h6')].filter(visible)) {
    const color = getComputedStyle(el).color;
    const bg = getComputedStyle(el).backgroundColor;
    if (color && bg === 'rgba(0, 0, 0, 0)' && el.tagName !== 'A') {
      const parentBg = bgOf(el);
      if (parentBg) coloredTextNoBg.push({ tag: el.tagName, color, text: textOf(el).slice(0, 40) });
    }
  }

  const links = [...document.querySelectorAll('a[href],[role=link]')].filter(visible).map((a) => {
    const s = getComputedStyle(a);
    const underline = s.textDecorationLine.includes('underline') || s.textDecoration.includes('underline');
    const diffColor = s.color !== getComputedStyle(a.parentElement || document.body).color;
    const hasIndicator = underline || diffColor || a.querySelector('img,svg') || a.getAttribute('aria-label');
    return { text: textOf(a).slice(0, 60), colorOnly: !hasIndicator && !!textOf(a), href: (a.href || '').slice(0, 80) };
  });
  const colorOnlyLinks = links.filter((l) => l.colorOnly);

  const focusableEls = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"]),[contenteditable=true]')].filter(visible);
  const noFocusOutline = focusableEls.filter((el) => {
    const s = getComputedStyle(el);
    return (s.outlineStyle === 'none' || s.outlineWidth === '0px') && !s.boxShadow && s.borderWidth === '0px';
  }).slice(0, 15).map((el) => ({ tag: el.tagName, name: accName(el).slice(0, 50) }));

  const hiddenContent = [...document.querySelectorAll('[hidden],[aria-hidden=true]')].map((el) => ({
    tag: el.tagName, role: el.getAttribute('role'), text: textOf(el).slice(0, 60),
    focusable: el.matches('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])'),
  }));
  const hiddenWithFocusable = hiddenContent.filter((h) => h.focusable);

  const bgImageText = [...document.querySelectorAll('*')].filter(visible).filter((el) => {
    const s = getComputedStyle(el);
    return s.backgroundImage && s.backgroundImage !== 'none' && textOf(el).length > 2;
  }).slice(0, 10).map((el) => ({ tag: el.tagName, text: textOf(el).slice(0, 40) }));

  const hoverTooltips = [...document.querySelectorAll('[title],[data-tooltip],[aria-describedby]')].filter(visible).slice(0, 20).map((el) => ({
    tag: el.tagName, title: el.getAttribute('title'), name: accName(el).slice(0, 40),
  }));

  // --- Theme 11: Formulaires ---
  const formFields = [...document.querySelectorAll('input,select,textarea')].filter((f) => f.type !== 'hidden' && visible(f)).map((f) => {
    const id = f.id;
    const label = id ? document.querySelector(`label[for="${CSS.escape(id)}"]`) : f.closest('label');
    const ariaLabel = f.getAttribute('aria-label');
    const ariaLabelledby = f.getAttribute('aria-labelledby');
    const title = f.getAttribute('title');
    const placeholder = f.getAttribute('placeholder');
    const hasLabel = !!(label || ariaLabel || ariaLabelledby || title);
    const labelText = label ? textOf(label) : (ariaLabel || title || '');
    const visibleLabelNear = label && visible(label);
    return {
      tag: f.tagName, type: f.type || '', name: f.name || f.id || '', id,
      hasLabel, labelText: labelText.slice(0, 80), visibleLabelNear,
      ariaLabel, ariaLabelledby, title, placeholder,
      required: f.required || f.getAttribute('aria-required') === 'true',
      ariaInvalid: f.getAttribute('aria-invalid') === 'true',
      autocomplete: f.getAttribute('autocomplete'),
      labelMismatch: label && ariaLabel && !ariaLabel.toLowerCase().includes(textOf(label).toLowerCase().slice(0, 10)) && textOf(label).length > 3,
    };
  });
  const fieldsNoLabel = formFields.filter((f) => !f.hasLabel);
  const buttons = [...document.querySelectorAll('button,input[type=submit],input[type=button],input[type=reset]')].filter(visible).map((b) => ({
    tag: b.tagName, type: b.type || '', text: textOf(b).slice(0, 60), name: accName(b).slice(0, 60),
    ariaMismatch: !!(textOf(b) && b.getAttribute('aria-label') && !accName(b).toLowerCase().includes(textOf(b).toLowerCase().slice(0, 8))),
  }));
  const fieldsets = [...document.querySelectorAll('fieldset')].map((fs) => ({
    legend: textOf(fs.querySelector('legend')).slice(0, 80),
    hasLegend: !!fs.querySelector('legend'),
    fieldCount: fs.querySelectorAll('input,select,textarea').length,
  }));
  const optgroups = [...document.querySelectorAll('optgroup')].map((og) => ({
    label: og.getAttribute('label'), hasLabel: !!og.getAttribute('label'),
  }));
  const optgroupsNoLabel = optgroups.filter((o) => !o.hasLabel);
  const errorMsgs = [...document.querySelectorAll('[role=alert],.error,.invalid,.field-error,[class*=error],[class*=invalid]')].filter(visible).map((el) => ({
    tag: el.tagName, role: el.getAttribute('role'), text: textOf(el).slice(0, 100),
  }));
  const forms = [...document.querySelectorAll('form')].map((f) => ({
    action: (f.action || '').slice(0, 80),
    hasSubmit: !!f.querySelector('button[type=submit],input[type=submit]'),
    hasReset: !!f.querySelector('button[type=reset],input[type=reset],button:not([type])'),
    method: f.method,
    fieldCount: f.querySelectorAll('input,select,textarea').length,
  }));
  const userFields = formFields.filter((f) => /nom|name|email|tel|phone|address|adresse|postal|ville|city|user|prenom|prénom|siren|siret/i.test(f.name + f.id + f.labelText));

  // --- Theme 12: Navigation ---
  const skipLink = [...document.querySelectorAll('a[href^="#"]')].find((a) => /aller au contenu|skip to|accès rapide|contenu principal/i.test(textOf(a) + (a.getAttribute('aria-label') || '')));
  const mainEl = document.querySelector('main,[role=main]');
  const sitemapLinks = [...document.querySelectorAll('a[href]')].filter((a) => /plan du site|sitemap/i.test(textOf(a) + (a.getAttribute('aria-label') || ''))).map((a) => ({ text: textOf(a), href: a.href.slice(0, 80) }));
  const searchInputs = [...document.querySelectorAll('input[type=search],input[name*=search i],input[placeholder*=recherche i],form[role=search],form[action*=search]')].filter(visible);
  const navSignature = navEls.map((n) => ({
    linkTexts: [...n.querySelectorAll('a[href]')].slice(0, 15).map((a) => textOf(a).slice(0, 40)),
    htmlHash: [...n.querySelectorAll('a[href]')].slice(0, 10).map((a) => a.getAttribute('href')).join('|'),
  }));
  const focusOrder = focusableEls.map((el, i) => ({
    index: i, tag: el.tagName, type: el.type || '', name: accName(el).slice(0, 60), tabindex: el.tabIndex,
  }));
  const tabindexPositive = [...document.querySelectorAll('[tabindex]')].filter((el) => parseInt(el.getAttribute('tabindex'), 10) > 0 && visible(el)).map((el) => ({
    tag: el.tagName, tabindex: el.getAttribute('tabindex'), name: accName(el).slice(0, 50),
  }));
  const landmarkZones = [...document.querySelectorAll('header,nav,main,footer,aside,[role=banner],[role=navigation],[role=main],[role=contentinfo],[role=complementary]')].filter(visible).map((el) => ({
    tag: el.tagName, role: el.getAttribute('role'), hasAriaLabel: !!(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')),
  }));
  const singleKeyShortcuts = [];

  // --- Theme 13: Consultation ---
  const metaRefresh = [...document.querySelectorAll('meta[http-equiv=refresh i],meta[http-equiv="refresh"]')].map((m) => m.getAttribute('content'));
  const autoRedirects = [...document.querySelectorAll('script')].filter((s) => /location\.(href|replace)|window\.open|setTimeout.*location/i.test(s.textContent || '')).length;
  const popupTriggers = [...document.querySelectorAll('[onclick*=window.open],[onclick*=open\\(]')].length;
  const officeDownloads = [...document.querySelectorAll('a[href]')].filter((a) => /\.(doc|docx|xls|xlsx|ppt|pptx|odt|ods)(\?|$)/i.test(a.href)).map((a) => ({
    href: a.href.slice(0, 100), text: textOf(a).slice(0, 60),
    altFormat: !!(a.closest('li,p')?.querySelector('a[href$=".pdf"],a[href*=".pdf"]') || /pdf|accessible|html/i.test(textOf(a.parentElement))),
  }));
  const cryptic = [...document.querySelectorAll('abbr,span,p')].filter(visible).filter((el) => {
    const t = textOf(el);
    return (/\p{Extended_Pictographic}/u.test(t) && t.length < 30) || /^[\W_]{3,}$/.test(t);
  }).slice(0, 10).map((el) => ({ tag: el.tagName, text: textOf(el).slice(0, 40), title: el.getAttribute('title') }));
  const blinking = [...document.querySelectorAll('marquee,blink')].length;
  const animations = [...document.querySelectorAll('*')].filter((el) => {
    const s = getComputedStyle(el);
    return s.animationName && s.animationName !== 'none' && s.animationIterationCount !== 'infinite';
  }).length;
  const autoMoving = [...document.querySelectorAll('marquee,[autoplay]')].filter(visible).map((el) => ({ tag: el.tagName, autoplay: el.hasAttribute('autoplay') }));
  const touchOnly = [...document.querySelectorAll('[ontouchstart],[data-swipe],[data-gesture]')].length;
  const motionFeatures = [...document.querySelectorAll('[ondevicemotion],[ondeviceorientation]')].length;

  return {
    url: location.href,
    title: document.title,
    theme9: { headings, headingJumps, emptyHeadings, landmarks, navOutsideNav, lists, quotes },
    theme10: {
      presentationTags, presentationAttrs: presentationAttrs.slice(0, 30), nbspAbuse,
      contrast: { checked: contrastChecked, failCount: contrastFails.length, fails: contrastFails.slice(0, 25) },
      coloredTextNoBg: coloredTextNoBg.slice(0, 15), colorOnlyLinks, noFocusOutline, hiddenContent, hiddenWithFocusable,
      bgImageText, hoverTooltips, hasStylesheets: document.styleSheets.length > 0 || document.querySelectorAll('link[rel=stylesheet],style').length > 0,
    },
    theme11: {
      formFields, fieldsNoLabel, buttons, fieldsets, optgroups, optgroupsNoLabel, errorMsgs, forms, userFields,
      formCount: document.querySelectorAll('form').length,
    },
    theme12: {
      skipLink: skipLink ? { text: textOf(skipLink), href: skipLink.getAttribute('href') } : null,
      hasMain: !!mainEl, sitemapLinks, searchInputs: searchInputs.length, navSignature,
      focusOrder, tabindexPositive, landmarkZones, singleKeyShortcuts,
      focusableCount: focusableEls.length,
    },
    theme13: {
      metaRefresh, autoRedirects, popupTriggers, officeDownloads, cryptic, blinking, animations, autoMoving,
      touchOnly, motionFeatures,
    },
  };
})()
