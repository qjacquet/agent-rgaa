(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
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
  const genericLink = /^(cliquez ici|cliquer ici|ici|lire la suite|en savoir plus|plus d['']infos|plus d'informations|d[ée]couvrir|voir plus|suite|link|click here|read more|learn more)$/i;
  const validLang = (c) => /^[a-z]{2,3}(-[A-Za-z]{2,8})*$/.test((c || '').trim());

  const mapTable = (t) => {
    const ths = [...t.querySelectorAll('th')];
    const tds = [...t.querySelectorAll('td')];
    const caption = t.querySelector('caption');
    const role = t.getAttribute('role');
    const isPresentation = role === 'presentation' || role === 'none';
    const thDetails = ths.map((th) => ({ scope: th.getAttribute('scope'), id: th.id || null, role: th.getAttribute('role'), headers: th.getAttribute('headers'), text: textOf(th).slice(0, 60) }));
    const isDataTable = ((ths.length > 0) || role === 'table') && !isPresentation;
    const isLayoutTable = !isDataTable && t.tagName === 'TABLE';
    const thPartial = ths.filter((th) => th.getAttribute('headers') || (th.id && ths.some((o) => o !== th && o.getAttribute('headers')?.includes(th.id))));
    const isComplex = isDataTable && (ths.some((th) => { const row = th.closest('tr'); const rowIdx = row ? [...row.parentElement.children].indexOf(row) : -1; return rowIdx > 0 && th.getAttribute('scope') !== 'col'; }) || thPartial.length > 0);
    const describedby = t.getAttribute('aria-describedby');
    const hasSummary = !!(caption?.textContent?.trim() || t.getAttribute('summary')?.trim() || (describedby && textOf(document.getElementById(describedby))));
    const thNoScopeNoId = ths.filter((th) => !th.getAttribute('scope') && !th.id && !['rowheader', 'columnheader'].includes(th.getAttribute('role') || ''));
    return {
      isDataTable, isLayoutTable, isPresentation, isComplex, hasSummary, hasCaption: !!caption, captionText: textOf(caption).slice(0, 80),
      thDetails, thNoScopeNoId, thPartial,
      layoutViolations: isLayoutTable ? {
        summary: !!t.getAttribute('summary'), caption: !!caption, thead: !!t.querySelector('thead'), th: ths.length > 0, tfoot: !!t.querySelector('tfoot'),
        tdScope: tds.some((td) => td.hasAttribute('scope')), tdHeaders: tds.some((td) => td.hasAttribute('headers')), tdAxis: tds.some((td) => td.hasAttribute('axis')),
        rowheader: !!t.querySelector('[role=rowheader],[role=columnheader]'),
      } : null,
      titleAttr: t.getAttribute('title'), ariaLabel: t.getAttribute('aria-label'), ariaLabelledby: t.getAttribute('aria-labelledby'),
    };
  };

  const tables = [...document.querySelectorAll('table,[role=table]')].filter(visible).map(mapTable);
  const dataTables = tables.filter((t) => t.isDataTable);
  const layoutTables = tables.filter((t) => t.isLayoutTable);
  const complexTables = dataTables.filter((t) => t.isComplex);

  const mapLink = (a) => {
    const imgs = [...a.querySelectorAll('img,[role=img],svg,object,canvas,area')];
    const text = textOf(a);
    const visibleText = [...a.childNodes].filter((n) => n.nodeType === 3 || (n.nodeType === 1 && !['IMG', 'SVG', 'OBJECT', 'CANVAS'].includes(n.tagName))).map(textOf).join(' ').trim();
    const isImageLink = imgs.length > 0 && !visibleText;
    const isComposite = imgs.length > 0 && !!visibleText;
    const isSvgLink = !!(a.querySelector('svg') && !visibleText);
    const name = accName(a);
    const ctx = textOf(a.closest('li,td,th,p,h1,h2,h3,h4,h5,h6,figcaption,label') || a.parentElement).slice(0, 120);
    const generic = genericLink.test(text.trim()) || genericLink.test(name.trim());
    return {
      text: text.slice(0, 80), visibleText: visibleText.slice(0, 80), name: name.slice(0, 80),
      isTextLink: !isImageLink && !isComposite && !isSvgLink, isImageLink, isComposite, isSvgLink,
      generic, hasContext: generic && ctx.length > text.length + 5, empty: !text && !name && !a.getAttribute('title'),
      hasBothVisibleAndAria: !!(visibleText && (a.getAttribute('aria-label') || a.getAttribute('title') || a.getAttribute('aria-labelledby'))),
      ariaMismatch: !!(visibleText && (a.getAttribute('aria-label') || a.getAttribute('title')) && !accName(a).toLowerCase().includes(visibleText.toLowerCase().slice(0, Math.min(visibleText.length, 20)))),
      hasImgWithoutAlt: imgs.some((i) => !accName(i) && i.tagName !== 'SVG'),
    };
  };

  const links = [...document.querySelectorAll('a[href],[role=link]')].filter(visible).map(mapLink);
  const svgLinks = [...document.querySelectorAll('svg a[href], svg [href]')].filter((el) => visible(el.closest('svg') || el)).map((el) => ({ text: textOf(el), svgLabel: accName(el.closest('svg') || el) }));

  const clickOnly = [...document.querySelectorAll('[onclick],[onmousedown],[onmouseup]')].filter(visible).filter((el) => !['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName) && el.getAttribute('role') !== 'button' && el.getAttribute('role') !== 'link' && el.tabIndex < 0).map((el) => ({ tag: el.tagName, name: accName(el).slice(0, 60) }));
  const scriptWidgets = [...document.querySelectorAll('[role=button],[role=link],[role=tab],[role=menuitem],[role=checkbox],[role=radio],[role=switch],[role=combobox],[role=listbox]')].filter(visible).map((el) => ({ tag: el.tagName, role: el.getAttribute('role'), name: accName(el).slice(0, 80), visibleText: textOf(el).slice(0, 60), ariaMismatch: !!(textOf(el) && el.getAttribute('aria-label') && !accName(el).toLowerCase().includes(textOf(el).toLowerCase().slice(0, 15))) }));
  const statusMsgs = [...document.querySelectorAll('[role=status],[role=alert],[role=log],[role=progressbar],[aria-live]')].filter(visible).map((el) => ({ role: el.getAttribute('role'), live: el.getAttribute('aria-live'), atomic: el.getAttribute('aria-atomic'), text: textOf(el).slice(0, 80) }));
  const selectOnChange = [...document.querySelectorAll('select')].filter((s) => s.getAttribute('onchange') || s.onchange).map((s) => ({ name: s.name || s.id, hasSubmitNearby: !!(s.closest('form')?.querySelector('button[type=submit],input[type=submit]')) }));
  const noscriptCount = document.querySelectorAll('noscript').length;

  const html = document.documentElement;
  const ids = [...document.querySelectorAll('[id]')].map((el) => el.id).filter(Boolean);
  const idCounts = {};
  ids.forEach((id) => { idCounts[id] = (idCounts[id] || 0) + 1; });
  const duplicateIds = Object.entries(idCounts).filter(([, c]) => c > 1).map(([id, c]) => ({ id, count: c }));
  const langChanges = [...document.querySelectorAll('[lang],[xml\\:lang]')].filter((el) => el !== html).map((el) => ({ tag: el.tagName, lang: el.getAttribute('lang') || el.getAttribute('xml:lang'), valid: validLang(el.getAttribute('lang') || el.getAttribute('xml:lang')) }));
  const rtlBlocks = [...document.querySelectorAll('[dir=rtl],[dir=ltr]')].map((el) => ({ tag: el.tagName, dir: el.getAttribute('dir') }));
  const presentationMisuse = [...document.querySelectorAll('blockquote,cite,address,dl,ul,ol,hr,pre,em,strong,abbr,q,s,del,ins,sub,sup,small,big,code,var,samp,kbd,dfn')].filter(visible).filter((el) => getComputedStyle(el).fontStyle === 'normal' && getComputedStyle(el).fontWeight === 'normal' && !el.querySelector('li,dt,dd') && textOf(el).length < 3).slice(0, 20).map((el) => ({ tag: el.tagName, role: el.getAttribute('role') }));

  return {
    url: location.href,
    theme5: { counts: { total: tables.length, data: dataTables.length, layout: layoutTables.length, complex: complexTables.length }, tables, dataTables, layoutTables, complexTables },
    theme6: { counts: { total: links.length, text: links.filter((l) => l.isTextLink).length, image: links.filter((l) => l.isImageLink).length, composite: links.filter((l) => l.isComposite).length, svg: svgLinks.length }, links, svgLinks },
    theme7: { clickOnly, scriptWidgets, statusMsgs, selectOnChange, noscriptCount, hasNoscript: noscriptCount > 0 },
    theme8: {
      doctype: document.doctype ? `<!DOCTYPE ${document.doctype.name}>` : null, doctypeName: document.doctype?.name || null,
      lang: html.getAttribute('lang') || '', pageTitle: document.title?.trim() || '', duplicateIds, duplicateIdCount: duplicateIds.length,
      langChanges, rtlBlocks, presentationMisuse, hasTitle: !!document.title?.trim(), validDefaultLang: validLang(html.getAttribute('lang') || ''),
    },
  };
})()
