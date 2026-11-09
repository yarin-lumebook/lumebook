"""Builds ../data/reels.csv: one row per selected Reel (100 top + 20 comparisons) with raw public metrics,
derived ratios, evidence availability and the coded analytic tags. Missing values are empty cells, never zero.
Inputs: metrics.json, coded/*.json, media analysis index.json files, coverage.json. Rerun after any recode."""
import json, csv, os, statistics as st
M = '/Users/yarinbruner/Claude/Projects/Lumebook/media/projects/2026-11-09-matan-nistor-reels'
metrics = json.load(open('metrics.json'))
order = [l.strip() for l in open('top100_codes.txt') if l.strip()] + [l.strip() for l in open('cmp20_codes.txt') if l.strip()]
verified = json.load(open('verified.json')) if os.path.exists('verified.json') else {}
inv = json.load(open('inventory.json'))
_bym = {}
for x in inv['clips']:
    _bym.setdefault(x['date'][:7], []).append(x['play_count'])
MONTH_MED = {k: st.median(v) for k, v in _bym.items()}
def j(x):
    if x is None: return ''
    if isinstance(x, list): return '; '.join(str(i) for i in x)
    if isinstance(x, dict): return json.dumps(x, ensure_ascii=False)
    return x
def first_word(s):
    return (s or '').split(' ')[0].split(':')[0].strip(' ,.(') if isinstance(s, str) else ''
rows = []
for c in order:
    m = metrics[c]
    idx_p = f'{M}/analysis/{c}/index.json'
    idx = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
    w = f'{M}/analysis/{c}/whisper.txt'
    tr_file = os.path.exists(w)
    d = json.load(open(f'coded/{c}.json')) if os.path.exists(f'coded/{c}.json') else {}
    o, v, e, s_, t, st_, en, cv = (d.get(k, {}) for k in ('opening', 'visual', 'editing', 'sound', 'text', 'story', 'engagement', 'conversion'))
    ev = d.get('evidence', {})
    dur = idx.get('duration') or m['duration_s']
    rms = idx.get('rms_db_per_0_5s') or []
    quiet = round(sum(1 for x in rms if x < -40) / len(rms), 3) if rms else None
    row = {
        'rank_top100': m['rank_top100'] or '', 'group': m['group'], 'code': c, 'url': m['url'], 'pair_code': m['pair'] or '',
        'published_utc': m['published_utc'], 'collected': m['collected'], 'days_live': m['days_live'], 'duration_s': dur,
        'views_grid': m['views_grid'], 'ig_views': m['ig_views'] if m['ig_views'] is not None else '', 'fb_views': m['fb_views'] if m['fb_views'] is not None else '',
        'likes': m['likes'], 'comments': m['comments'], 'shares': m['shares'] if m['shares'] is not None else '', 'shares_raw_api': m['shares_raw'] if m['shares_raw'] is not None else '',
        'shares_comparable': m['shares_comparable'], 'reposts': m['reposts'] if m['reposts'] is not None else '', 'saves': '',
        'likes_per_1k_ig_views': m['likes_per_1k_ig_views'], 'comments_per_1k_ig_views': m['comments_per_1k_ig_views'],
        'shares_per_1k_ig_views': m['shares_per_1k_ig_views'] if m['shares_per_1k_ig_views'] is not None else '', 'views_per_day': m['views_per_day'], 'month_median_views_all_reels': MONTH_MED.get(m['published_utc'][:7]), 'views_vs_month_median': round(m['views_grid'] / MONTH_MED[m['published_utc'][:7]], 2),
        'owner': m['owner'], 'coauthors': j(m['coauthors']), 'collab': m['collab'], 'paid_partnership_label': m['paid_partnership_label'],
        'pinned_reels_tab': m['pinned_reels_tab'], 'pinned_profile_grid': m['pinned_profile_grid'], 'audio_type': m['audio_type'] or '',
        'music_title': (m['music'] or {}).get('title', ''),
        'ev_video': os.path.exists(f'{M}/videos/{c}.mp4'), 'ev_frames_1fps_sheets': len(idx.get('sheets', [])), 'ev_hook_4fps': bool(idx.get('hook_sheets')),
        'ev_transcript_file': tr_file, 'ev_coder_transcript': ev.get('transcript', ''), 'ev_coder_sheets_opened': ev.get('sheets_opened', ''),
        'ev_comments_sampled': ev.get('comments_read', ''), 'ev_cover': os.path.exists(f'{M}/covers/{c}.jpg'), 'ev_checked_by_lead': verified.get(c, ''),
        'cuts_detected': len(idx.get('cuts', [])) if idx else '', 'avg_shot_s': idx.get('avg_shot_s', ''),
        'cuts_per_10s': round(len(idx.get('cuts', [])) * 10 / dur, 2) if idx and dur else '', 'quiet_share_below_-40db': quiet if quiet is not None else '',
        'topic': d.get('topic', ''), 'topic_detail': d.get('topic_detail', ''), 'audience': d.get('audience', ''), 'format': d.get('format', ''),
        'setting_type': d.get('setting_type', ''), 'purpose': d.get('purpose', ''),
        'hook_types': j(o.get('hook_types')), 'hook_motive': j(o.get('motive')), 'text_hook': o.get('text_hook', ''), 'first_frame': o.get('first_frame', ''),
        'first_sentence_standalone': first_word(o.get('first_sentence_standalone')), 'number_or_money_first_3s': first_word(o.get('number_or_money_in_first_3s')),
        'topic_clear_at_s': o.get('topic_clear_at_s', ''), 'works_without_sound': first_word(o.get('works_without_sound')),
        'shot_size_main': v.get('shot_size_main', ''), 'eye_contact': v.get('eye_contact', ''), 'on_camera': j(v.get('on_camera')),
        'broll_source': j(v.get('broll_source')), 'persistent_branding': v.get('persistent_branding', ''), 'cover_matches_video': first_word(v.get('cover_matches_video')),
        'edit_moves': j(e.get('edit_moves')), 'ending_type': e.get('ending_type', ''), 'loop': first_word(e.get('loop')),
        'speech': s_.get('speech', ''), 'music': first_word(s_.get('music')),
        'on_screen_text': j(t.get('on_screen')), 'colour_coding': t.get('colour_coding', ''),
        'story_structure': st_.get('structure', ''), 'story_mechanisms': j(st_.get('mechanisms')), 'payoff_delivered': first_word(st_.get('payoff_delivered')),
        'explicit_prompts': j(sorted({p.get('type', '') for p in en.get('explicit_prompts', []) if isinstance(p, dict)})),
        'implicit_triggers': j(en.get('implicit_triggers')), 'creator_replies_in_sample': en.get('creator_replies_in_sample', ''),
        'comment_categories': j(en.get('comment_categories')),
        'next_action': j(cv.get('next_action')), 'cta_timing': cv.get('cta_timing', ''), 'funnel_entry_visible': cv.get('funnel_entry_visible', ''),
        'cta_fits_content': first_word(cv.get('cta_fits_content')),
        'pair_match': j(d.get('pair_match')) if m['group'] == 'comparison' else '',
        'rights_and_privacy': d.get('rights_and_privacy', ''),
        'why_it_may_work_interpretation': d.get('why_it_may_work', ''),
    }
    rows.append(row)
os.makedirs('../data', exist_ok=True)
with open('../data/reels.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('rows', len(rows), 'coded', sum(1 for r in rows if r['format']))
