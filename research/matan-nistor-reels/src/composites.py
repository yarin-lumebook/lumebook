"""Composite features over the coded Reels, with period-adjusted performance (views / month median) inside the top 100.
Writes composites.json and prints a table."""
import json, csv, statistics as st, re, os
rows = {r['code']: r for r in csv.DictReader(open('../data/reels.csv', encoding='utf-8-sig'))}
top = [l.strip() for l in open('top100_codes.txt') if l.strip()]
cmp_ = [l.strip() for l in open('cmp20_codes.txt') if l.strip()]
def C(c): return json.load(open(f'coded/{c}.json'))
def toks(s): return {t.strip().split(' ')[0].split(':')[0].lower() for t in s.split(';') if t.strip()}
def f_story(r):
    m = toks(r['story_mechanisms']); s = r['story_structure'].split(' ')[0].lower()
    return s in ('setup_escalation_payoff', 'story_arc') or bool(m & {'twist', 'delayed_reveal', 'conflict_or_argument', 'repeated_episodes_with_escalation', 'social_experiment'})
def f_advice(r):
    s = r['story_structure'].split(' ')[0].lower()
    return s in ('claim_reasons_close', 'list') and not f_story(r)
def f_own(r):
    b = toks(r['broll_source']); return bool(b & {'own_lifestyle_proof', 'own_event_or_client_footage'})
def f_stock(r):
    b = toks(r['broll_source']); return 'stock_footage' in b
def f_stock_no_own(r): return f_stock(r) and not f_own(r)
def f_humor(r): return 'humor' in toks(r['hook_types']) or 'humor' in toks(r['implicit_triggers'])
def f_situation(r):  # a real situation filmed (street, skit, vlog, tour, POV) vs speech-led formats
    return r['format'].split(' ')[0].lower() in ('street_interaction', 'skit_or_pov', 'vlog_montage', 'tour_or_reveal')
def f_speech_led(r): return r['format'].split(' ')[0].lower() in ('talking_head_direct', 'podcast_or_interview_clip', 'stage_or_lecture_clip')
def f_standalone(r): return r['first_sentence_standalone'] == 'yes'
def f_num3(r): return r['number_or_money_first_3s'] == 'yes'
def f_kw(r): return 'comment_keyword_for_dm' in toks(r['next_action'])
def f_payoff(r): return r['payoff_delivered'] == 'yes'
def f_identity_only(r):
    h = toks(r['hook_types']); return 'identity_callout' in h and not (h & {'money_or_number', 'in_medias_res', 'visual_spectacle_or_location', 'pov_or_skit_setup', 'humor', 'challenge_or_giveaway'})
def f_end_card(r): return r['ending_type'].split(' ')[0].lower() == 'end_card_brand_promo'
def f_overlay(r): return 'overlay_effect' in toks(r['edit_moves'])
F = {'story_engine': f_story, 'advice_lecture_only': f_advice, 'own_footage_proof': f_own, 'stock_without_own': f_stock_no_own, 'humor': f_humor,
     'filmed_situation_format': f_situation, 'speech_led_format': f_speech_led, 'standalone_first_line': f_standalone, 'number_in_3s': f_num3,
     'keyword_cta': f_kw, 'payoff_delivered': f_payoff, 'identity_callout_without_concrete_hook': f_identity_only, 'brand_end_card': f_end_card, 'overlay_effects': f_overlay}
groups = {'top': top, 'tierA': top[:25], 'tierD': top[75:], 'cmp': cmp_}
out = {}
print(f"{'feature':<40} {'top':>7} {'tierA':>7} {'tierD':>7} {'cmp':>7} | top100 x-month median with / without (n)")
for k, fn in F.items():
    o = {g: sum(fn(rows[c]) for c in cs) for g, cs in groups.items()}
    w = [float(rows[c]['views_vs_month_median']) for c in top if fn(rows[c])]
    wo = [float(rows[c]['views_vs_month_median']) for c in top if not fn(rows[c])]
    o['xmonth_with'] = (round(st.median(w), 2) if w else None, len(w)); o['xmonth_without'] = (round(st.median(wo), 2) if wo else None, len(wo))
    out[k] = o
    print(f"{k:<40} {o['top']:>4}/100 {o['tierA']:>4}/25 {o['tierD']:>4}/25 {o['cmp']:>4}/20 | {o['xmonth_with']} / {o['xmonth_without']}")
json.dump(out, open('composites.json', 'w'), indent=1)
