(() => {
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
})()
