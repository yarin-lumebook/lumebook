import json, glob, os, statistics, sys
sys.path.insert(0,'discovery'); from ig_stats import med as igmed, v as igv
tt_med={}
for f in glob.glob('discovery/tt_*.jsonl'):
    rows=[json.loads(l) for l in open(f) if l.strip()]
    if rows: tt_med[f.split('tt_')[1][:-6]]=statistics.median([r.get('view_count') or 0 for r in rows])
tt_med.setdefault('lovevery',1168)  # from the 80-video listing at 2026-10-06 (file later overwritten by a failed retry)
TT_KEEP=['7558132191016848653','7590920094268656918','7643375925211548942','7654309839501282573','7670237675021978910','7678574235685522718','7691722009285348621','7681725986479574286','7685388630449294606','7684276679774162206']
IL_KEEP=open('shortlist_he.txt').read().split()
out=[]
for f in sorted(glob.glob('videos/*.info.json')):
    j=json.load(open(f)); vid=os.path.basename(f)[:-10]; pre,code=vid.split('_',1)
    if pre=='tt' and code not in TT_KEEP: continue
    if pre=='ig' and code not in IL_KEEP: continue
    if pre=='igen' and code not in igv: continue
    if pre=='ai':
        cand={c.get('_id'):c for c in json.load(open('discovery/ai_solo_candidates.json'))}.get(code)
        if not cand: continue
    plat={'tt':'TikTok'}.get(pre) or ('YouTube' if 'youtu' in (j.get('webpage_url') or '') else 'TikTok' if 'tiktok' in (j.get('webpage_url') or '') else 'Instagram')
    m={'id':vid,'platform':plat,'country':'IL' if pre=='ig' else 'intl','source':'ai' if pre=='ai' else 'scan',
       'url': j.get('webpage_url'),'post_owner': (j.get('channel') if pre!='tt' else None) or (j.get('uploader') if pre=='tt' else None) or j.get('uploader_id'),'post_owner_name': j.get('uploader'),
       'duration_s': j.get('duration'),'upload_date': j.get('upload_date'),'caption': j.get('description') or ''}
    if pre=='ai':
        m.update(account=cand.get('account') or j.get('uploader_id') or j.get('uploader'), views=j.get('view_count') or cand.get('views'), likes=j.get('like_count') or cand.get('likes'),
                 comments=j.get('comment_count'), account_median_views=cand.get('account_median_views'), country=cand.get('country','intl'), ai_made_how=cand.get('made_how'), ai_tools=cand.get('ai_tools_if_known'), found_via=cand.get('source_of_finding'))
    elif pre=='tt':
        acct=(j.get('webpage_url') or '').split('@')[1].split('/')[0] if '@' in (j.get('webpage_url') or '') else (j.get('uploader') or '')
        m.update(account=acct, views=j.get('view_count'), likes=j.get('like_count'), comments=j.get('comment_count'), shares=j.get('repost_count'), account_median_views=tt_med.get(acct))
    else:
        acct,p,l,c=igv[code]
        m.update(account=acct, views=p, likes=l, comments=c, account_median_views=igmed.get(acct))
    if m.get('views') and m.get('account_median_views'): m['outlier_x']=round(m['views']/m['account_median_views'],1)
    if m.get('views') and m.get('likes') is not None: m['like_rate_pct']=round(100*m['likes']/m['views'],2)
    os.makedirs(f'analysis/{vid}',exist_ok=True); json.dump(m,open(f'analysis/{vid}/meta.json','w'),ensure_ascii=False,indent=1)
    out.append(m)
json.dump(out,open('all_meta.json','w'),ensure_ascii=False,indent=1)
print(len(out)); [print(m['id'],m['account'],m.get('views'),m.get('outlier_x'),m.get('like_rate_pct')) for m in out]
