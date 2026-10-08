import json,glob
rows=[]
for f in sorted(glob.glob('analysis/*/breakdown.json')):
    d=f.rsplit('/',1)[0]; m=json.load(open(d+'/meta.json')); b=json.load(open(f))
    rows.append((m.get('outlier_x') or 0,m['id'],m.get('account'),m.get('views'),m.get('like_rate_pct'),b.get('format'),b.get('made_by'),(b.get('solo_route') or {}).get('verdict'),(b.get('solo_route') or {}).get('effort'),b.get('niches'),str(b.get('paid_signal'))[:12],b.get('one_line')))
for r in sorted(rows,reverse=True):
    print(f"{r[0]:>7} | {r[1]} | @{r[2]} | {r[3]} | lr {r[4]} | {r[5]} | {r[6]} | {r[7]}/{r[8]} | {','.join(r[9] or [])} | paid:{r[10]}\n        {r[11]}")
