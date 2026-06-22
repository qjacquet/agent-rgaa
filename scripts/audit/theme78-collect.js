(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = (el) => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = (el) => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const acc = (el) => { const lb=el.getAttribute('aria-labelledby'); if(lb){const x=lb.split(/\s+/).map(id=>document.getElementById(id)).filter(Boolean).map(t).join(' '); if(x)return x;} return el.getAttribute('aria-label')||el.getAttribute('alt')||el.getAttribute('title')||t(el); };
  const validLang = (c) => /^[a-z]{2,3}(-[A-Za-z]{2,8})*$/.test((c||'').trim());
  const clickOnly=[...document.querySelectorAll('[onclick],[onmousedown],[onmouseup]')].filter(v).filter(el=>!['A','BUTTON','INPUT','SELECT','TEXTAREA'].includes(el.tagName)&&el.getAttribute('role')!=='button'&&el.getAttribute('role')!=='link'&&el.tabIndex<0).map(el=>({tag:el.tagName,name:acc(el).slice(0,60)}));
  const scriptWidgets=[...document.querySelectorAll('[role=button],[role=link],[role=tab],[role=menuitem],[role=checkbox],[role=radio],[role=switch],[role=combobox],[role=listbox]')].filter(v).map(el=>({tag:el.tagName,role:el.getAttribute('role'),name:acc(el).slice(0,80),visibleText:t(el).slice(0,60),ariaMismatch:!!(t(el)&&el.getAttribute('aria-label')&&!acc(el).toLowerCase().includes(t(el).toLowerCase().slice(0,15)))}));
  const statusMsgs=[...document.querySelectorAll('[role=status],[role=alert],[role=log],[role=progressbar],[aria-live]')].filter(v).map(el=>({role:el.getAttribute('role'),live:el.getAttribute('aria-live'),atomic:el.getAttribute('aria-atomic'),text:t(el).slice(0,80)}));
  const selectOnChange=[...document.querySelectorAll('select')].filter(s=>s.getAttribute('onchange')||s.onchange).map(s=>({name:s.name||s.id,hasSubmitNearby:!!(s.closest('form')?.querySelector('button[type=submit],input[type=submit]'))}));
  const ns=document.querySelectorAll('noscript').length;
  const html=document.documentElement;
  const ids=[...document.querySelectorAll('[id]')].map(el=>el.id).filter(Boolean);
  const idCounts={}; ids.forEach(id=>{idCounts[id]=(idCounts[id]||0)+1;});
  const duplicateIds=Object.entries(idCounts).filter(([,c])=>c>1).map(([id,c])=>({id,count:c}));
  const langChanges=[...document.querySelectorAll('[lang],[xml\\:lang]')].filter(el=>el!==html).map(el=>({tag:el.tagName,lang:el.getAttribute('lang')||el.getAttribute('xml:lang'),valid:validLang(el.getAttribute('lang')||el.getAttribute('xml:lang'))}));
  const rtlBlocks=[...document.querySelectorAll('[dir=rtl],[dir=ltr]')].map(el=>({tag:el.tagName,dir:el.getAttribute('dir')}));
  const presentationMisuse=[...document.querySelectorAll('blockquote,cite,address,dl,ul,ol,hr,pre,em,strong,abbr,q,s,del,ins,sub,sup,small,big,code,var,samp,kbd,dfn')].filter(v).filter(el=>getComputedStyle(el).fontStyle==='normal'&&getComputedStyle(el).fontWeight==='normal'&&!el.querySelector('li,dt,dd')&&t(el).length<3).slice(0,20).map(el=>({tag:el.tagName,role:el.getAttribute('role')}));
  return {url:location.href,theme7:{clickOnly,scriptWidgets,statusMsgs,selectOnChange,noscriptCount:ns,hasNoscript:ns>0},theme8:{doctype:document.doctype?`<!DOCTYPE ${document.doctype.name}>`:null,doctypeName:document.doctype?.name||null,lang:html.getAttribute('lang')||'',pageTitle:document.title?.trim()||'',duplicateIds,duplicateIdCount:duplicateIds.length,langChanges,rtlBlocks,presentationMisuse,hasTitle:!!document.title?.trim(),validDefaultLang:validLang(html.getAttribute('lang')||'')}};
})()
