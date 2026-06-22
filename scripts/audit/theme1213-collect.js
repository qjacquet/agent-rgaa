(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  [...document.querySelectorAll('button')].find(b => /accepter|tout accepter|refuser tout/i.test(b.textContent || ''))?.click();
  const v = el => { const s = getComputedStyle(el), r = el.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  const t = el => (el?.innerText || el?.textContent || '').trim().replace(/\s+/g, ' ');
  const acc = el => el.getAttribute('aria-label') || el.getAttribute('title') || t(el);
  const navEls = [...document.querySelectorAll('nav,[role=navigation]')];
  const skipLink = [...document.querySelectorAll('a[href^="#"]')].find(a => /aller au contenu|skip to|accès rapide|contenu principal/i.test(t(a) + (a.getAttribute('aria-label') || '')));
  const sitemapLinks = [...document.querySelectorAll('a[href]')].filter(a => /plan du site|sitemap/i.test(t(a) + (a.getAttribute('aria-label') || ''))).map(a => ({ text: t(a), href: a.href.slice(0, 80) }));
  const focusable = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"]),[contenteditable=true]')].filter(v);
  const navSignature = navEls.map(n => ({ linkTexts: [...n.querySelectorAll('a[href]')].slice(0, 15).map(a => t(a).slice(0, 40)), htmlHash: [...n.querySelectorAll('a[href]')].slice(0, 10).map(a => a.getAttribute('href')).join('|') }));
  const landmarkZones = [...document.querySelectorAll('header,nav,main,footer,aside,[role=banner],[role=navigation],[role=main],[role=contentinfo],[role=complementary]')].filter(v).map(el => ({ tag: el.tagName, role: el.getAttribute('role'), hasAriaLabel: !!(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) }));
  const metaRefresh = [...document.querySelectorAll('meta[http-equiv=refresh i],meta[http-equiv="refresh"]')].map(m => m.getAttribute('content'));
  const autoRedirects = [...document.querySelectorAll('script')].filter(s => /location\.(href|replace)|window\.open|setTimeout.*location/i.test(s.textContent || '')).length;
  const popupTriggers = [...document.querySelectorAll('[onclick]')].filter(el => /window\.open/i.test(el.getAttribute('onclick') || '')).length;
  const officeDownloads = [...document.querySelectorAll('a[href]')].filter(a => /\.(doc|docx|xls|xlsx|ppt|pptx|odt|ods)(\?|$)/i.test(a.href)).map(a => ({ href: a.href.slice(0, 100), text: t(a).slice(0, 60), altFormat: !!(a.closest('li,p')?.querySelector('a[href$=".pdf"],a[href*=".pdf"]') || /pdf|accessible|html/i.test(t(a.parentElement))) }));
  const cryptic = [...document.querySelectorAll('abbr,span,p')].filter(v).filter(el => { const tx = t(el); return (/\p{Extended_Pictographic}/u.test(tx) && tx.length < 30) || /^[\W_]{3,}$/.test(tx); }).slice(0, 10).map(el => ({ tag: el.tagName, text: t(el).slice(0, 40), title: el.getAttribute('title') }));
  return {
    url: location.href,
    title: document.title,
    theme12: {
      skipLink: skipLink ? { text: t(skipLink), href: skipLink.getAttribute('href') } : null,
      hasMain: !!document.querySelector('main,[role=main]'),
      sitemapLinks,
      searchInputs: [...document.querySelectorAll('input[type=search],input[name*=search i],input[placeholder*=recherche i],form[role=search],form[action*=search]')].filter(v).length,
      navSignature,
      focusOrder: focusable.map((el, i) => ({ index: i, tag: el.tagName, type: el.type || '', name: acc(el).slice(0, 60), tabindex: el.tabIndex })),
      tabindexPositive: [...document.querySelectorAll('[tabindex]')].filter(el => parseInt(el.getAttribute('tabindex'), 10) > 0 && v(el)).map(el => ({ tag: el.tagName, tabindex: el.getAttribute('tabindex'), name: acc(el).slice(0, 50) })),
      landmarkZones,
      singleKeyShortcuts: [],
      focusableCount: focusable.length
    },
    theme13: {
      metaRefresh,
      autoRedirects,
      popupTriggers,
      officeDownloads,
      cryptic,
      blinking: [...document.querySelectorAll('marquee,blink')].length,
      animations: 0,
      autoMoving: [...document.querySelectorAll('marquee,[autoplay]')].filter(v).map(el => ({ tag: el.tagName })),
      touchOnly: [...document.querySelectorAll('[ontouchstart],[data-swipe],[data-gesture]')].length,
      motionFeatures: [...document.querySelectorAll('[ondevicemotion],[ondeviceorientation]')].length
    }
  };
})()
