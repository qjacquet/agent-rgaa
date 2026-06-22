/**
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
}
