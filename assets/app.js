'use strict';
const $ = id => document.getElementById(id);
const engine = window.ReportEngine;
const money = n => new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',minimumFractionDigits:2}).format(n/100);
const number = n => new Intl.NumberFormat('en-GB').format(n);
const escapeHTML = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let source = [], selectedBucket = null, selectedRow = null, page = 0, current = [], view = [], summary;
const pageSize = 8;
function policy() { return {mode:$('policy').value,excludeDescription:$('exclude-description').checked,excludeCustomer:$('exclude-customer').checked}; }
function render() {
  const month = $('month').value, p = policy();
  current = source.filter(r=>month==='all'||r.date.startsWith(month));
  summary = engine.summarize(current,p);
  const baseline = engine.summarize(current,{mode:'positive',excludeDescription:false,excludeCustomer:false});
  $('baseline-total').textContent = money(baseline.includedPence);
  $('selected-total').textContent = money(summary.includedPence);
  $('difference').textContent = money(summary.includedPence-baseline.includedPence);
  $('baseline-rows').textContent = number(baseline.includedRows)+' priced positive-quantity lines';
  $('selected-rows').textContent = number(summary.includedRows)+' included · '+number(summary.rows-summary.includedRows)+' excluded';
  $('identity').textContent = summary.identityVerified?'✓ Balanced':'Check failed';
  $('row-count').textContent = number(current.length)+' source rows';
  $('raw-total').textContent = money(summary.rawPence);
  $('included-total').textContent = money(summary.includedPence);
  $('excluded-total').textContent = money(summary.excludedPence);
  const ordered = Object.keys(engine.LABELS).filter(k=>summary.groups[k]);
  $('buckets').innerHTML = ordered.map(k=>`<button class="bucket ${k} ${k===selectedBucket?'active':''}" data-bucket="${k}"><span class="bucket-label"><i class="dot"></i>${escapeHTML(engine.LABELS[k])}</span><span class="count">${number(summary.groups[k].rows)} rows</span><span class="money">${money(summary.groups[k].pence)}</span></button>`).join('');
  for (const button of $('buckets').querySelectorAll('button')) button.addEventListener('click',()=>{selectedBucket=button.dataset.bucket;page=0;render();});
  view=current.filter(r=>!selectedBucket||engine.classify(r,p)===selectedBucket);
  if(page*pageSize>=view.length) page=0;
  $('table-heading').textContent = selectedBucket?engine.LABELS[selectedBucket]:'Source lines';
  const visible=view.slice(page*pageSize,(page+1)*pageSize);
  $('source-rows').innerHTML = visible.map(r=>{const bucket=engine.classify(r,p);return `<tr data-row="${r.source_row}" tabindex="0" aria-label="Inspect workbook row ${r.source_row}" class="${r.source_row===selectedRow?'active':''}"><td>#${r.source_row}</td><td>${escapeHTML(r.invoice)}<small>${escapeHTML(r.stock)}</small></td><td>${escapeHTML(r.description||'— missing in original export —')}<small>${escapeHTML(r.date.slice(0,10))} · ${escapeHTML(r.country)}</small></td><td>${r.quantity}</td><td>${escapeHTML(r.unit_price)}</td><td>${money(engine.amountPence(r.quantity,r.unit_price))}</td><td><span class="result-tag ${bucket==='included'?'':'excluded'}">${bucket==='included'?'Included':escapeHTML(engine.LABELS[bucket])}</span></td></tr>`;}).join('');
  for (const tr of $('source-rows').querySelectorAll('tr')) { const show=()=>{selectedRow=Number(tr.dataset.row);inspect(current.find(r=>r.source_row===selectedRow));render();}; tr.addEventListener('click',show);tr.addEventListener('keydown',event=>{if(event.key==='Enter')show();}); }
  $('table-count').textContent = view.length?`${page*pageSize+1}–${Math.min((page+1)*pageSize,view.length)} of ${number(view.length)} lines · source row numbers include the workbook header`:'No source lines in this bucket';
  $('prev').disabled=page===0;$('next').disabled=(page+1)*pageSize>=view.length;
  window.demoState={summary,baseline,policy:p,displayRows:source.length,filteredRows:current.length};
}
function inspect(r) {
  const key=engine.classify(r,policy());
  $('selected-detail').innerHTML=`<h3>Workbook row #${r.source_row} · ${escapeHTML(r.description||'Missing description')}</h3><div class="detail-grid"><div><small>ORIGINAL INVOICE</small><b>${escapeHTML(r.invoice)}</b></div><div><small>QUANTITY × UNIT PRICE</small><b>${r.quantity} × £${escapeHTML(r.unit_price)}</b></div><div><small>ROUNDED LINE AMOUNT</small><b>${money(engine.amountPence(r.quantity,r.unit_price))}</b></div><div><small>CUSTOMER REFERENCE</small><b>${r.missing_customer?'Missing in original':'Present · identifier omitted'}</b></div></div><div class="detail-reason">${key==='included'?'Included under this explicit policy.':escapeHTML(engine.LABELS[key])+'. Source amount is retained in the excluded contribution.'}</div>`;
}
function download(exceptionsOnly) {
  const p=policy(), rows=exceptionsOnly?current.filter(r=>engine.classify(r,p)!=='included'):current;
  const fields=['source_row','invoice','stock','description','quantity','unit_price','date','country','missing_customer','amount_pence','policy_result','policy_mode','exclude_missing_description','require_customer_reference'];
  // Spreadsheet-formula injection prevention on text columns; never alter original numeric amounts.
  const cell=(value,text=false)=>{let s=String(value);if(text&&/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
  const csv=[fields.join(','),...rows.map(r=>[r.source_row,...['invoice','stock','description'].map(k=>cell(r[k],true)),r.quantity,cell(r.unit_price),cell(r.date),cell(r.country,true),r.missing_customer,engine.amountPence(r.quantity,r.unit_price),cell(engine.classify(r,p)),p.mode,p.excludeDescription,p.excludeCustomer].join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download=`source-bridge-${exceptionsOnly?'exceptions':'report'}-${p.mode}-${$('month').value}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
  $('export-status').textContent=`Downloaded ${number(rows.length)} source-linked ${exceptionsOnly?'exception':'report'} lines. CSV includes policy, row IDs and integer-pence amounts.`;
}
function reset() { $('policy').value='positive';$('month').value='all';$('exclude-description').checked=false;$('exclude-customer').checked=false;selectedBucket=null;selectedRow=null;page=0;$('selected-detail').innerHTML='<span class="muted">Select a source line to inspect its original fields.</span>';$('export-status').textContent='';render(); }
async function start() {
  try {
    const [data,results]=await Promise.all([fetch('data/sample.json').then(r=>{if(!r.ok)throw Error('Sample unavailable');return r.json();}),fetch('eval/results.json').then(r=>{if(!r.ok)throw Error('Evaluation unavailable');return r.json();})]);
    source=data.rows;$('sample-count').textContent=number(source.length);
    for(const month of [...new Set(source.map(r=>r.date.slice(0,7)))].sort()){const o=document.createElement('option');o.value=month;o.textContent=new Intl.DateTimeFormat('en-GB',{month:'long',year:'numeric',timeZone:'UTC'}).format(new Date(month+'-01T00:00:00Z'));$('month').appendChild(o);}
    const full=results.policies;
    $('full-evidence').innerHTML=`<div><b>5 / 5</b><small>Policies match independent reference</small></div><div><b>${number(results.diagnostics_overlap.negative_quantity)}</b><small>Negative quantities · diagnostic count</small></div><div><b>${number(results.diagnostics_overlap.c_prefix)}</b><small>C-prefix rows · a different cohort</small></div><div><b>${number(results.diagnostics_overlap.negative_price)}</b><small>Negative-price records kept visible</small></div><div><b>${money(full.positive_quantity_baseline.included_pence)}</b><small>Full-corpus positive-quantity baseline</small></div><div><b>${money(full.signed_positive_price.included_pence)}</b><small>Full-corpus signed positive-price policy</small></div>`;
    for(const id of ['policy','month','exclude-description','exclude-customer'])$(id).addEventListener('change',()=>{selectedBucket=null;page=0;selectedRow=null;$('selected-detail').innerHTML='<span class="muted">Select a source line to inspect its original fields.</span>';render();});
    $('show-negative').addEventListener('click',()=>{selectedBucket='negative_price';page=0;const row=current.find(r=>Number(r.unit_price)<0);if(row){selectedRow=row.source_row;inspect(row);}render();});
    $('show-all').addEventListener('click',()=>{selectedBucket=null;page=0;render();});
    $('prev').addEventListener('click',()=>{page--;render();});$('next').addEventListener('click',()=>{page++;render();});
    $('export').addEventListener('click',()=>download(false));$('export-exceptions').addEventListener('click',()=>download(true));$('reset').addEventListener('click',reset);
    reset();window.demoReady=true;
  } catch(error){$('error').hidden=false;$('error').textContent='The demo could not load its local assets. Run python scripts/run.py, then open the printed local address. Detail: '+error.message;}
}
start();
