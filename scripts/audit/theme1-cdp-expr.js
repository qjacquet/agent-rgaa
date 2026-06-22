() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const labelledByText = (el) => {
    const lb = el.getAttribute('aria-labelledby');
    if (!lb) return '';
    return lb.split(/\s+/).map((id) => document.getElementById(id)).filter(Boolean).map(textOf).join(' ');
  };
  const accName = (el) =>
    labelledByText(el) ||
    el.getAttribute('aria-label') ||
    el.getAttribute('alt') ||
    el.getAttribute('title') ||
    '';
  const hasAltText = (el) => !!accName(el);
  const isDecorative = (el) => {
    if (el.getAttribute('role') === 'presentation' || el.getAttribute('aria-hidden') === 'true') return true;
    if (el.tagName === 'IMG' && el.getAttribute('alt') === '') return true;
    if (el.getAttribute('role') === 'img' && el.getAttribute('aria-label') === '') return false;
    return false;
  };
  const isCaptcha = (el) =>
    /captcha|recaptcha|hcaptcha/i.test(
      (el.className?.baseVal || el.className || '') + ' ' + (el.id || '') + ' ' + (el.src || '') + ' ' + (el.outerHTML || '').slice(0, 500),
    );
  const hasLegend = (el) => {
    const fig = el.closest('figure');
    if (fig?.querySelector('figcaption')) return true;
    const next = el.nextElementSibling;
    if (next?.tagName === 'FIGCAPTION') return true;
    return false;
  };
  const svgHasTitle = (svg) => !!svg.querySelector('title')?.textContent?.trim();
  const svgHasText = (svg) => {
    const texts = [...svg.querySelectorAll('text,tspan')].map(textOf).join('');
    return texts.length > 0;
  };
  const isTextImage = (el) => {
    if (el.tagName === 'SVG') return svgHasText(el);
    const src = el.src || el.getAttribute('src') || '';
    const alt = el.getAttribute('alt') || '';
    return /logo|texte|banner|heading|titre/i.test(src + alt) || (el.tagName === 'IMG' && alt.length > 20);
  };
  const hasLongdesc = (el) =>
    !!el.getAttribute('longdesc') ||
    !!el.getAttribute('aria-describedby') ||
    !!document.getElementById(el.getAttribute('aria-describedby') || '___');

  const imgs = [...document.querySelectorAll('img,[role="img"]')].filter(visible);
  const areas = [...document.querySelectorAll('area')];
  const inputImages = [...document.querySelectorAll('input[type="image"]')];
  const ismapImgs = [...document.querySelectorAll('img[ismap]')];
  const svgs = [...document.querySelectorAll('svg')].filter(visible);
  const objects = [...document.querySelectorAll('object')].filter((o) => /^image\//i.test(o.getAttribute('type') || ''));
  const embeds = [...document.querySelectorAll('embed')].filter((e) => /^image\//i.test(e.getAttribute('type') || ''));
  const canvases = [...document.querySelectorAll('canvas')].filter(visible);

  const mapEl = (el, extra = {}) => ({
    tag: el.tagName,
    alt: el.getAttribute('alt'),
    ariaLabel: el.getAttribute('aria-label'),
    ariaLabelledby: el.getAttribute('aria-labelledby'),
    ariaDescribedby: el.getAttribute('aria-describedby'),
    title: el.getAttribute('title'),
    role: el.getAttribute('role'),
    ariaHidden: el.getAttribute('aria-hidden'),
    src: (el.src || el.getAttribute('src') || '').slice(-80),
    hasLegend: hasLegend(el),
    isCaptcha: isCaptcha(el),
    isDecorative: isDecorative(el),
    hasAltText: hasAltText(el),
    accName: accName(el).slice(0, 120),
    ...extra,
  });

  const infoImgs = imgs.filter((el) => !isDecorative(el));
  const decImgs = imgs.filter((el) => isDecorative(el));
  const captchaImgs = imgs.filter(isCaptcha);

  const svgDetails = svgs.map((s) => ({
    role: s.getAttribute('role'),
    ariaLabel: s.getAttribute('aria-label'),
    ariaHidden: s.getAttribute('aria-hidden'),
    hasTitle: svgHasTitle(s),
    hasText: svgHasText(s),
    hasLegend: hasLegend(s),
    parentText: textOf(s.parentElement || s).slice(0, 80),
    isDecorative: s.getAttribute('aria-hidden') === 'true' || s.getAttribute('role') === 'presentation',
  }));

  const figures = [...document.querySelectorAll('figure')].map((f) => ({
    hasCaption: !!f.querySelector('figcaption'),
    captionText: textOf(f.querySelector('figcaption') || '').slice(0, 80),
    imgHasAlt: hasAltText(f.querySelector('img,svg,canvas,object,embed,input[type=image]') || f),
  }));

  return {
    url: location.href,
    counts: {
      imgs: imgs.length,
      infoImgs: infoImgs.length,
      decImgs: decImgs.length,
      areas: areas.length,
      inputImages: inputImages.length,
      ismap: ismapImgs.length,
      svgs: svgs.length,
      objects: objects.length,
      embeds: embeds.length,
      canvases: canvases.length,
      captcha: captchaImgs.length,
      figures: figures.length,
    },
    infoImgsNoAlt: infoImgs.filter((el) => !hasAltText(el)).map((el) => mapEl(el)),
    decImgsBad: decImgs.filter((el) => {
      if (el.getAttribute('role') === 'presentation' || el.getAttribute('aria-hidden') === 'true') return false;
      if (el.tagName === 'IMG' && el.getAttribute('alt') === '') return false;
      return true;
    }).map((el) => mapEl(el)),
    areas: areas.map((a) => mapEl(a, { href: a.getAttribute('href') })),
    inputImages: inputImages.map((i) => mapEl(i)),
    ismapImgs: ismapImgs.map((i) => mapEl(i)),
    svgs: svgDetails,
    objects: objects.map((o) => mapEl(o)),
    embeds: embeds.map((e) => mapEl(e)),
    canvases: canvases.map((c) => mapEl(c)),
    captchaImgs: captchaImgs.map((el) => mapEl(el)),
    figures,
    textImages: imgs.filter(isTextImage).map((el) => mapEl(el)),
  };
}