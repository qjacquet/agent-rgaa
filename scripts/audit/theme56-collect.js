(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = (el) => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = (el) => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const acc = (el) => { const lb=el.getAttribute('aria-labelledby'); if(lb){const x=lb.split(/\s+/).map(id=>document.getElementById(id)).filter(Boolean).map(t).join(' '); if(x)return x;} return el.getAttribute('aria-label')||el.getAttribute('alt')||el.getAttribute('title')||t(el); };
  const gen=/^(cliquez ici|cliquer ici|ici|lire la suite|en savoir plus|plus d['']infos|plus d'informations|d[ée]couvrir|voir plus|suite|link|click here|read more|learn more)$/i;
  const mapTable = (tb) => {
    const ths=[...tb.querySelectorAll('th')], tds=[...tb.querySelectorAll('td')], cap=tb.querySelector('caption'), role=tb.getAttribute('role');
    const pres=role==='presentation'||role==='none', data=(ths.length>0||role==='table')&&!pres, layout=!data&&tb.tagName==='TABLE';
    const partial=ths.filter(th=>th.getAttribute('headers')||(th.id&&ths.some(o=>o!==th&&o.getAttribute('headers')?.includes(th.id))));
    const complex=data&&(ths.some(th=>{const row=th.closest('tr');const ri=row?[...row.parentElement.children].indexOf(row):-1;return ri>0&&th.getAttribute('scope')!=='col';})||partial.length>0);
    const db=tb.getAttribute('aria-describedby');
    const sum=!!(cap?.textContent?.trim()||tb.getAttribute('summary')?.trim()||(db&&t(document.getElementById(db))));
    const thD=ths.map(th=>({scope:th.getAttribute('scope'),id:th.id||null,role:th.getAttribute('role')}));
    return {isDataTable:data,isLayoutTable:layout,isPresentation:pres,isComplex:complex,hasSummary:sum,hasCaption:!!cap,captionText:t(cap).slice(0,80),thDetails:thD,thNoScopeNoId:ths.filter(th=>!th.getAttribute('scope')&&!th.id&&!['rowheader','columnheader'].includes(th.getAttribute('role')||'')).length,thPartial:partial.length,layoutViolations:layout?{summary:!!tb.getAttribute('summary'),caption:!!cap,thead:!!tb.querySelector('thead'),th:ths.length>0,tfoot:!!tb.querySelector('tfoot'),tdScope:tds.some(td=>td.hasAttribute('scope')),tdHeaders:tds.some(td=>td.hasAttribute('headers')),tdAxis:tds.some(td=>td.hasAttribute('axis')),rowheader:!!tb.querySelector('[role=rowheader],[role=columnheader]')}:null,titleAttr:tb.getAttribute('title'),ariaLabel:tb.getAttribute('aria-label')};
  };
  const tables=[...document.querySelectorAll('table,[role=table]')].filter(v).map(mapTable);
  const dataTables=tables.filter(x=>x.isDataTable), layoutTables=tables.filter(x=>x.isLayoutTable), complexTables=tables.filter(x=>x.isComplex);
  let text=0,img=0,comp=0,svg=0,badText=[],badImg=[],badComp=[],badEmpty=[],badAria=[];
  for (const a of [...document.querySelectorAll('a[href],[role=link]')].filter(v)) {
    const imgs=[...a.querySelectorAll('img,[role=img],svg,object,canvas,area')];
    const textV=t(a), vis=[...a.childNodes].filter(n=>n.nodeType===3||(n.nodeType===1&&!['IMG','SVG','OBJECT','CANVAS'].includes(n.tagName))).map(n=>n.nodeType===3?n.textContent:t(n)).join(' ').trim();
    const imgL=imgs.length>0&&!vis, c=imgs.length>0&&!!vis, svgL=!!(a.querySelector('svg')&&!vis), name=acc(a);
    const ctx=t(a.closest('li,td,th,p,h1,h2,h3,h4,h5,h6,figcaption,label')||a.parentElement).slice(0,120);
    const generic=gen.test(textV.trim())||gen.test(name.trim());
    const empty=!textV&&!name&&!a.getAttribute('title');
    const hasBoth=!!(vis&&(a.getAttribute('aria-label')||a.getAttribute('title')||a.getAttribute('aria-labelledby')));
    const ariaBad=hasBoth&&!(acc(a).toLowerCase().includes(vis.toLowerCase().slice(0,Math.min(vis.length,20))));
    const noAlt=imgs.some(i=>!acc(i)&&i.tagName!=='SVG');
    if (!imgL&&!c&&!svgL) text++; else if (imgL) img++; else if (c) comp++; else svg++;
    if (empty) badEmpty.push({text:textV.slice(0,40),href:(a.href||'').slice(0,80)});
    if (!imgL&&!c&&!svgL && (empty||(generic&&! (generic&&ctx.length>textV.length+5)))) badText.push({text:textV.slice(0,40),generic});
    if (imgL&&(noAlt||empty)) badImg.push({name:name.slice(0,40)});
    if (c&&(noAlt||empty)) badComp.push({text:textV.slice(0,40)});
    if (hasBoth&&ariaBad) badAria.push({visible:vis.slice(0,30),name:name.slice(0,40)});
  }
  const svgLinks=[...document.querySelectorAll('svg a[href], svg [href]')].filter(el=>v(el.closest('svg')||el));
  const badSvg=svgLinks.filter(el=>!acc(el.closest('svg')||el)&&!t(el)).length;
  return {url:location.href,theme5:{counts:{total:tables.length,data:dataTables.length,layout:layoutTables.length,complex:complexTables.length},dataTables,layoutTables,complexTables},theme6:{counts:{total:text+img+comp+svg,text,image:img,composite:comp,svg:svgLinks.length},badText,badImg,badComp,badEmpty,badAria,badSvg,svgLinks:svgLinks.length}};
})()
