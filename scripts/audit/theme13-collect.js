(() => {
  document.getElementById('accept-recommended-btn-handler')?.click();
  const v = el => { const s=getComputedStyle(el),r=el.getBoundingClientRect(); return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0; };
  const t = el => (el?.innerText||el?.textContent||'').trim().replace(/\s+/g,' ');
  const metaRefresh=[...document.querySelectorAll('meta[http-equiv=refresh i],meta[http-equiv="refresh"]')].map(m=>m.getAttribute('content'));
  const autoRedirects=[...document.querySelectorAll('script')].filter(s=>/location\.(href|replace)|window\.open|setTimeout.*location/i.test(s.textContent||'')).length;
  const popupTriggers=[...document.querySelectorAll('[onclick*=window.open]')].length;
  const officeDownloads=[...document.querySelectorAll('a[href]')].filter(a=>/\.(doc|docx|xls|xlsx|ppt|pptx|odt|ods)(\?|$)/i.test(a.href)).map(a=>({href:a.href.slice(0,100),text:t(a).slice(0,60),altFormat:!!(a.closest('li,p')?.querySelector('a[href$=".pdf"],a[href*=".pdf"]')||/pdf|accessible|html/i.test(t(a.parentElement)))}));
  const cryptic=[...document.querySelectorAll('abbr,span,p')].filter(v).filter(el=>{const tx=t(el);return(/\p{Extended_Pictographic}/u.test(tx)&&tx.length<30)||/^[\W_]{3,}$/.test(tx);}).slice(0,10).map(el=>({tag:el.tagName,text:t(el).slice(0,40),title:el.getAttribute('title')}));
  return {url:location.href,title:document.title,theme13:{metaRefresh,autoRedirects,popupTriggers,officeDownloads,cryptic,blinking:[...document.querySelectorAll('marquee,blink')].length,animations:0,autoMoving:[...document.querySelectorAll('marquee,[autoplay]')].filter(v).map(el=>({tag:el.tagName})),touchOnly:[...document.querySelectorAll('[ontouchstart],[data-swipe],[data-gesture]')].length,motionFeatures:[...document.querySelectorAll('[ondevicemotion],[ondeviceorientation]')].length}};
})()
