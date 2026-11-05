# Builds lumebook-kids-content-lab.html from analysis/*/meta.json + breakdown.json + frames, src/app.html, src/synthesis.json.
# Run from research/kids-brand-content-research/:  ~/.claude/skills/watch-video/.venv/bin/python src/build.py
# Look and chrome come from the LumeBook design system (shared/design): design.head() inlines the stylesheet,
# design.logo_data_uri() the logo; src/base.css holds the lab's own page rules.
import json, glob, os, sys, re, io, base64, datetime
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.dirname(os.path.dirname(ROOT))
sys.path.insert(0, os.path.join(PROJECT, 'shared', 'design'))
import design
os.chdir(ROOT)
T = open('src/app.html').read()
LOGO = design.logo_data_uri()
BASECSS = open('src/base.css').read()

def thumb(path, w=180):
    im = Image.open(path).convert('RGB')
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=62, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

MIN_T = {'analysis/ig_DbsxBSLMyOO': 5.0}  # skip body-forward opening frames; show stills from the reveal on

def frames_for(d, b):
    idx = json.load(open(f'{d}/frames/index.json'))
    allf = [f for f in idx['frames'] if f['t'] >= MIN_T.get(d, 0)]
    by_name = {os.path.basename(f['file']): f for f in allf}
    pick = [allf[0]]
    for c in b.get('frames_cited', []):
        f = by_name.get(os.path.basename(c))
        if f and f not in pick: pick.append(f)
    # top up with evenly spaced frames to at least 6
    if len(pick) < 6:
        step = max(1, len(allf) // 6)
        for f in allf[::step]:
            if f not in pick: pick.append(f)
            if len(pick) >= 6: break
    pick = sorted(pick[:8], key=lambda f: f['t'])
    return [{'t': round(f['t'], 1), 's': thumb(f['file'])} for f in pick]

EXCLUDE = {'analysis/ai_yt_hrlxvmyhva0'}  # frames show a real toddler's bare bottom in close-up; not shown on the page
V = []
for d in sorted(glob.glob('analysis/*')):
    if d in EXCLUDE: continue
    if not (os.path.exists(f'{d}/meta.json') and os.path.exists(f'{d}/breakdown.json') and os.path.exists(f'{d}/frames/index.json')):
        continue
    m = json.load(open(f'{d}/meta.json')); b = json.load(open(f'{d}/breakdown.json'))
    ud = m.get('upload_date') or ''
    V.append({
        'id': m['id'], 'plat': m['platform'], 'ctry': m['country'], 'url': m.get('url'),
        'acct': m.get('account'), 'owner': m.get('post_owner'), 'views': m.get('views'), 'likes': m.get('likes'),
        'cmts': m.get('comments'), 'med': m.get('account_median_views'), 'ox': m.get('outlier_x'), 'lr': m.get('like_rate_pct'),
        'dur': m.get('duration_s') or json.load(open(f'{d}/frames/index.json')).get('duration'), 'date': f'{ud[:4]}-{ud[4:6]}-{ud[6:]}' if len(ud) == 8 else ud,
        'cap': (m.get('caption') or '')[:900], 'src': m.get('source', 'scan'), 'aiHow': m.get('ai_made_how'),
        'b': b, 'th': frames_for(d, b)})

SYN = json.load(open('src/synthesis.json'))
SYN['lede'] = SYN['lede'].replace('__N__', str(len(V)))
stamp = '6 Oct 2026'  # the research date; later rebuilds (restyles) must not relabel it
n_il = sum(v['ctry'] == 'IL' for v in V)
T = (T.replace('__LBHEAD__', design.head())
      .replace('__BASECSS__', BASECSS).replace('__LOGO__', LOGO)
      .replace('__DATA__', json.dumps(V, ensure_ascii=False)).replace('__SYN__', json.dumps(SYN, ensure_ascii=False))
      .replace('__STAMP__', stamp).replace('__H1__', SYN['h1']).replace('__LEDE__', SYN['lede'])
      .replace('__METHOD__', SYN['method_html'])
      .replace('__DESC__', f"{len(V)} kids-brand short videos watched and broken down ({n_il} Israeli), with formats a solo creator can shoot, edit or make with AI"))
out = 'lumebook-kids-content-lab.html'
T = T.replace('\u2014', ' - ')  # quoted third-party captions can contain em dashes; the user never wants them on the page
open(out, 'w').write(T)
assert '—' not in T, 'em dash found in output'
print(out, len(V), 'videos', round(len(T) / 1e6, 2), 'MB')
