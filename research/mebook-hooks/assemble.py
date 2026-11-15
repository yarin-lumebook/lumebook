"""Builds hooks.json and mebook-hooks.md: MeBook's 50 best performing on-screen, spoken and caption hooks.
Reels are ranked by the Instagram play count shown on @mebook.ai's Reels grid (15 Nov 2026). Ads have no public
numbers: they follow the Ad Library's own "total impressions" order and come after the reels, marked as ads."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
W = lambda *p: os.path.join(HERE, *p)
INVIS = re.compile('[⁦-⁩‎‏‪-‮\t]')

def clean(s):
    return re.sub(r'\s+', ' ', INVIS.sub('', s or '')).strip()

def first_sentence(s, limit=140):
    s = clean(s)
    m = re.match(r'(.+?[.!?…](?=\s|$))', s)
    out = m.group(1) if m and len(m.group(1)) >= 12 else s
    return out if len(out) <= limit else out[:limit].rsplit(' ', 1)[0] + ' …'

reels = json.load(open(W('work/reels-meta.json')))
ads = json.load(open(W('raw/ads.json')))['ads']
ons = {}
for b in 'abcde':
    for x in json.load(open(W(f'work/onscreen-{b}.json'))):
        ons[x['key']] = x
for k, fix in json.load(open(W('work/onscreen-fixes.json'))).items():
    ons[k].update(fix)

NO_SPEECH = {'', 'תודה רבה.', 'תודה רבה', '[no audio]', '[מוזיקה]', '[Music]', 'תודה.'}
SFIX = {k: v for k, v in json.load(open(W('work/spoken-fixes.json'))).items() if not k.startswith('_')}
def spoken_basis(key):
    return SFIX[key]['basis'] if key in SFIX else 'auto'
def spoken(key):
    if key in SFIX:
        return SFIX[key]['text']
    p = W('work/whisper', key + '.txt')
    if not os.path.exists(p):
        return None
    lines = [clean(l) for l in open(p, encoding='utf-8') if clean(l)]
    text = ' '.join(l for l in lines if l not in NO_SPEECH)
    if not text or text in NO_SPEECH:
        return ''
    return first_sentence(text)

items = []
for r in reels:
    o = ons.get(r['code'], {})
    items.append(dict(kind='reel', key=r['code'], url=f"https://www.instagram.com/reel/{r['code']}/", views=r['views'],
                      account='@' + (r['account'] or ''), date=r['date'], on_screen=clean(o.get('on_screen', '')),
                      on_screen_kind=o.get('on_screen_kind'), on_screen_conf=o.get('confidence'), spoken=spoken(r['code']), spoken_basis=spoken_basis(r['code']),
                      caption=first_sentence(r['caption_first'], 160)))
for a in ads:
    o = ons.get(a['id'], {})
    items.append(dict(kind='ad', key=a['id'], url=f"https://www.facebook.com/ads/library/?id={a['id']}", views=None,
                      ad_rank=a['rank'], account='MeBook ad', date=a['start'], on_screen=clean(o.get('on_screen', '')),
                      on_screen_kind=o.get('on_screen_kind'), on_screen_conf=o.get('confidence'), spoken=spoken(a['id']), spoken_basis=spoken_basis(a['id']),
                      caption=first_sentence(a['text'].split('\n')[0], 160)))

def on_screen_display(it, o):
    if o.get('display'):
        return o['display']
    if it['on_screen'] and it.get('on_screen_kind') == 'subtitles' and it.get('spoken_basis') == 'subtitles':
        return it['spoken']            # the subtitles say the spoken words; frames caught them mid-build
    return it['on_screen'].replace(' / ', ' ')

for it in items:
    it['on_screen_raw'] = it['on_screen']
    it['on_screen'] = on_screen_display(it, ons.get(it['key'], {})) if it['on_screen'] else ''

def top(field, n=50):
    seen, out = set(), []
    for it in items:                      # reels first (already by views), then ads in Ad Library order
        v = it.get(field)
        if not v:
            continue
        norm = re.sub(r'[^֐-׿a-zA-Z0-9]', '', v)[:40]
        if norm in seen:
            continue
        seen.add(norm); out.append(it)
        if len(out) == n:
            break
    return out

lists = {f: top(f) for f in ('on_screen', 'spoken', 'caption')}
json.dump({'items': items, 'top': {f: [i['key'] for i in v] for f, v in lists.items()}},
          open(W('hooks.json'), 'w'), ensure_ascii=False, indent=1)

def fmt_views(it):
    return f"{it['views']:,}" if it['views'] is not None else f"ad #{it['ad_rank']}"

TITLES = {'on_screen': 'On-screen hooks (text on the video in the first 3 seconds)',
          'spoken': 'Spoken hooks (first spoken sentence)',
          'caption': 'Caption hooks (first line of the post caption)'}
reel_n = sum(1 for i in items if i['kind'] == 'reel')
no_speech = sum(1 for i in items if i['kind'] == 'reel' and i['spoken'] == '' and spoken_basis(i['key']) == 'auto')
unclear = sum(1 for i in items if i['kind'] == 'reel' and spoken_basis(i['key']) == 'unclear')
no_text = sum(1 for i in items if i['kind'] == 'reel' and not i['on_screen'])
md = ['# MeBook: 50 best performing hooks', '',
      'Read 15 / 11 / 2026. Three lists of 50: what is written on screen, what is said first, and the first line of the caption.', '',
      '## How it was measured', '',
      f"- Source: every Reel on the Reels tab of instagram.com/mebook.ai ({reel_n} Reels, 21 / 07 / 2024 to 22 / 10 / 2026), ranked by the play count the grid showed on 15 / 11 / 2026 (Instagram plays, plus Facebook plays when cross-posted). Most are collabs: \"Posted by\" is the account that posted it, and its audience drives the reach, so a high number says as much about the creator as about the hook.",
      f"- {no_speech} of the {reel_n} Reels have no speech in the first 12 seconds, {unclear} more have speech too unclear to transcribe, and {no_text} have no text on screen in the first 4.5 seconds; each list skips the Reels that have no hook of its kind, so the lists are not the same 50 Reels.",
      '- On-screen: read from 6 frames between 0.2 and 4.5 seconds and copied as written. 34 of the 50 are subtitles of the spoken line (marked \"subtitles\"), so they repeat the spoken hook; the rest are titles written over the video.',
      '- Spoken: a local Hebrew transcript of the first 12 seconds, corrected against the Reel\'s own subtitles where it has them (43 of 50). \"(transcript)\" = from the transcript with an obvious mishearing fixed; \"(auto)\" = the transcript as it came out. [?] is a word that could not be made out.',
      '- Caption: the first line of the caption as posted, emoji included. Long dashes in MeBook\'s and the creators\' text are shown as a plain hyphen.',
      '- MeBook\'s 21 video ads in the Meta Ad Library come last, in a separate table: ads have no public numbers, so they are not ranked with the Reels.',
      '- Children\'s first names appear because they are part of the creators\' own public words.', '']
for f, rows in lists.items():
    md += [f'## {TITLES[f]}', '', '| # | Hook | Views | Posted by | Date | Link |', '|---|---|---|---|---|---|']
    for n, it in enumerate(rows, 1):
        hook = it[f].replace('|', '/')
        if f == 'on_screen' and it.get('on_screen_kind') == 'subtitles':
            hook += ' (subtitles)'
        if f == 'spoken' and it.get('spoken_basis') == 'auto+edit':
            hook += ' (transcript)'
        if f == 'spoken' and it.get('spoken_basis') == 'auto':
            hook += ' (auto)'
        md.append(f"| {n} | {hook} | {it['views']:,} | {it['account']} | {it['date']} | [open]({it['url']}) |")
    md.append('')
md += ['## Appendix: MeBook\'s 21 video ads (no public numbers)', '',
       'Meta Ad Library, Israel, page MeBook.AI מיבוק, all video ads shown on 15 / 11 / 2026, in the Library\'s own \"total impressions\" order (Meta\'s ordering, no figures shown). The same video often runs under several ad texts.', '',
       '| # | On screen | Spoken | Ad text (first line) | Started | Link |', '|---|---|---|---|---|---|']
for it in [i for i in items if i['kind'] == 'ad']:
    sp = it['spoken'] or ''
    if sp and it.get('spoken_basis') == 'auto':
        sp += ' (auto)'
    md.append(f"| {it['ad_rank']} | {it['on_screen'].replace('|','/') or 'none'} | {sp.replace('|','/') or 'none'} | {it['caption'].replace('|','/')} | {it['date']} | [open]({it['url']}) |")
md.append('')
open(W('mebook-hooks.md'), 'w').write(re.sub('[\u2013\u2014]', '-', '\n'.join(md)))
print({f: len(v) for f, v in lists.items()}, 'no transcript yet:', sum(1 for i in items if i['spoken'] is None))
