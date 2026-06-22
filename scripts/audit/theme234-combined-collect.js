(() => {
const theme2 = (/**
 * Theme 2 Cadres — CDP collect (iframe/frame titles).
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const genericTitles = /^(frame|iframe|cadre|blank|untitled|sans titre|widget|content|embed)$/i;
  const frames = [...document.querySelectorAll('iframe,frame')].map((f) => ({
    tag: f.tagName.toLowerCase(),
    title: f.getAttribute('title'),
    name: f.getAttribute('name'),
    src: (f.src || f.getAttribute('src') || '').slice(0, 120),
    visible: visible(f),
    hasTitle: f.hasAttribute('title') && (f.getAttribute('title') || '').trim().length > 0,
    titleGeneric: genericTitles.test((f.getAttribute('title') || '').trim()),
    ariaLabel: f.getAttribute('aria-label'),
  }));
  const visibleFrames = frames.filter((f) => f.visible);
  const hiddenFrames = frames.filter((f) => !f.visible);
  return {
    url: location.href,
    counts: { total: frames.length, visible: visibleFrames.length, hidden: hiddenFrames.length },
    frames,
    visibleFrames,
    noTitle: visibleFrames.filter((f) => !f.hasTitle),
    genericTitle: visibleFrames.filter((f) => f.hasTitle && f.titleGeneric),
  };
})();
const theme3 = (/**
 * Theme 3 Couleurs — CDP collect (color-only info + contrast).
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
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
  const isBold = (el) => {
    const w = getComputedStyle(el).fontWeight;
    return w === 'bold' || parseInt(w, 10) >= 700;
  };
  const fontSizePx = (el) => parseFloat(getComputedStyle(el).fontSize);

  const hasNonColorCue = (el) => {
    const s = getComputedStyle(el);
    if (s.textDecorationLine?.includes('underline') || s.textDecoration?.includes('underline')) return true;
    if (parseInt(s.fontWeight, 10) >= 700 || s.fontWeight === 'bold') return true;
    if (s.fontStyle === 'italic') return true;
    if (el.querySelector('svg,img,[class*="icon"],[class*="Icon"]')) return true;
    if (el.getAttribute('title') || el.getAttribute('aria-label')) return true;
    if (el.closest('[aria-invalid="true"]')?.querySelector('[role="alert"],.error,.invalid,.is-invalid')) return true;
    const parent = el.parentElement;
    if (parent && textOf(parent) !== textOf(el)) {
      const sib = [...parent.children].filter((c) => c !== el && visible(c));
      if (sib.some((c) => c.querySelector('svg,img') || /[*!⚠]/.test(textOf(c)))) return true;
    }
    return false;
  };

  const coloredTextCandidates = [];
  for (const el of [...document.querySelectorAll('span,p,a,li,td,th,label,strong,em,div')].filter(visible)) {
    const text = textOf(el);
    if (!text || text.length < 2 || el.children.length > 3) continue;
    const color = getComputedStyle(el).color;
    const parent = el.parentElement;
    if (!parent) continue;
    const parentColor = getComputedStyle(parent).color;
    if (color !== parentColor && !hasNonColorCue(el)) {
      coloredTextCandidates.push({ tag: el.tagName, text: text.slice(0, 60), color, parentColor });
    }
  }

  const selectors = 'p,span,a,button,h1,h2,h3,h4,h5,h6,label,li,td,th,input,textarea';
  const contrastByCategory = { smallNormal: [], smallBold: [], largeNormal: [], largeBold: [] };
  let checked = 0;
  for (const el of [...document.querySelectorAll(selectors)].filter(visible)) {
    const text = textOf(el);
    if (!text || text.length < 2) continue;
    const fg = parseRgb(getComputedStyle(el).color);
    const bgInfo = bgOf(el);
    if (!fg || !bgInfo.rgb) continue;
    const r = ratio(fg, bgInfo.rgb);
    checked++;
    const fs = fontSizePx(el);
    const bold = isBold(el);
    const large = fs >= 24 || (fs >= 18.5 && bold);
    const min = large ? 3 : 4.5;
    const entry = { tag: el.tagName, text: text.slice(0, 50), ratio: Math.round(r * 100) / 100, min, fs, bold };
    if (large && bold) contrastByCategory.largeBold.push(entry);
    else if (large) contrastByCategory.largeNormal.push(entry);
    else if (bold) contrastByCategory.smallBold.push(entry);
    else contrastByCategory.smallNormal.push(entry);
  }
  for (const k of Object.keys(contrastByCategory)) {
    contrastByCategory[k] = contrastByCategory[k].filter((e) => e.ratio < e.min).slice(0, 20);
  }

  const hcMechanism = [...document.querySelectorAll('a,button,[role=button]')].filter(visible).filter((el) =>
    /contraste|accessibilit|high contrast|mode contrast/i.test(textOf(el) + ' ' + (el.getAttribute('href') || '')),
  );

  const uiComponents = [...document.querySelectorAll('input,select,textarea,button,a[href],[role=button],[role=link],[role=checkbox],[role=radio],[role=tab]')].filter(visible);
  const uiContrastFails = [];
  for (const el of uiComponents.slice(0, 80)) {
    const border = getComputedStyle(el).borderColor;
    const bg = bgOf(el).rgb;
    const fg = parseRgb(getComputedStyle(el).color);
    const borderRgb = parseRgb(border);
    if (borderRgb && bg) {
      const br = ratio(borderRgb, bg);
      if (br < 3) uiContrastFails.push({ tag: el.tagName, name: textOf(el).slice(0, 40), ratio: Math.round(br * 100) / 100, type: 'border' });
    }
    if (fg && bg) {
      const cr = ratio(fg, bg);
      if (cr < 3 && textOf(el).length > 0) uiContrastFails.push({ tag: el.tagName, name: textOf(el).slice(0, 40), ratio: Math.round(cr * 100) / 100, type: 'text' });
    }
  }

  const videos = [...document.querySelectorAll('video')].filter(visible);
  const audios = [...document.querySelectorAll('audio')].filter(visible);
  const objects = [...document.querySelectorAll('object,embed')].filter(visible);

  return {
    url: location.href,
    colorOnlyCandidates: coloredTextCandidates.slice(0, 30),
    colorOnlyCount: coloredTextCandidates.length,
    contrastChecked: checked,
    contrastByCategory,
    hcMechanism: hcMechanism.map((el) => textOf(el).slice(0, 80)),
    uiContrastFails: uiContrastFails.slice(0, 20),
    media: { videos: videos.length, audios: audios.length, objects: objects.length },
  };
})();
const theme4 = (/**
 * Theme 4 Multimédia — CDP collect.
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const nearText = (el, re) => {
    const block = el.closest('section,article,div,figure') || el.parentElement;
    return re.test(textOf(block || el));
  };

  const mapMedia = (el) => {
    const tag = el.tagName.toLowerCase();
    const tracks = [...el.querySelectorAll?.('track') || []].map((t) => ({
      kind: t.getAttribute('kind'), src: (t.src || '').slice(-60), label: t.getAttribute('label'),
    }));
    const hasControls = el.hasAttribute?.('controls') || el.controls;
    const muted = el.muted;
    const autoplay = el.autoplay || el.hasAttribute?.('autoplay');
    const src = (el.src || el.currentSrc || el.getAttribute('src') || '').slice(0, 120);
    const type = el.getAttribute?.('type') || '';
    const hasAudio = tag === 'audio' || (tag === 'video' && !el.hasAttribute?.('muted'));
    const hasVideo = tag === 'video' || /^video\//i.test(type);
    const transcriptNear = nearText(el, /transcription|transcript|sous-titre|subtitle|audiodescription|audio-description/i);
    const linkNear = [...(el.closest('div,section,figure')?.querySelectorAll('a,button') || [])].some((a) =>
      /transcription|transcript|sous-titre|subtitle|audiodescription|version alternative|audio seulement/i.test(textOf(a)),
    );
    return {
      tag, src, type, hasControls, muted, autoplay, tracks, hasAudio, hasVideo,
      transcriptNear, linkNear, ariaLabel: el.getAttribute?.('aria-label'),
    };
  };

  const audios = [...document.querySelectorAll('audio')].filter(visible).map(mapMedia);
  const videos = [...document.querySelectorAll('video')].filter(visible).map(mapMedia);
  const objects = [...document.querySelectorAll('object[type^="video"],object[type^="audio"],embed[type^="video"],embed[type^="audio"]')].filter(visible).map(mapMedia);
  const mediaIframes = [...document.querySelectorAll('iframe')].filter(visible).filter((f) =>
    /youtube|vimeo|dailymotion|player|video|audio|soundcloud/i.test(f.src || ''),
  ).map((f) => ({ tag: 'iframe', src: (f.src || '').slice(0, 120), title: f.getAttribute('title') }));

  const all = [...audios, ...videos, ...objects, ...mediaIframes];
  const audioOnly = audios.filter((m) => m.tag === 'audio');
  const videoOnly = videos.filter((m) => !m.hasAudio || m.muted);
  const synced = videos.filter((m) => m.hasAudio && m.hasVideo && !m.muted);

  return {
    url: location.href,
    counts: { total: all.length, audio: audios.length, video: videos.length, object: objects.length, iframe: mediaIframes.length },
    audios, videos, objects, mediaIframes, all,
    audioOnly, videoOnly, synced,
    autoplayMedia: all.filter((m) => m.autoplay),
    noControls: all.filter((m) => !m.hasControls && m.tag !== 'iframe'),
  };
})();
return { theme2, theme3, theme4 };
})()