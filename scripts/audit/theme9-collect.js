(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  [...document.querySelectorAll('button')].find(b => /accepter|tout accepter|refuser tout/i.test(b.textContent||''))?.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = el => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter(v).map(h=>({tag:h.tagName,level:h.tagName.match(/^H(\d)$/)?+h.tagName[1]:+(h.getAttribute('aria-level')||0),text:t(h).slice(0,100),empty:!t(h)}));
  const jumps=[]; for(let i=1;i<headings.length;i++) if(headings[i].level&&headings[i-1].level&&headings[i].level-headings[i-1].level>1) jumps.push({from:headings[i-1],to:headings[i]});
  const navEls=[...document.querySelectorAll('nav,[role=navigation]')];
  const landmarks={hasHeader:!!document.querySelector('header,[role=banner]'),navCount:navEls.length,hasMain:!!document.querySelector('main,[role=main]'),hasFooter:!!document.querySelector('footer,[role=contentinfo]'),navMisuse:[...document.querySelectorAll('nav')].filter(n=>!n.querySelector('a[href],button')&&t(n).length<5).length};
  const navOutsideNav=[...document.querySelectorAll('ul,ol')].filter(l=>l.querySelectorAll('a[href]').length>=3&&!l.closest('nav,[role=navigation],header,footer,aside')&&v(l)).slice(0,5).map(l=>({tag:l.tagName,linkCount:l.querySelectorAll('a[href]').length}));
  const lists={ul:document.querySelectorAll('ul,[role=list]').length,ol:document.querySelectorAll('ol').length,dl:document.querySelectorAll('dl').length,badUlOl:[],badDl:[]};
  for(const ul of document.querySelectorAll('ul,ol')) if(ul.querySelectorAll(':scope>li').length===0&&ul.querySelectorAll('li').length>0) lists.badUlOl.push({tag:ul.tagName});
  for(const dl of document.querySelectorAll('dl')) { const dts=dl.querySelectorAll('dt'),dds=dl.querySelectorAll('dd'); if((dts.length||dds.length)&&dts.length!==dds.length) lists.badDl.push({dts:dts.length,dds:dds.length}); }
  const quotes={blockquote:[...document.querySelectorAll('blockquote')].filter(v).map(q=>({text:t(q).slice(0,60)})),q:[...document.querySelectorAll('q')].filter(v).map(q=>({text:t(q).slice(0,60)})),inlineCitations:[...document.querySelectorAll('p,li,td')].filter(v).filter(el=>/[«""].{10,}[»""]/.test(t(el))&&!el.querySelector('q,blockquote')).slice(0,5).map(el=>t(el).slice(0,60)),blockCitations:[...document.querySelectorAll('p,div')].filter(v).filter(el=>el.classList.contains('quote')||el.classList.contains('citation')).slice(0,5).map(el=>({tag:el.tagName,text:t(el).slice(0,60),hasBlockquote:!!el.closest('blockquote')||el.tagName==='BLOCKQUOTE'}))};
  return {url:location.href,title:document.title,theme9:{headings,headingJumps:jumps,emptyHeadings:headings.filter(h=>h.empty),landmarks,navOutsideNav,lists,quotes}};
})()
