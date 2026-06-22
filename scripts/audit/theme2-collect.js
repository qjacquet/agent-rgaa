/**
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
}
