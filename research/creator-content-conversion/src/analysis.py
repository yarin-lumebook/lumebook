"""Merge public metrics (sample.json), content codes (coded/), comment codes (comments_coded/)
and raw comments (cm.json) into posts.csv / creators.csv rows and print the leaderboards.
Every rate states its denominator. Missing = blank, never zero."""
import json, os, csv, glob, statistics as st, datetime, math, collections, re, sys

B = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(B, 'sample.json')))
DEEP = json.load(open(os.path.join(B, 'deep.json')))
CM = json.load(open(os.path.join(B, 'cm.json'))) if os.path.exists(os.path.join(B, 'cm.json')) else {}
MAP = {c['h']: c for c in json.load(open('/Users/yarinbruner/Claude/Projects/Lumebook/creators/creator-research/src/C_all.json'))}
CODED, CC = {}, {}
for f in glob.glob(os.path.join(B, 'coded', '*.json')):
    for x in json.load(open(f)):
        CODED[x['code']] = x
for f in glob.glob(os.path.join(B, 'comments_coded', '*.json')) + glob.glob(os.path.join(B, 'comments_extra_coded', '*.json')):
    d = json.load(open(f))
    for p in d['posts']:
        CC[p['code']] = p
ROLE = {p['code']: p['role'] for ps in DEEP.values() for p in ps}
if os.path.exists(os.path.join(B, 'extra_list.json')):
    for _u, _c, _pk in json.load(open(os.path.join(B, 'extra_list.json'))):
        ROLE.setdefault(_c, 'extra_high_relevance')
STRATA = json.load(open(os.path.join(B, 'strata.json'))) if os.path.exists(os.path.join(B, 'strata.json')) else {}

def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None

def per(a, b, k=1000):
    return round(a * k / b, 2) if a is not None and b else None

def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime('%Y-%m-%dT%H:%MZ')

rows = []
for u, r in S.items():
    fc = (r.get('prof') or {}).get('fc')
    base = r['base']
    keep_brk = sorted([q for q in r['posts'] if q['set'] == 'breakout'],
                      key=lambda q: -((q.get('rel_plays') if q['format'] == 'reel' else q.get('rel_likes')) or 0))[:3]
    keep = {q['code'] for q in keep_brk}
    for q in r['posts']:
        if q['set'] != 'sample' and q['code'] not in keep:
            continue
        c = CODED.get(q['code'], {})
        cc = CC.get(q['code'], {})
        likes = None if q['hid'] else q['likes']
        mdir = os.path.join(B, 'media', u, q['code'])
        meta = json.load(open(os.path.join(mdir, 'meta.json'))) if os.path.exists(os.path.join(mdir, 'meta.json')) else {}
        tr = ''
        if os.path.exists(os.path.join(mdir, 'whisper.txt')):
            _t = open(os.path.join(mdir, 'whisper.txt')).read().strip()
            tr = 'no_speech' if (len(_t) < 15 or re.fullmatch(r'((תודה רבה|תודה)\.?\s*)+', _t)) else 'speech'
        cnt = cc.get('counts', {})
        intent = sum(cnt.get(k, 0) for k in ('explicit_buying_intent', 'product_or_price_question', 'purchase_report')) if cc else None
        row = dict(
            creator=u, map_archetype=MAP.get(u, {}).get('arch'), stratum=STRATA.get(u, {}).get('stratum'),
            followers_14oct=fc, post_code=q['code'], url=f"https://www.instagram.com/p/{q['code']}/",
            set=q['set'], creator_window=r['window'], format=q['format'],
            published_utc=iso(q['t']), observed_utc=iso(r['obs']), age_days=round(q['age_d'], 1),
            plays=q.get('plays'), likes=likes, comments=q['com'], reposts=q.get('rep'),
            likes_hidden=bool(q['hid']), fb_crosspost_likes=q.get('fbl'), fb_crosspost_comments=q.get('fbc'),
            likes_per_1k_plays=per(likes, q.get('plays')), comments_per_1k_plays=per(q['com'], q.get('plays')),
            reposts_per_1k_plays=per(q.get('rep'), q.get('plays')),
            plays_per_follower_proxy=round(q['plays'] / fc, 3) if q.get('plays') and fc else None,
            likes_per_1k_followers_proxy=per(likes, fc), comments_per_1k_followers_proxy=per(q['com'], fc),
            baseline_n_same_format=base.get(q['format'], {}).get('n'),
            baseline_median_plays=base.get(q['format'], {}).get('plays'),
            baseline_median_likes=base.get(q['format'], {}).get('likes'),
            baseline_median_comments=base.get(q['format'], {}).get('com'),
            rel_plays=q.get('rel_plays') and round(q['rel_plays'], 2),
            rel_likes=q.get('rel_likes') and round(q['rel_likes'], 2),
            rel_comments=q.get('rel_com') and round(q['rel_com'], 2),
            ig_paid_partnership_label=bool(q.get('paid')), coauthors=';'.join(q.get('coa') or []),
            sponsor_tags=';'.join([s for s in (q.get('spons') or []) if s]), n_usertags=len(q.get('tags') or []),
            pinned=bool(q.get('pin')), duration_s=meta.get('duration_s') and round(meta['duration_s'], 1),
            audio_type=q.get('aud'), whisper_first_30s=tr or 'not_transcribed' if q['format'] == 'reel' else '',
            deep_role=ROLE.get(q['code'], ''),
            comments_sampled=cc.get('n_comments') if cc else None,
            unique_commenters_sampled=cc.get('n_unique_commenters') if cc else None,
            **{('cmt_' + k): (cnt.get(k) if cc else None) for k in ('identification', 'personal_experience', 'practical_help_request', 'product_or_price_question', 'objection', 'explicit_buying_intent', 'purchase_report', 'keyword_request', 'tag_or_share', 'giveaway_entry', 'generic_praise', 'creator_reply', 'spam_or_unrelated')},
            cmt_about_offer=cc.get('about_offer') if cc else None, cmt_gift_mention=cc.get('gift_mention') if cc else None,
            cmt_purchase_intent_signals=intent,
            **{k: c.get(k) for k in ('topic', 'problem_or_desire', 'occasion', 'occasion_note', 'buyer_segment', 'buyer_segment_basis',
                                     'format_detail', 'hook_text', 'caption_first_line', 'hook_type', 'emotional_angle', 'practical_takeaway',
                                     'product_visible', 'product_category', 'product_detail', 'proof', 'price_visible', 'discount_or_code',
                                     'cta', 'cta_detail', 'destination', 'status', 'status_basis', 'lumebook_relevance',
                                     'lumebook_relevance_reason', 'inspection', 'notes')},
        )
        rows.append(row)

def score(rw):
    return rw['rel_plays'] if rw['format'] == 'reel' else rw['rel_likes']

if __name__ == '__main__':
    json.dump(rows, open(os.path.join(B, 'rows.json'), 'w'), ensure_ascii=False)
    print(len(rows), 'rows;', sum(1 for r in rows if r['set'] == 'sample'), 'sample;', sum(1 for r in rows if r['topic']), 'coded;', sum(1 for r in rows if r['comments_sampled'] is not None), 'comment-coded')

def write_csvs(outdir):
    import glob as _g
    os.makedirs(outdir, exist_ok=True)
    cols = list(rows[0].keys())
    with open(os.path.join(outdir, 'posts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in sorted(rows, key=lambda r: (r['creator'], r['set'] != 'sample', r['published_utc'])):
            w.writerow({k: ('' if v is None else v) for k, v in r.items()})
    # creator level
    facts = json.load(open('/Users/yarinbruner/Claude/Projects/Lumebook/shared/facts.json'))['creators']
    od = '/private/tmp/claude-501/-Users-yarinbruner-Claude-Projects-Lumebook/fd0f7925-159f-49b8-a42a-92b54c8e7515/scratchpad/outreach/outreach/'
    status = {}
    for fn in _g.glob(od + '*.json'):
        status[os.path.basename(fn)[:-5]] = json.load(open(fn)).get('s') or ''
    crow = []
    for u, r in S.items():
        rs = [x for x in rows if x['creator'] == u and x['set'] == 'sample']
        reels = [x for x in rs if x['format'] == 'reel']
        car = [x for x in rs if x['format'] != 'reel']
        fc = (r.get('prof') or {}).get('fc')
        mp = MAP.get(u, {})
        cc = [x for x in rows if x['creator'] == u and x['comments_sampled'] is not None]
        def s(k):
            v = [x[k] for x in cc if x[k] is not None]
            return sum(v) if v else None
        occ = collections.Counter(x['occasion'] for x in rs if x['occasion'])
        crow.append(dict(
            creator=u, url=f'https://www.instagram.com/{u}/', stratum=STRATA.get(u, {}).get('stratum'),
            selection_reason=STRATA.get(u, {}).get('reason'), map_archetype=mp.get('arch'),
            followers_in_map=mp.get('f'), followers_14oct=fc,
            outreach_status_14oct=status.get(u, 'not contacted') or 'no status',
            barter_batch=u in facts['barter_batch'], paid_hold=u in facts['paid_hold'],
            competitor_conflict=u in facts['competitor_conflicts'],
            window=r['window'], sample_posts=len(rs), reels=len(reels), carousels=sum(1 for x in rs if x['format'] == 'carousel'),
            images=sum(1 for x in rs if x['format'] == 'image'),
            median_reel_plays=med([x['plays'] for x in reels]),
            median_reel_plays_per_follower_proxy=round(med([x['plays'] for x in reels]) / fc, 2) if med([x['plays'] for x in reels]) and fc else None,
            median_likes_per_1k_plays=med([x['likes_per_1k_plays'] for x in reels]),
            median_comments_per_1k_plays=med([x['comments_per_1k_plays'] for x in reels]),
            median_reposts_per_1k_plays=med([x['reposts_per_1k_plays'] for x in reels]),
            median_nonreel_likes=med([x['likes'] for x in car]), median_nonreel_comments=med([x['comments'] for x in car]),
            median_nonreel_likes_per_1k_followers_proxy=med([x['likes_per_1k_followers_proxy'] for x in car]),
            posts_high_relevance=sum(1 for x in rs if x['lumebook_relevance'] == 'high'),
            posts_medium_relevance=sum(1 for x in rs if x['lumebook_relevance'] == 'medium'),
            top_occasions=';'.join(f'{k}:{v}' for k, v in occ.most_common(3)),
            posts_product_featured=sum(1 for x in rs if x['product_visible'] in ('featured', 'demonstrated')),
            posts_comment_keyword_cta=sum(1 for x in rs if x['cta'] == 'comment_keyword'),
            posts_sponsored_or_collab=sum(1 for x in rs if x['status'] in ('likely_sponsored', 'collaboration', 'paid_partnership_label')),
            posts_giveaway=sum(1 for x in rs if x['status'] == 'giveaway'),
            breakouts_analysed=sum(1 for x in rows if x['creator'] == u and x['set'] == 'breakout'),
            deep_posts=len(cc), comments_classified=s('comments_sampled'),
            cmt_purchase_intent_signals=s('cmt_purchase_intent_signals'), cmt_keyword_requests=s('cmt_keyword_request'),
            cmt_identification_or_experience=(s('cmt_identification') or 0) + (s('cmt_personal_experience') or 0) if cc else None,
            cmt_help_requests=s('cmt_practical_help_request'), cmt_objections=s('cmt_objection'), cmt_gift_mentions=s('cmt_gift_mention'),
        ))
    with open(os.path.join(outdir, 'creators.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(crow[0].keys())); w.writeheader()
        for c in sorted(crow, key=lambda c: (c['stratum'] or '', c['creator'])):
            w.writerow({k: ('' if v is None else v) for k, v in c.items()})
    json.dump(crow, open(os.path.join(B, 'creators_rows.json'), 'w'), ensure_ascii=False)
    print('wrote', len(rows), 'posts and', len(crow), 'creators to', outdir)

if __name__ == '__main__' and len(sys.argv) > 1:
    write_csvs(sys.argv[1])
