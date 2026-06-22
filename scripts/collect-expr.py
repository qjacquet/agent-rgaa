#!/usr/bin/env python3
"""Collecte DOM via expression JS compacte — à exécuter dans browser_cdp Runtime.evaluate."""
COLLECT_EXPR = r"""(() => {
  const btn = [...document.querySelectorAll('button')].find(b => /accepter|refuser tout/i.test(b.textContent||''));
  if (btn) btn.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
  const t = el => (el.innerText||'').trim().replace(/\s+/g,' ');
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(v).map(h=>({tag:h.tagName,level:+h.tagName[1],text:t(h).slice(0,100)}));
  const h1 = hs.filter(h=>h.tag==='H1');
  const jumps = []; for(let i=1;i<hs.length;i++) if(hs[i].level-hs[i-1].level>1) jumps.push({from:hs[i-1],to:hs[i]});
  const imgs = [...document.querySelectorAll('img,[role=img]')].filter(v);
  const noAlt = imgs.filter(i=>i.getAttribute('alt')===null&&!i.getAttribute('aria-label')&&!i.getAttribute('aria-labelledby')&&!['presentation','none'].includes(i.getAttribute('role')));
  const links = [...document.querySelectorAll('a[href]')].filter(v).filter(a=>!t(a)&&!a.getAttribute('aria-label')&&!a.title).map(a=>({href:a.href.slice(0,120),hasImg:!!a.querySelector('img,svg')}));
  const skip = [...document.querySelectorAll('a[href^="#"]')].find(a=>/aller au contenu|skip/i.test(t(a)+(a.getAttribute('aria-label')||'')));
  const fields = [...document.querySelectorAll('input,select,textarea')].filter(f=>f.type!=='hidden'&&v(f)).filter(f=>{const id=f.id;const lb=id?document.querySelector(`label[for="${id}"]`):null;return !lb&&!f.getAttribute('aria-label')&&!f.getAttribute('aria-labelledby')}).map(f=>({name:f.name||f.id||f.type,type:f.type||f.tagName}));
  const iframes = [...document.querySelectorAll('iframe')].filter(v).filter(f=>!f.title).length;
  const tab = [...document.querySelectorAll('[tabindex]')].filter(el=>parseInt(el.getAttribute('tabindex'),10)>0&&v(el)).map(el=>({tag:el.tagName,tabindex:el.getAttribute('tabindex')}));
  return {url:location.href,title:document.title,lang:document.documentElement.lang||'',h1Count:h1.length,h1Texts:h1.map(x=>x.text),headings:hs,headingJumps:jumps,images:{total:imgs.length,withoutAlt:noAlt.length},linksNoText:links,skipLink:skip?{text:t(skip),href:skip.getAttribute('href')}:null,fieldsNoLabel:fields,iframesNoTitle:iframes,tabindexPositive:tab,landmarks:[...document.querySelectorAll('main,nav,header,footer,[role=main],[role=navigation]')].filter(v).length};
})()"""

if __name__ == "__main__":
    print(COLLECT_EXPR)
