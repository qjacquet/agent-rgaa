(() => {
  const parts = [(() => {
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
})(),(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = el => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const acc = el => el.getAttribute('aria-label')||el.getAttribute('title')||t(el);
  const deprecated=['basefont','big','blink','center','font','marquee','s','strike'];
  const presentationTags=deprecated.flatMap(tag=>[...document.querySelectorAll(tag)].filter(v).map(el=>({tag:el.tagName})));
  const presAttrNames=['align','bgcolor','border','cellpadding','cellspacing','width','height'];
  const presentationAttrs=[]; for(const el of document.querySelectorAll('*')) for(const a of presAttrNames) if(el.hasAttribute(a)) presentationAttrs.push({tag:el.tagName,attr:a});
  const nbspAbuse=[...document.querySelectorAll('p,td,th,span,div')].filter(v).filter(el=>/\u00a0{2,}/.test(el.textContent||'')||/(\s{3,})/.test((el.textContent||'').replace(/\u00a0/g,' '))).slice(0,10).map(el=>({tag:el.tagName,text:t(el).slice(0,40)}));
  const parseRgb=c=>{const m=c.match(/[\d.]+/g);return m&&m.length>=3?m.slice(0,3).map(Number):null;};
  const lum=([r,g,b])=>{const a=[r,g,b].map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2];};
  const ratio=(fg,bg)=>{const L1=lum(fg),L2=lum(bg);return (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);};
  const bgOf=el=>{let n=el;while(n&&n!==document.documentElement){const bg=parseRgb(getComputedStyle(n).backgroundColor);if(bg&&bg.some(x=>x>0)&&getComputedStyle(n).backgroundColor!=='rgba(0, 0, 0, 0)')return bg;n=n.parentElement;}return parseRgb(getComputedStyle(document.body).backgroundColor)||[255,255,255];};
  const fails=[]; let checked=0;
  for(const el of [...document.querySelectorAll('p,span,a,button,h1,h2,h3,h4,h5,h6,label,li,td,th')].filter(v)){const text=t(el);if(text.length<2)continue;const fg=parseRgb(getComputedStyle(el).color),bg=bgOf(el);if(!fg||!bg)continue;const r=ratio(fg,bg);checked++;const fs=parseFloat(getComputedStyle(el).fontSize),bold=parseInt(getComputedStyle(el).fontWeight,10)>=700,min=(fs>=18||(fs>=14&&bold))?3:4.5;if(r<min)fails.push({tag:el.tagName,text:text.slice(0,50),ratio:Math.round(r*100)/100,min});}
  const coloredTextNoBg=[]; for(const el of [...document.querySelectorAll('p,span,li,td,th,label,h1,h2,h3,h4,h5,h6')].filter(v)){const color=getComputedStyle(el).color,bg=getComputedStyle(el).backgroundColor;if(color&&bg==='rgba(0, 0, 0, 0)'&&el.tagName!=='A'&&bgOf(el))coloredTextNoBg.push({tag:el.tagName,text:t(el).slice(0,40)});}
  const links=[...document.querySelectorAll('a[href],[role=link]')].filter(v).map(a=>{const s=getComputedStyle(a),underline=s.textDecorationLine.includes('underline')||s.textDecoration.includes('underline'),diffColor=s.color!==getComputedStyle(a.parentElement||document.body).color,hasIndicator=underline||diffColor||a.querySelector('img,svg')||a.getAttribute('aria-label');return{text:t(a).slice(0,60),colorOnly:!hasIndicator&&!!t(a)};});
  const focusable=[...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])')].filter(v);
  const noFocusOutline=focusable.filter(el=>{const s=getComputedStyle(el);return(s.outlineStyle==='none'||s.outlineWidth==='0px')&&!s.boxShadow&&s.borderWidth==='0px';}).slice(0,15).map(el=>({tag:el.tagName,name:acc(el).slice(0,50)}));
  const hiddenContent=[...document.querySelectorAll('[hidden],[aria-hidden=true]')].map(el=>({tag:el.tagName,focusable:el.matches('a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])')}));
  const hoverTooltips=[...document.querySelectorAll('[title],[data-tooltip],[aria-describedby]')].filter(v).slice(0,20).map(el=>({tag:el.tagName,title:el.getAttribute('title')}));
  return {url:location.href,title:document.title,theme10:{presentationTags,presentationAttrs:presentationAttrs.slice(0,30),nbspAbuse,contrast:{checked,failCount:fails.length,fails:fails.slice(0,25)},coloredTextNoBg:coloredTextNoBg.slice(0,15),colorOnlyLinks:links.filter(l=>l.colorOnly),noFocusOutline,hiddenContent,hiddenWithFocusable:hiddenContent.filter(h=>h.focusable),bgImageText:[],hoverTooltips,hasStylesheets:document.styleSheets.length>0||document.querySelectorAll('link[rel=stylesheet],style').length>0}};
})(),(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = el => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const acc = el => el.getAttribute('aria-label')||el.getAttribute('title')||t(el);
  const formFields=[...document.querySelectorAll('input,select,textarea')].filter(f=>f.type!=='hidden'&&v(f)).map(f=>{
    const id=f.id; const label=id?document.querySelector(`label[for="${CSS.escape(id)}"]`):f.closest('label');
    const ariaLabel=f.getAttribute('aria-label'),ariaLabelledby=f.getAttribute('aria-labelledby'),title=f.getAttribute('title');
    const hasLabel=!!(label||ariaLabel||ariaLabelledby||title);
    return {tag:f.tagName,type:f.type||'',name:f.name||f.id||'',id,hasLabel,labelText:(label?t(label):(ariaLabel||title||'')).slice(0,80),visibleLabelNear:label&&v(label),ariaLabel,ariaLabelledby,title,required:f.required||f.getAttribute('aria-required')==='true',ariaInvalid:f.getAttribute('aria-invalid')==='true',autocomplete:f.getAttribute('autocomplete'),labelMismatch:label&&ariaLabel&&!ariaLabel.toLowerCase().includes(t(label).toLowerCase().slice(0,10))&&t(label).length>3};
  });
  const buttons=[...document.querySelectorAll('button,input[type=submit],input[type=button],input[type=reset]')].filter(v).map(b=>({tag:b.tagName,type:b.type||'',text:t(b).slice(0,60),name:acc(b).slice(0,60),ariaMismatch:!!(t(b)&&b.getAttribute('aria-label')&&!acc(b).toLowerCase().includes(t(b).toLowerCase().slice(0,8)))}));
  const fieldsets=[...document.querySelectorAll('fieldset')].map(fs=>({legend:t(fs.querySelector('legend')).slice(0,80),hasLegend:!!fs.querySelector('legend'),fieldCount:fs.querySelectorAll('input,select,textarea').length}));
  const optgroups=[...document.querySelectorAll('optgroup')].map(og=>({label:og.getAttribute('label'),hasLabel:!!og.getAttribute('label')}));
  const errorMsgs=[...document.querySelectorAll('[role=alert],.error,.invalid,.field-error,[class*=error],[class*=invalid]')].filter(v).map(el=>({tag:el.tagName,role:el.getAttribute('role'),text:t(el).slice(0,100)}));
  const forms=[...document.querySelectorAll('form')].map(f=>({action:(f.action||'').slice(0,80),hasSubmit:!!f.querySelector('button[type=submit],input[type=submit]'),hasReset:!!f.querySelector('button[type=reset],input[type=reset],button:not([type])'),fieldCount:f.querySelectorAll('input,select,textarea').length}));
  const userFields=formFields.filter(f=>/nom|name|email|tel|phone|address|adresse|postal|ville|city|user|prenom|prénom|siren|siret/i.test(f.name+f.id+f.labelText));
  return {url:location.href,title:document.title,theme11:{formFields,fieldsNoLabel:formFields.filter(f=>!f.hasLabel),buttons,fieldsets,optgroups,optgroupsNoLabel:optgroups.filter(o=>!o.hasLabel),errorMsgs,forms,userFields,formCount:document.querySelectorAll('form').length}};
})()];
  return Object.assign({}, ...parts);
})()
