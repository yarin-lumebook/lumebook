import json,sys,glob,statistics,datetime
for f in sorted(glob.glob('discovery/tt_*.jsonl')):
    rows=[json.loads(l) for l in open(f) if l.strip()]
    if not rows: continue
    v=[r.get('view_count') or 0 for r in rows]
    med=statistics.median(v)
    h=f.split('tt_')[1][:-6]
    ts=[r.get('timestamp') for r in rows if r.get('timestamp')]
    span=''
    if ts: span=f"{datetime.date.fromtimestamp(min(ts))}..{datetime.date.fromtimestamp(max(ts))}"
    print(f"\n### {h} n={len(rows)} median={med:,.0f} {span}")
    top=sorted(rows,key=lambda r:-(r.get('view_count') or 0))[:6]
    for r in top:
        d=(r.get('description') or r.get('title') or '').replace('\n',' ')[:110]
        dt=datetime.date.fromtimestamp(r['timestamp']) if r.get('timestamp') else ''
        print(f"  {r.get('view_count') or 0:>11,} x{(r.get('view_count') or 0)/max(med,1):5.1f} {dt} {r.get('duration')}s {r.get('id')} | {d}")
