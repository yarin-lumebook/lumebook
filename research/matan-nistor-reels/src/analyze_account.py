"""Account-wide patterns over every Reel posted 2024-01-01 .. 2026-10-26 (at least 14 days live at collection).
Metric: relative views = Reel views / median views of all Reels posted in the same calendar month (controls
roughly for account growth and period; does not control for promotion, topic demand or follower count at posting).
Writes account_patterns.json and prints a summary. Descriptive only: no causal claims."""
import json, re, statistics as st, datetime, collections
info = json.load(open('media_info_2026-11-09.json'))
COLLECT = datetime.datetime(2026, 11, 9, 12, tzinfo=datetime.UTC)
VERB = r'(תגיבו|הגיבו|תכתבו|כתבו|שלחו|תרשמו|הגב|כתוב)'
REWARD = r'(ותקבלו|וקבלו|קבלו|לקבל|לקבלת|ואשלח|אשלח|אצלכם|להסבר|ישירות|בפרטי|במתנה|ותבינו|המלא)'
def kw(c):
    """Comment-keyword CTA: a comment verb, a pointer or quoted word, and a promised reward within the same stretch."""
    for m in re.finditer(VERB, c):
        win = c[max(0, m.start() - 60): m.end() + 90]
        if re.search(REWARD, win) and re.search(r'(המילה|👇|👈|⬇️|[״"\'׳]\S{1,14}[״"\'׳])', win):
            return True
    return False
rows = []
for v in info.values():
    t = datetime.datetime.fromtimestamp(v['taken_at'], datetime.UTC)
    if t < datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC) or (COLLECT - t).days < 14:
        continue
    cap = v.get('caption') or ''
    first = cap.strip().split('\n')[0] if cap.strip() else ''
    rows.append({
        'code': v['code'], 'month': t.strftime('%Y-%m'), 'dur': v.get('dur') or 0, 'views': v['play'],
        'ig': v.get('ig_play') or v['play'], 'likes': v['likes'], 'comments': v['comments'], 'shares': v.get('reshare'),
        'collab': (v.get('owner') != 'matan.nistor') or bool(v.get('coauthors')),
        'licensed': v.get('audio_type') == 'licensed_music',
        'kw': kw(cap),
        'opinion': bool(re.search(r'(תרשמו|תגיבו|כתבו)[^\n]{0,40}(בתגובות|דעתכם|👇)', cap)) and not kw(cap),
        'share_prompt': bool(re.search(r'(שלחו לחבר|שלחו ל|שתפו)', cap)),
        'giveaway': bool(re.search(r'(מחלק|הגרלה|לזכות|זוכה|תזכו)', cap)),
        'watch_end': bool(re.search(r'(צפו עד הסוף|עד הסוף)', cap)),
        'link_bio': bool(re.search(r'(ביו|בביו|bio)', cap)),
        'story': bool(re.search(r'סטורי', cap)),
        'question_first': '?' in first or '❓' in first,
        'hashtags': len(re.findall(r'#\S+', cap)),
        'cap_len': len(cap), 'episode': bool(re.search(r'(פרק|פודקאסט|יוטיוב|ביוטיוב)', cap)),
        'live': (v.get('dur') or 0) > 600,
    })
med = {m: st.median([r['views'] for r in rows if r['month'] == m]) for m in {r['month'] for r in rows}}
for r in rows:
    r['rel'] = r['views'] / med[r['month']]
top10 = sorted(r['rel'] for r in rows)[int(len(rows) * .9)]
def summ(name, sel):
    xs = [r for r in rows if sel(r)]
    if not xs: return None
    ig = [r['comments'] * 1000 / r['ig'] for r in xs if r['ig']]
    lk = [r['likes'] * 1000 / r['ig'] for r in xs if r['ig']]
    return {'group': name, 'n': len(xs), 'median_rel_views': round(st.median(r['rel'] for r in xs), 2),
            'share_in_top_decile': round(sum(r['rel'] >= top10 for r in xs) / len(xs), 3),
            'median_comments_per_1k': round(st.median(ig), 2), 'median_likes_per_1k': round(st.median(lk), 2)}
out = {'population': f'{len(rows)} Reels posted 2024-01-01..2026-10-26 with metadata', 'top_decile_rel_threshold': round(top10, 2), 'groups': []}
G = out['groups']
G.append(summ('all', lambda r: True))
for lo, hi in ((0, 15), (15, 30), (30, 45), (45, 60), (60, 90), (90, 600)):
    G.append(summ(f'duration {lo}-{hi}s', lambda r, lo=lo, hi=hi: lo <= r['dur'] < hi))
G.append(summ('live replay >600s', lambda r: r['live']))
for k, lab in (('collab', 'collab'), ('licensed', 'licensed music'), ('kw', 'caption comment-keyword CTA'), ('opinion', 'caption asks for opinions in comments'), ('share_prompt', 'caption asks to share/send to a friend'), ('giveaway', 'caption giveaway words'),
               ('watch_end', "caption 'watch to the end'"), ('link_bio', 'caption link in bio'), ('story', 'caption mentions story'),
               ('question_first', 'caption first line is a question'), ('episode', 'caption mentions episode/podcast/YouTube')):
    G.append(summ(f'{lab}: yes', lambda r, k=k: r[k] and not r['live']))
    G.append(summ(f'{lab}: no', lambda r, k=k: not r[k] and not r['live']))
for lo, hi in ((0, 1), (1, 6), (6, 100)):
    G.append(summ(f'hashtags {lo}-{hi - 1}', lambda r, lo=lo, hi=hi: lo <= r['hashtags'] < hi and not r['live']))
for y in ('2024', '2025', '2026'):
    G.append(summ(f'year {y}', lambda r, y=y: r['month'].startswith(y)))
# keyword CTA by year (does the comment lift hold within each year?)
for y in ('2024', '2025', '2026'):
    for flag in (True, False):
        G.append(summ(f'{y} keyword CTA {"yes" if flag else "no"}', lambda r, y=y, f=flag: r['month'].startswith(y) and r['kw'] == f and not r['live']))
out['groups'] = [g for g in G if g]
out['monthly_median_views'] = dict(sorted(med.items()))
json.dump(out, open('account_patterns.json', 'w'), ensure_ascii=False, indent=1)
print(out['population'], 'top decile rel >=', out['top_decile_rel_threshold'])
for g in out['groups']:
    print(f"{g['group']:<48} n={g['n']:>4} relV={g['median_rel_views']:>5} topdec={g['share_in_top_decile']:>5} c/1k={g['median_comments_per_1k']:>6} l/1k={g['median_likes_per_1k']:>6}")
