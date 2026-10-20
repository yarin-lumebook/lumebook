"""Add my verification verdicts for round-2 Reels to review.json.
python3 add_review.py verdicts.json   where verdicts = {CODE: {"approach": "...", "status": "verified|excluded", "note": "...", "why": "..."}}
why and lesson default to the agent's coding (format, lumebook_lesson) when I give no note; inspected = agent coding + my 10-frame check."""
import json, re, sys
R = json.load(open('review.json', encoding='utf-8'))
V = json.load(open(sys.argv[1], encoding='utf-8'))
for code, v in V.items():
    c = json.load(open(f'coded/{code}.json', encoding='utf-8'))
    lesson = re.sub(r'^\s*Interpretation:\s*', '', str(c.get('lumebook_lesson') or '')).strip()
    lesson = re.split(r'(?<=[.!?])\s', lesson)[0] if lesson else ''
    disc = c.get('disclosure_visible') or ''
    co = ''
    R[code] = {
        'status': v.get('status', 'verified'),
        'approach': v.get('approach', ''),
        'why': v.get('why') or (str(c.get('format') or '')[:140].rstrip('.') + '.'),
        'lesson': v.get('note') or lesson,
        'commercial': v.get('commercial') or ('Collaboration post, see disclosure' if 'collab' in str(c.get('relationship', '')).lower() else 'Unknown or none evident'),
        'disclosure': str(disc)[:160],
        'inspected': 'agent coding + my 10-frame check',
        'deep': '',
        'round': 2,
    }
    if v.get('product'):
        R[code]['product'] = v['product']
json.dump(R, open('review.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(V), 'added;', sum(1 for k, r in R.items() if not k.startswith('_') and r['status'] == 'verified'), 'verified in total')
