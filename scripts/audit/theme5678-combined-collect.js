(() => {
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

  // --- Theme 5: Tables ---
  const mapTable = (t) => {
    const ths = [...t.querySelectorAll('th')];
    const tds = [...t.querySelectorAll('td')];
    const caption = t.querySelector('caption');
    const describedby = t.getAttribute('aria-describedby');
    const summary = t.getAttribute('summary');
    const role = t.getAttribute('role');
    const isPresentation = role === 'presentation' || role === 'none';
    const hasTh = ths.length > 0;
    const hasThead = !!t.querySelector('thead');
    const hasTfoot = !!t.querySelector('tfoot');
    const rowHeaders = ths.filter((th) => th.getAttribute('scope') === 'row' || th.closest('tbody,tfoot') || (th.parentElement && th.parentElement.querySelector('td')));
    const colHeaders = ths.filter((th) => th.getAttribute('scope') === 'col' || (!th.getAttribute('scope') && th.closest('thead, tr:first-child')));
    const thDetails = ths.map((th) => ({
      scope: th.getAttribute('scope'), id: th.id || null, role: th.getAttribute('role'),
      headers: th.getAttribute('headers'), text: textOf(th).slice(0, 60),
    }));
    const tdDetails = tds.map((td) => ({
      headers: td.getAttribute('headers'), scope: td.getAttribute('scope'), axis: td.getAttribute('axis'),
    }));
    const isDataTable = (hasTh || role === 'table') && !isPresentation;
    const isLayoutTable = !isDataTable && t.tagName === 'TABLE';
    const multiScopeTh = ths.filter((th) => {
      const sc = th.getAttribute('scope');
      return sc && !['row', 'col', 'rowgroup', 'colgroup'].includes(sc);
    });
    const thNoScopeNoId = ths.filter((th) => !th.getAttribute('scope') && !th.id && !['rowheader', 'columnheader'].includes(th.getAttribute('role') || ''));
    const thWithBadScope = ths.filter((th) => {
      const sc = th.getAttribute('scope');
      return sc && !['row', 'col'].includes(sc);
    });
    const thPartial = ths.filter((th) => th.getAttribute('headers') || (th.id && ths.some((o) => o !== th && o.getAttribute('headers')?.includes(th.id))));
    const cellsNeedHeaders = [...t.querySelectorAll('td,th')].filter((c) => {
      const ids = (c.getAttribute('headers') || '').split(/\s+/).filter(Boolean);
      return ths.some((h) => h.id) && ths.some((h) => h.id && !ids.includes(h.id)) && c.tagName === 'TD' && thPartial.length;
    });
    const isComplex = isDataTable && (
      ths.some((th, i) => {
        const row = th.closest('tr');
        const rowIdx = row ? [...row.parentElement.children].indexOf(row) : -1;
        return rowIdx > 0 && th.getAttribute('scope') !== 'col';
      }) || thPartial.length > 0 || multiScopeTh.length > 0
    );
    const hasSummary = !!(caption?.textContent?.trim() || summary?.trim() || (describedby && textOf(document.getElementById(describedby))));
    return {
      isDataTable, isLayoutTable, isPresentation, isComplex, hasSummary,
      hasCaption: !!caption, captionText: textOf(caption).slice(0, 80),
      summary, describedby, hasThead, hasTfoot, hasTh, thCount: ths.length, tdCount: tds.length,
      thDetails, tdDetails, thNoScopeNoId, thWithBadScope, thPartial,
      layoutViolations: isLayoutTable ? {
        summary: !!summary, caption: !!caption, thead: hasThead, th: hasTh, tfoot: hasTfoot,
        tdScope: tds.some((td) => td.hasAttribute('scope')),
        tdHeaders: tds.some((td) => td.hasAttribute('headers')),
        tdAxis: tds.some((td) => td.hasAttribute('axis')),
        rowheader: !!t.querySelector('[role=rowheader],[role=columnheader]'),
      } : null,
      titleAttr: t.getAttribute('title'), ariaLabel: t.getAttribute('aria-label'), ariaLabelledby: t.getAttribute('aria-labelledby'),
    };
  };

  const tables = [...document.querySelectorAll('table,[role=table]')].filter(visible).map(mapTable);
  const dataTables = tables.filter((t) => t.isDataTable);
  const layoutTables = tables.filter((t) => t.isLayoutTable);
  const complexTables = dataTables.filter((t) => t.isComplex);

  // --- Theme 6: Links ---
  const mapLink = (a) => {
    const imgs = [...a.querySelectorAll('img,[role=img],svg,object,canvas,area')];
    const text = textOf(a);
    const visibleText = [...a.childNodes].filter((n) => n.nodeType === 3 || (n.nodeType === 1 && !['IMG', 'SVG', 'OBJECT', 'CANVAS'].includes(n.tagName))).map(textOf).join(' ').trim();
    const imgAlts = imgs.map((i) => i.getAttribute('alt') || i.getAttribute('aria-label') || textOf(i)).filter(Boolean);
    const isImageLink = imgs.length > 0 && !visibleText;
    const isComposite = imgs.length > 0 && !!visibleText;
    const isSvgLink = a.querySelector('svg a[href], svg [href], svg [xlink\\:href]') || (a.tagName === 'A' && a.querySelector('svg') && !visibleText);
    const isTextLink = !isImageLink && !isComposite && !isSvgLink;
    const name = accName(a);
    const ctx = textOf(a.closest('li,td,th,p,h1,h2,h3,h4,h5,h6,figcaption,label') || a.parentElement).slice(0, 120);
    const generic = genericLink.test(text.trim()) || genericLink.test(name.trim());
    const hasContext = generic && ctx.length > text.length + 5;
    const empty = !text && !name && !a.getAttribute('title');
    const hasBothVisibleAndAria = !!(visibleText && (a.getAttribute('aria-label') || a.getAttribute('title') || a.getAttribute('aria-labelledby')));
    const ariaMismatch = hasBothVisibleAndAria && !(name.toLowerCase().includes(visibleText.toLowerCase().slice(0, Math.min(visibleText.length, 20))));
    return {
      href: (a.href || a.getAttribute('href') || '').slice(0, 120), text: text.slice(0, 80), visibleText: visibleText.slice(0, 80),
      name: name.slice(0, 80), isTextLink, isImageLink, isComposite, isSvgLink, generic, hasContext, empty, ariaMismatch,
      imgAlts, hasImgWithoutAlt: imgs.some((i) => !accName(i) && i.tagName !== 'SVG'),
      target: a.getAttribute('target'),
    };
  };

  const links = [...document.querySelectorAll('a[href],[role=link]')].filter(visible).map(mapLink);
  const svgLinks = [...document.querySelectorAll('svg a[href], svg [href]')].filter((el) => visible(el.closest('svg') || el)).map((el) => ({
    text: textOf(el), href: el.getAttribute('href') || el.getAttribute('xlink:href'),
    svgLabel: accName(el.closest('svg') || el),
  }));

  // --- Theme 7: Scripts ---
  const clickOnly = [...document.querySelectorAll('[onclick],[onmousedown],[onmouseup]')].filter(visible).filter((el) => {
    const tag = el.tagName;
    if (['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(tag)) return false;
    if (el.getAttribute('role') === 'button' || el.getAttribute('role') === 'link') return false;
    if (el.tabIndex >= 0) return false;
    return true;
  }).map((el) => ({ tag: el.tagName, role: el.getAttribute('role'), tabindex: el.tabIndex, name: accName(el).slice(0, 60) }));

  const scriptWidgets = [...document.querySelectorAll('[role=button],[role=link],[role=tab],[role=menuitem],[role=checkbox],[role=radio],[role=switch],[role=combobox],[role=listbox],[role=slider],[role=spinbutton]')].filter(visible).map((el) => ({
    tag: el.tagName, role: el.getAttribute('role'), name: accName(el).slice(0, 80),
    tabindex: el.tabIndex, hasKeyboard: el.tabIndex >= 0 || ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName),
    visibleText: textOf(el).slice(0, 60), ariaMismatch: !!(textOf(el) && el.getAttribute('aria-label') && !accName(el).toLowerCase().includes(textOf(el).toLowerCase().slice(0, 15))),
  }));

  const statusMsgs = [...document.querySelectorAll('[role=status],[role=alert],[role=log],[role=progressbar],[aria-live]')].filter(visible).map((el) => ({
    role: el.getAttribute('role'), live: el.getAttribute('aria-live'), atomic: el.getAttribute('aria-atomic'),
    text: textOf(el).slice(0, 80),
  }));

  const selectOnChange = [...document.querySelectorAll('select')].filter((s) => s.getAttribute('onchange') || s.onchange).map((s) => ({
    name: s.name || s.id, hasSubmitNearby: !!(s.closest('form')?.querySelector('button[type=submit],input[type=submit]')),
  }));

  const noscript = [...document.querySelectorAll('noscript')].map((n) => textOf(n).slice(0, 120));

  // --- Theme 8: Mandatory elements ---
  const html = document.documentElement;
  const doctype = document.doctype ? `<!DOCTYPE ${document.doctype.name}${document.doctype.publicId ? ' PUBLIC "' + document.doctype.publicId + '"' : ''}>` : null;
  const ids = [...document.querySelectorAll('[id]')].map((el) => el.id).filter(Boolean);
  const idCounts = {};
  ids.forEach((id) => { idCounts[id] = (idCounts[id] || 0) + 1; });
  const duplicateIds = Object.entries(idCounts).filter(([, c]) => c > 1).map(([id, c]) => ({ id, count: c }));

  const presentationMisuse = [...document.querySelectorAll('blockquote,cite,address,dl,ul,ol,hr,pre,em,strong,abbr,q,s,del,ins,sub,sup,small,big,code,var,samp,kbd,dfn')].filter(visible).filter((el) => {
    const s = getComputedStyle(el);
    return s.fontStyle === 'normal' && s.fontWeight === 'normal' && !el.querySelector('li,dt,dd') && textOf(el).length < 3;
  }).slice(0, 20).map((el) => ({ tag: el.tagName, role: el.getAttribute('role'), text: textOf(el).slice(0, 40) }));

  const langChanges = [...document.querySelectorAll('[lang],[xml\\:lang]')].filter((el) => el !== html).map((el) => ({
    tag: el.tagName, lang: el.getAttribute('lang') || el.getAttribute('xml:lang'), text: textOf(el).slice(0, 60),
    valid: validLang(el.getAttribute('lang') || el.getAttribute('xml:lang')),
  }));

  const rtlBlocks = [...document.querySelectorAll('[dir=rtl],[dir=ltr]')].map((el) => ({
    tag: el.tagName, dir: el.getAttribute('dir'), text: textOf(el).slice(0, 60),
  }));

  const pageTitle = document.title?.trim() || '';
  const defaultLang = html.getAttribute('lang') || html.getAttribute('xml:lang') || '';

  return {
    url: location.href,
    theme5: {
      counts: { total: tables.length, data: dataTables.length, layout: layoutTables.length, complex: complexTables.length },
      tables, dataTables, layoutTables, complexTables,
    },
    theme6: {
      counts: { total: links.length, text: links.filter((l) => l.isTextLink).length, image: links.filter((l) => l.isImageLink).length, composite: links.filter((l) => l.isComposite).length, svg: svgLinks.length },
      links, svgLinks,
    },
    theme7: {
      clickOnly, scriptWidgets, statusMsgs, selectOnChange, noscriptCount: noscript.length,
      hasNoscript: noscript.length > 0,
    },
    theme8: {
      doctype, doctypeName: document.doctype?.name || null,
      lang: defaultLang, xmlLang: html.getAttribute('xml:lang'),
      charset: document.characterSet, pageTitle,
      duplicateIds, duplicateIdCount: duplicateIds.length,
      langChanges, rtlBlocks, presentationMisuse,
      hasTitle: !!pageTitle, validDefaultLang: validLang(defaultLang),
    },
  };
})()
