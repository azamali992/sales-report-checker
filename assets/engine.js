(function (root) {
  'use strict';
  const LABELS = {included:'Included in this report',negative_price:'Negative price · unsupported adjustment',zero_price:'Zero price · no priced contribution',zero_quantity:'Zero quantity',missing_description:'Description missing',missing_customer:'Customer reference missing',c_prefix_negative:'C-prefix negative quantities',other_negative:'Other negative quantities'};
  function amountPence(quantity, text) {
    if (!Number.isSafeInteger(quantity)) throw Error('Quantity must be a safe integer');
    const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(String(text));
    if (!match) throw Error('Unsupported decimal unit price');
    const digits = match[3] || '';
    let numerator = BigInt(match[2] + digits) * BigInt(quantity) * 100n;
    if (match[1]) numerator = -numerator;
    const denominator = 10n ** BigInt(digits.length);
    const sign = numerator < 0n ? -1n : 1n;
    const absolute = numerator < 0n ? -numerator : numerator;
    const rounded = sign * (absolute / denominator + ((absolute % denominator) * 2n >= denominator ? 1n : 0n));
    if (rounded > BigInt(Number.MAX_SAFE_INTEGER) || rounded < BigInt(Number.MIN_SAFE_INTEGER)) throw Error('Amount too large');
    return Number(rounded);
  }
  function classify(row, policy) {
    const price = Number(row.unit_price);
    if (price < 0) return 'negative_price';
    if (price === 0) return 'zero_price';
    if (row.quantity === 0) return 'zero_quantity';
    if (policy.excludeDescription && !row.description) return 'missing_description';
    if (policy.excludeCustomer && row.missing_customer) return 'missing_customer';
    if (policy.mode === 'positive' && row.quantity < 0) return row.invoice.toUpperCase().startsWith('C') ? 'c_prefix_negative' : 'other_negative';
    return 'included';
  }
  function summarize(rows, policy) {
    const groups = {}; let rawPence = 0;
    for (const row of rows) {
      const key = classify(row, policy), amount = amountPence(row.quantity, row.unit_price);
      if (!groups[key]) groups[key] = {rows:0,pence:0};
      groups[key].rows++; groups[key].pence += amount; rawPence += amount;
      if (!Number.isSafeInteger(rawPence) || !Number.isSafeInteger(groups[key].pence)) throw Error('Aggregate exceeded safe integer range');
    }
    const included = groups.included || {rows:0,pence:0};
    const excludedPence = Object.entries(groups).reduce((sum,[key,g]) => sum + (key==='included'?0:g.pence),0);
    return {rows:rows.length, rawPence, includedPence:included.pence, includedRows:included.rows, excludedPence, groups, identityVerified:rawPence===included.pence+excludedPence};
  }
  const api = {LABELS, amountPence, classify, summarize};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ReportEngine = api;
})(typeof window === 'undefined' ? globalThis : window);
