(() => {
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
  const forms=[...document.querySelectorAll('form')].map(f=>({action:(f.action||'').slice(0,80),hasSubmit:!!f.querySelector('button[type=submit],input[type=submit]'),hasReset:!!f.querySelector('button[type=reset],input[type=reset],button:not([type])'),fieldCount:f.querySelectorAll('input,select,textarea').length})];
  const userFields=formFields.filter(f=>/nom|name|email|tel|phone|address|adresse|postal|ville|city|user|prenom|prénom|siren|siret/i.test(f.name+f.id+f.labelText));
  return {url:location.href,title:document.title,theme11:{formFields,fieldsNoLabel:formFields.filter(f=>!f.hasLabel),buttons,fieldsets,optgroups,optgroupsNoLabel:optgroups.filter(o=>!o.hasLabel),errorMsgs,forms,userFields,formCount:document.querySelectorAll('form').length}};
})()
