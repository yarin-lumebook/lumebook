"""Patterns in the 120 coded Reels (100 top + 20 matched comparisons). Writes coded_patterns.json and coded_patterns.md.
Counts always carry their denominator. Groups: top (100), tierA (ranks 1-25), tierD (ranks 76-100), cmp (20 comparisons),
plus pair-level tallies over the 20 top/comparison pairs. Descriptive only."""
import json, os, re, statistics as st, collections
M = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels'
metrics = json.load(open('metrics.json'))
pairs = json.load(open('comparisons.json'))['pairs']
top = [l.strip() for l in open('top100_codes.txt') if l.strip()]
cmp_ = [p['cmp'] for p in pairs]
C = {}
for c in top + cmp_:
    p = f'coded/{c}.json'
    if os.path.exists(p):
        C[c] = json.load(open(p))
idx = {c: json.load(open(f'{M}/analysis/{c}/index.json')) for c in C if os.path.exists(f'{M}/analysis/{c}/index.json')}

def toks(x):
    """Vocabulary tokens from a coded list or string field (first word of each item, lower, before ':' or ' (')."""
    if x is None: return set()
    items = x if isinstance(x, list) else [x]
    out = set()
    for it in items:
        if isinstance(it, dict): it = it.get('type', '')
        for part in re.split(r'\s*\|\s*', str(it)):
            w = re.split(r'[\s:(,]', part.strip(), maxsplit=1)[0].lower()
            if w: out.add(w)
    return out
def yes(x):
    return str(x or '').strip().lower().startswith('yes')
F = {  # feature name -> function(coded, code) -> bool
}
def add(name, fn): F[name] = fn
for fmt in ['talking_head_direct', 'street_interaction', 'podcast_or_interview_clip', 'stage_or_lecture_clip', 'skit_or_pov', 'vlog_montage', 'tour_or_reveal', 'text_only', 'b_roll_voiceover', 'tv_clip']:
    add(f'format={fmt}', lambda d, c, f=fmt: f in toks(d.get('format')))
for tp in ['money_giveaway', 'anti_school_degree', 'employee_vs_owner', 'wealth_mindset', 'business_tactics', 'marketing_social_media', 'relationships_gender', 'travel_lifestyle', 'couple_life', 'mortality_meaning', 'personal_story', 'own_offer_promo', 'podcast_guest_talk', 'humor_skit']:
    add(f'topic={tp}', lambda d, c, t=tp: t in toks(d.get('topic')))
for pu in ['reach_growth', 'community_engagement', 'lead_capture', 'sell_own_offer', 'drive_to_long_form', 'personal_brand', 'entertainment']:
    add(f'purpose={pu}', lambda d, c, p=pu: p in toks(d.get('purpose')))
for h in ['bold_claim_contrarian', 'money_or_number', 'direct_question', 'curiosity_gap', 'identity_callout', 'in_medias_res', 'visual_spectacle_or_location', 'pov_or_skit_setup', 'list_promise', 'warning_or_urgency', 'personal_confession', 'status_or_social_proof', 'challenge_or_giveaway', 'humor']:
    add(f'hook={h}', lambda d, c, h=h: h in toks(d.get('opening', {}).get('hook_types')))
add('first_sentence_standalone', lambda d, c: yes(d.get('opening', {}).get('first_sentence_standalone')))
add('number_or_money_first_3s', lambda d, c: yes(d.get('opening', {}).get('number_or_money_in_first_3s')))
add('works_without_sound=yes', lambda d, c: yes(d.get('opening', {}).get('works_without_sound')))
add('eye_contact=mostly', lambda d, c: 'mostly' in toks(d.get('visual', {}).get('eye_contact')))
add('partner_on_camera', lambda d, c: any('partner' in str(x).lower() or 'livnat' in str(x).lower() for x in (d.get('visual', {}).get('on_camera') or [])))
for b in ['own_lifestyle_proof', 'own_event_or_client_footage', 'stock_footage', 'film_or_tv_clips_third_party', 'viral_clip_third_party', 'screen_recording']:
    add(f'broll={b}', lambda d, c, b=b: b in toks(d.get('visual', {}).get('broll_source')))
add('cover_matches=yes', lambda d, c: yes(d.get('visual', {}).get('cover_matches_video')))
for em in ['jump_cut', 'punch_in_zoom', 'insert_broll', 'inset_picture', 'overlay_effect', 'text_animation', 'end_card', 'fade_from_black', 'transition_effect', 'speed_change']:
    add(f'edit={em}', lambda d, c, em=em: em in toks(d.get('editing', {}).get('edit_moves')))
for et in ['end_card_brand_promo', 'direct_cta_to_camera', 'punchline', 'loop', 'cliffhanger', 'summary_or_point_card', 'abrupt', 'fade_out']:
    add(f'ending={et}', lambda d, c, et=et: et in toks(d.get('editing', {}).get('ending_type')))
add('loop=yes', lambda d, c: yes(d.get('editing', {}).get('loop')))
for sp in ['direct_to_camera', 'voiceover', 'dialogue', 'lecture_mic', 'none']:
    add(f'speech={sp}', lambda d, c, sp=sp: sp in toks(d.get('sound', {}).get('speech')))
add('music_likely', lambda d, c: str(d.get('sound', {}).get('music', '')).lower().startswith('likely'))
for tx in ['word_by_word_captions', 'phrase_captions', 'headline_persistent', 'running_counter_or_scoreboard', 'numbered_point_cards', 'numbers_or_prices', 'none']:
    add(f'text={tx}', lambda d, c, tx=tx: tx in toks(d.get('text', {}).get('on_screen')))
for s in ['claim_reasons_close', 'setup_escalation_payoff', 'list', 'story_arc', 'qa_or_interview', 'demonstration', 'montage', 'announcement']:
    add(f'structure={s}', lambda d, c, s=s: s in toks(d.get('story', {}).get('structure')))
for mk in ['open_question', 'delayed_reveal', 'demonstration', 'numbered_list', 'escalating_examples', 'repeated_episodes_with_escalation', 'callback', 'contrast_before_after', 'conflict_or_argument', 'twist', 'social_experiment', 'analogy', 'visual_proof_of_claim']:
    add(f'mech={mk}', lambda d, c, mk=mk: mk in toks(d.get('story', {}).get('mechanisms')))
add('payoff_delivered=yes', lambda d, c: yes(d.get('story', {}).get('payoff_delivered')))
for pr in ['comment_keyword', 'comment_opinion', 'tag_friend', 'share', 'save', 'follow', 'like', 'watch_to_end', 'poll', 'story_visit']:
    add(f'prompt={pr}', lambda d, c, pr=pr: pr in toks(d.get('engagement', {}).get('explicit_prompts')))
add('prompt_in_video', lambda d, c: any(isinstance(p, dict) and p.get('type') not in (None, 'none') and str(p.get('where', '')).startswith(('video', 'both')) for p in d.get('engagement', {}).get('explicit_prompts', [])))
for it in ['relatability', 'disagreement_bait', 'identity', 'utility', 'humor', 'emotion', 'status_aspiration', 'curiosity', 'money_reward']:
    add(f'trigger={it}', lambda d, c, it=it: it in toks(d.get('engagement', {}).get('implicit_triggers')))
for na in ['comment_keyword_for_dm', 'link_in_bio', 'story_link', 'follow', 'watch_long_form', 'buy_ticket_or_course', 'join_club', 'read_book', 'none']:
    add(f'next={na}', lambda d, c, na=na: na in toks(d.get('conversion', {}).get('next_action')))
add('third_party_footage', lambda d, c: str(d.get('rights_and_privacy', '')).lower().startswith('third-party film, tv or viral footage used: yes') or bool(re.search(r'\byes\b', str(d.get('rights_and_privacy', '')).lower().split(';')[0])))
add('collab', lambda d, c: metrics[c]['collab'])
add('licensed_music', lambda d, c: metrics[c]['audio_type'] == 'licensed_music')

def grp(name):
    if name == 'top': return [c for c in top if c in C]
    if name == 'tierA': return [c for c in top[:25] if c in C]
    if name == 'tierD': return [c for c in top[75:] if c in C]
    if name == 'cmp': return [c for c in cmp_ if c in C]
    if name == 'top_paired': return [p['top'] for p in pairs if p['top'] in C and p['cmp'] in C]
G = ['top', 'tierA', 'tierD', 'cmp', 'top_paired']
res = {'n': {g: len(grp(g)) for g in G}, 'features': {}, 'pairs': {}, 'numeric': {}, 'comments': {}, 'by_format': {}, 'by_topic': {}}
for f, fn in F.items():
    res['features'][f] = {g: sum(1 for c in grp(g) if fn(C[c], c)) for g in G}
    tally = collections.Counter()
    for p in pairs:
        if p['top'] in C and p['cmp'] in C:
            a, b = fn(C[p['top']], p['top']), fn(C[p['cmp']], p['cmp'])
            tally['top_only' if a and not b else 'cmp_only' if b and not a else 'both' if a else 'neither'] += 1
    res['pairs'][f] = dict(tally)
def num(c, k):
    m = metrics[c]; ix = idx.get(c, {})
    if k == 'duration': return m['duration_s']
    if k == 'cuts_per_10s': return len(ix.get('cuts', [])) * 10 / m['duration_s'] if ix else None
    if k == 'avg_shot_s': return ix.get('avg_shot_s')
    if k == 'topic_clear_at_s':
        v = C[c].get('opening', {}).get('topic_clear_at_s')
        try: return float(v)
        except Exception: return None
    if k == 'quiet_share': 
        r = ix.get('rms_db_per_0_5s') or []
        return sum(1 for x in r if x < -40) / len(r) if r else None
    return m.get(k)
for k in ['duration', 'cuts_per_10s', 'avg_shot_s', 'topic_clear_at_s', 'quiet_share', 'likes_per_1k_ig_views', 'comments_per_1k_ig_views', 'shares_per_1k_ig_views', 'views_grid', 'views_per_day']:
    res['numeric'][k] = {}
    for g in G:
        vals = [num(c, k) for c in grp(g)]
        vals = [v for v in vals if v is not None]
        res['numeric'][k][g] = {'n': len(vals), 'median': round(st.median(vals), 2) if vals else None}
for g in ['top', 'cmp']:
    tot = collections.Counter(); read = 0; replies = 0
    for c in grp(g):
        e = C[c].get('engagement', {})
        for k, v in (e.get('comment_categories') or {}).items():
            if isinstance(v, (int, float)): tot[k] += v
        read += C[c].get('evidence', {}).get('comments_read') or 0
        replies += e.get('creator_replies_in_sample') or 0
    res['comments'][g] = {'comments_read': read, 'categories': dict(tot), 'creator_replies_in_sample': replies}
def by(fieldfn, store):
    buckets = collections.defaultdict(list)
    for c in grp('top'):
        for k in fieldfn(C[c]): buckets[k].append(c)
    for k, cs in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        vals = lambda key: [metrics[c][key] for c in cs if metrics[c][key] is not None]
        store[k] = {'n': len(cs), 'median_views': st.median(vals('views_grid')), 'median_likes_1k': round(st.median(vals('likes_per_1k_ig_views')), 2),
                    'median_comments_1k': round(st.median(vals('comments_per_1k_ig_views')), 2),
                    'shares_1k_comparable_n': len(vals('shares_per_1k_ig_views')), 'median_shares_1k': round(st.median(vals('shares_per_1k_ig_views')), 2) if vals('shares_per_1k_ig_views') else None,
                    'codes': cs[:8]}
by(lambda d: toks(d.get('format')) or {'?'}, res['by_format'])
by(lambda d: toks(d.get('topic')) or {'?'}, res['by_topic'])
json.dump(res, open('coded_patterns.json', 'w'), ensure_ascii=False, indent=1)
L = [f"# Coded patterns (generated by analyze_coded.py)", '', f"Coded: top {res['n']['top']}/100, tier A {res['n']['tierA']}/25, tier D {res['n']['tierD']}/25, comparisons {res['n']['cmp']}/20, complete pairs {res['n']['top_paired']}/20.", '',
     '| Feature | Top | Tier A (1-25) | Tier D (76-100) | Comparisons | Pairs: top only / cmp only / both / neither |', '|---|---|---|---|---|---|']
for f, v in res['features'].items():
    pr = res['pairs'][f]
    L.append(f"| {f} | {v['top']}/{res['n']['top']} | {v['tierA']}/{res['n']['tierA']} | {v['tierD']}/{res['n']['tierD']} | {v['cmp']}/{res['n']['cmp']} | {pr.get('top_only',0)} / {pr.get('cmp_only',0)} / {pr.get('both',0)} / {pr.get('neither',0)} |")
L += ['', '| Numeric (median) | Top | Tier A | Tier D | Comparisons | Paired tops |', '|---|---|---|---|---|---|']
for k, v in res['numeric'].items():
    L.append(f"| {k} | " + ' | '.join(f"{v[g]['median']} (n={v[g]['n']})" for g in G[:4] + ['top_paired']) + ' |')
L += ['', '## By format (top 100)', '', '| Format | n | Median views | Likes/1k | Comments/1k | Shares/1k (n comparable) | Examples |', '|---|---|---|---|---|---|---|']
for k, v in res['by_format'].items():
    L.append(f"| {k} | {v['n']} | {v['median_views']:,} | {v['median_likes_1k']} | {v['median_comments_1k']} | {v['median_shares_1k']} ({v['shares_1k_comparable_n']}) | {', '.join(v['codes'][:4])} |")
L += ['', '## By topic (top 100)', '', '| Topic | n | Median views | Likes/1k | Comments/1k | Shares/1k (n comparable) | Examples |', '|---|---|---|---|---|---|---|']
for k, v in res['by_topic'].items():
    L.append(f"| {k} | {v['n']} | {v['median_views']:,} | {v['median_likes_1k']} | {v['median_comments_1k']} | {v['median_shares_1k']} ({v['shares_1k_comparable_n']}) | {', '.join(v['codes'][:4])} |")
L += ['', '## Sampled comments', '']
for g, v in res['comments'].items():
    L.append(f"- {g}: {v['comments_read']} comments read, categories {v['categories']}, creator replies seen {v['creator_replies_in_sample']}")
open('coded_patterns.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:3]))
