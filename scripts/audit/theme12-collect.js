(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = el => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const acc = el => el.getAttribute('aria-label')||el.getAttribute('title')||t(el);
  const navEls=[...document.querySelectorAll('nav,[role=navigation]')];
  const skipLink=[...document.querySelectorAll('a[href^="#"]')].find(a=>/aller au contenu|skip to|accès rapide|contenu principal/i.test(t(a)+(a.getAttribute('aria-label')||'')));
  const sitemapLinks=[...document.querySelectorAll('a[href]')].filter(a=>/plan du site|sitemap/i.test(t(a)+(a.getAttribute('aria-label')||''))).map(a=>({text:t(a),href:a.href.slice(0,80)}));
  const focusable=[...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"]),[contenteditable=true]')].filter(v);
  const navSignature=navEls.map(n=>({linkTexts:[...n.querySelectorAll('a[href]')].slice(0,15).map(a=>t(a).slice(0,40)),htmlHash:[...n.querySelectorAll('a[href]')].slice(0,10).map(a=>a.getAttribute('href')).join('|')}));
  const landmarkZones=[...document.querySelectorAll('header,nav,main,footer,aside,[role=banner],[role=navigation],[role=main],[role=contentinfo],[role=complementary]')].filter(v).map(el=>({tag:el.tagName,role:el.getAttribute('role'),hasAriaLabel:!!(el.getAttribute('aria-label')||el.getAttribute('aria-labelledby'))}));
  return {url:location.href,title:document.title,theme12:{skipLink:skipLink?{text:t(skipLink),href:skipLink.getAttribute('href')}:null,hasMain:!!document.querySelector('main,[role=main]'),sitemapLinks,searchInputs:[...document.querySelectorAll('input[type=search],input[name*=search i],input[placeholder*=recherche i],form[role=search],form[action*=search]')].filter(v).length,navSignature,focusOrder:focusable.map((el,i)=>({index:i,tag:el.tagName,type:el.type||'',name:acc(el).slice(0,60),tabindex:el.tabIndex})),tabindexPositive:[...document.querySelectorAll('[tabindex]')].filter(el=>parseInt(el.getAttribute('tabindex'),10)>0&&v(el)).map(el=>({tag:el.tagName,tabindex:el.getAttribute('tabindex'),name:acc(el).slice(0,50)})),landmarkZones,singleKeyShortcuts:[],focusableCount:focusable.length}};
})()
