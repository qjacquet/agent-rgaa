/**
 * Compact theme 2+3+4 collect for batch audit.
 */
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const parseRgb = (c) => { const m = c.match(/[\d.]+/g); return m && m.length >= 3 ? m.slice(0, 3).map(Number) : null; };
  const lum = ([r, g, b]) => { const a = [r, g, b].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]; };
  const ratio = (fg, bg) => { const L1 = lum(fg); const L2 = lum(bg); return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05); };
  const bgOf = (el) => { let n = el; while (n && n !== document.documentElement) { const bg = parseRgb(getComputedStyle(n).backgroundColor); if (bg && bg.some((x) => x > 0) && getComputedStyle(n).backgroundColor !== 'rgba(0, 0, 0, 0)') return { rgb: bg }; n = n.parentElement; } return { rgb: parseRgb(getComputedStyle(document.body).backgroundColor) }; };
  const isBold = (el) => { const w = getComputedStyle(el).fontWeight; return w === 'bold' || parseInt(w, 10) >= 700; };
  const genericTitles = /^(frame|iframe|cadre|blank|untitled|sans titre|widget|content|embed)$/i;
  const frames = [...document.querySelectorAll('iframe,frame')].map((f) => ({ tag: f.tagName.toLowerCase(), title: f.getAttribute('title'), src: (f.src || '').slice(0, 120), visible: visible(f), hasTitle: f.hasAttribute('title') && (f.getAttribute('title') || '').trim().length > 0, titleGeneric: genericTitles.test((f.getAttribute('title') || '').trim()) }));
  const visibleFrames = frames.filter((f) => f.visible);
  const hasNonColorCue = (el) => { const s = getComputedStyle(el); return s.textDecoration?.includes('underline') || parseInt(s.fontWeight, 10) >= 700 || s.fontStyle === 'italic' || !!el.querySelector('svg,img') || !!el.getAttribute('title'); };
  let colorOnlyCount = 0; const colorOnlyCandidates = [];
  for (const el of [...document.querySelectorAll('span,p,a,li,label,strong,em')].filter(visible)) {
    const text = textOf(el); if (!text || text.length < 2 || el.children.length > 3) continue;
    const color = getComputedStyle(el).color; const parent = el.parentElement; if (!parent) continue;
    if (color !== getComputedStyle(parent).color && !hasNonColorCue(el)) { colorOnlyCount++; if (colorOnlyCandidates.length < 5) colorOnlyCandidates.push({ tag: el.tagName, text: text.slice(0, 50) }); }
  }
  const contrastByCategory = { smallNormal: [], smallBold: [], largeNormal: [], largeBold: [] };
  let checked = 0;
  for (const el of [...document.querySelectorAll('p,span,a,button,h1,h2,h3,h4,h5,h6,label,li,input')].filter(visible)) {
    const text = textOf(el); if (!text || text.length < 2) continue;
    const fg = parseRgb(getComputedStyle(el).color); const bg = bgOf(el).rgb; if (!fg || !bg) continue;
    const r = ratio(fg, bg); checked++; const fs = parseFloat(getComputedStyle(el).fontSize); const bold = isBold(el);
    const large = fs >= 24 || (fs >= 18.5 && bold); const min = large ? 3 : 4.5;
    const entry = { tag: el.tagName, text: text.slice(0, 50), ratio: Math.round(r * 100) / 100, min, fs, bold };
    if (r < min) { if (large && bold) contrastByCategory.largeBold.push(entry); else if (large) contrastByCategory.largeNormal.push(entry); else if (bold) contrastByCategory.smallBold.push(entry); else contrastByCategory.smallNormal.push(entry); }
  }
  for (const k of Object.keys(contrastByCategory)) contrastByCategory[k] = contrastByCategory[k].slice(0, 20);
  const hcMechanism = [...document.querySelectorAll('a,button')].filter(visible).filter((el) => /contraste|high contrast|mode contrast/i.test(textOf(el) + ' ' + (el.getAttribute('href') || ''))).map((el) => textOf(el).slice(0, 80));
  const uiContrastFails = [];
  for (const el of [...document.querySelectorAll('input,button,a[href]')].filter(visible).slice(0, 40)) {
    const borderRgb = parseRgb(getComputedStyle(el).borderColor); const bg = bgOf(el).rgb; const fg = parseRgb(getComputedStyle(el).color);
    if (borderRgb && bg && ratio(borderRgb, bg) < 3) uiContrastFails.push({ tag: el.tagName, name: textOf(el).slice(0, 40), ratio: Math.round(ratio(borderRgb, bg) * 100) / 100, type: 'border' });
    if (fg && bg && textOf(el) && ratio(fg, bg) < 3) uiContrastFails.push({ tag: el.tagName, name: textOf(el).slice(0, 40), ratio: Math.round(ratio(fg, bg) * 100) / 100, type: 'text' });
  }
  const mapMedia = (el) => ({ tag: el.tagName.toLowerCase(), src: (el.src || el.currentSrc || el.getAttribute('src') || '').slice(0, 120), hasControls: !!(el.controls || el.hasAttribute?.('controls')), muted: !!el.muted, autoplay: !!(el.autoplay || el.hasAttribute?.('autoplay')), tracks: [...(el.querySelectorAll?.('track') || [])].map((t) => ({ kind: t.getAttribute('kind') })), hasAudio: el.tagName === 'AUDIO' || (el.tagName === 'VIDEO' && !el.hasAttribute?.('muted')), hasVideo: el.tagName === 'VIDEO', transcriptNear: false, linkNear: false });
  const audios = [...document.querySelectorAll('audio')].filter(visible).map(mapMedia);
  const videos = [...document.querySelectorAll('video')].filter(visible).map(mapMedia);
  const mediaIframes = [...document.querySelectorAll('iframe')].filter(visible).filter((f) => /youtube|vimeo|dailymotion|player|video|audio|soundcloud/i.test(f.src || '')).map((f) => ({ tag: 'iframe', src: (f.src || '').slice(0, 120), title: f.getAttribute('title'), hasControls: true, muted: false, autoplay: false, tracks: [], hasAudio: true, hasVideo: true, transcriptNear: false, linkNear: false }));
  const all = [...audios, ...videos, ...mediaIframes];
  return {
    theme2: { url: location.href, counts: { total: frames.length, visible: visibleFrames.length }, visibleFrames, noTitle: visibleFrames.filter((f) => !f.hasTitle), genericTitle: visibleFrames.filter((f) => f.hasTitle && f.titleGeneric) },
    theme3: { url: location.href, colorOnlyCount, colorOnlyCandidates, contrastChecked: checked, contrastByCategory, hcMechanism, uiContrastFails: uiContrastFails.slice(0, 20), media: { videos: videos.length, audios: audios.length, objects: 0 } },
    theme4: { url: location.href, counts: { total: all.length, audio: audios.length, video: videos.length, object: 0, iframe: mediaIframes.length }, audios, videos, objects: [], mediaIframes, all, audioOnly: audios, videoOnly: videos.filter((m) => !m.hasAudio || m.muted), synced: videos.filter((m) => m.hasAudio && m.hasVideo && !m.muted).concat(mediaIframes), autoplayMedia: all.filter((m) => m.autoplay), noControls: all.filter((m) => !m.hasControls && m.tag !== 'iframe') },
  };
}
