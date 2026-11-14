/* Metrics of one content experiment (MeBook customer study, 14 Nov 2026). Pure functions: the page inlines this file
   (build.py) and tools/tests/test_experiments.py runs it with node.

   A result is a number or null. null means "not measured" and is never treated as 0; 0 means "measured, none".
   CPA        = ad spend / attributed purchases   (paid only; ad spend based, not total CAC)
   ROAS       = attributed revenue / ad spend      (paid only)
   Visit to purchase = attributed purchases / landing page visits
   Each metric is {value, reason}: value is a number, or null with the reason it is unavailable. */
(function (root) {
  function num(v) {
    if (v === null || v === undefined || v === '') return null;
    var n = typeof v === 'number' ? v : Number(String(v).replace(/,/g, '').trim());
    return isFinite(n) && n >= 0 ? n : null;
  }

  function metrics(results, mode) {
    var r = results || {};
    var spend = num(r.spend), purchases = num(r.purchases), revenue = num(r.revenue), visits = num(r.visits);
    var paid = mode === 'paid';
    var cpa, roas, conv;
    if (!paid) cpa = { value: null, reason: 'not_paid' };
    else if (spend === null) cpa = { value: null, reason: 'no_spend' };
    else if (purchases === null) cpa = { value: null, reason: 'purchases_not_measured' };
    else if (purchases === 0) cpa = { value: null, reason: 'zero_purchases' };
    else cpa = { value: spend / purchases, reason: null };

    if (!paid) roas = { value: null, reason: 'not_paid' };
    else if (spend === null) roas = { value: null, reason: 'no_spend' };
    else if (spend === 0) roas = { value: null, reason: 'zero_spend' };
    else if (revenue === null) roas = { value: null, reason: 'revenue_not_measured' };
    else roas = { value: revenue / spend, reason: null };

    if (visits === null) conv = { value: null, reason: 'visits_not_measured' };
    else if (visits === 0) conv = { value: null, reason: 'zero_visits' };
    else if (purchases === null) conv = { value: null, reason: 'purchases_not_measured' };
    else conv = { value: purchases / visits, reason: null };

    return { cpa: cpa, roas: roas, conversion: conv };
  }

  /* Which investigation prompts apply. No thresholds: a prompt is offered when the numbers it talks about were measured,
     and the person decides whether "many" and "few" describe them. */
  function prompts(results) {
    var r = results || {};
    var reach = num(r.views) !== null ? num(r.views) : num(r.impressions);
    var visits = num(r.visits), purchases = num(r.purchases);
    var out = [];
    if (reach !== null && visits !== null) out.push('reach_vs_visits');
    if (visits !== null && purchases !== null) out.push('visits_vs_purchases');
    if (purchases === 1) out.push('single_purchase');
    return out;
  }

  var api = { num: num, metrics: metrics, prompts: prompts };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MBMetrics = api;
})(this);
