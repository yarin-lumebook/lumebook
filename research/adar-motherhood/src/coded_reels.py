"""My coding of the 34 selected Reels (22 top, 12 same-period controls) from frames read on 11 Nov 2026.
hook = on-screen text in the first 1 to 3 s (my reading; quotes kept short). Writes data/coded.json + prints summary."""
import json, statistics as st
H = {  # code: (hook text, hook type, husband central, speech, caption CTA type)
 'C35YBBIMXF8': ('וועלייה 🤷🏽‍♀️🥹🤣', 'cute moment + one word reaction', False, 'none', 'none'),
 'DQU5Q8aDEUy': ('כשסגרתם חופשה ואתם שומרים טהרה', 'when X + Y situation', True, 'none', 'none'),
 'DFJJcG2MjR3': ('כשכולם כבר התרגלו אבל אנחנו לא 💔', 'when X situation (emotional)', True, 'none', 'none'),
 'DJ7G3SysUH_': ('POV: אתם בחופשה בת 12 ימים ואל על לא שלחו לבעלך את המזוודה', 'POV situation', True, 'none', 'none (series callback in caption)'),
 'DZVdqUesJ42': ('אדר עם מי היית נתקעת באי בודד?', 'question someone asked her', True, 'none', 'none (גברים תלמדו)'),
 'DVTrVFnDNsq': ('איראן, כולם הלכו בבי', 'news moment', True, 'none', 'none'),
 'DZsr9PJMd3X': ('ככה נראה הדבר הכי נורמלי בעולם: נולדה בבית, בת שנתיים ועדיין יונקת, בלי מעון וגן', 'provocative claim + facts on screen', False, 'none', 'none'),
 'DQ7UzJpjE-C': ('עד מתי את מתכוונת להניק אותו? / בטח 6 חודשים? לא להגזים!', 'quoted judgement + reveal', False, 'none', 'none'),
 'DTdPCoujLwR': ('יש סופה אבל את ובעלך משוגעים קצת', 'situation', True, 'none', 'comment keyword (סופה for the location)'),
 'DRRyPAsjKR1': ('POV ילדת לעצמך את המחזר האולטימטיבי', 'POV situation + dialogue subtitles', True, 'none', 'none'),
 'DZMqvUVMBFw': ('POV כשאתה אבא לוחם במילואים ... אבל המציאות ברקע', 'POV situation', True, 'husband talks to camera (selfie)', 'none'),
 'DPt9p5-jKKW': ('list of hard life facts, then 10 years later', 'before and after life story', False, 'song only', 'none'),
 'DagO9hcsqu-': ('אין לי שום כוונה להכניס את הילדים שלי למסגרות', 'manifesto: what we will not do', False, 'music (transcript unusable)', 'none'),
 'DZlI-GDs3LU': ('״לא יכול להיות שהבת שלך עושה קקי בשירותים מגיל חצי שנה״', 'quoted disbelief + talking to camera', False, 'talks in the moment', 'comment question (next video from your question)'),
 'DZNYh28ME9c': ('השפע שלך זה האישה שלך והמשפחה', 'reminder (before Shabbat flowers)', True, 'none', 'none'),
 'Dct6IBGs75z': ('חינוך ביתי ב 1 לספטמבר 🎉', 'contrast meme', False, 'none', 'none'),
 'DWBPINWjJYT': ('2018: אף אחד לא חשב שנחזיק', 'then and now (couple)', True, 'none', 'none'),
 'DQJ1FV2jOir': ('״איך היא תעלה במשקל אם את רק מניקה אותה?״ + נולדה בשבוע 36, 2.450 ק״ג', 'quoted judgement + reveal', False, 'none', 'advice'),
 'DcySiZZMgKL': ('מערכת החינוך לוקחת ילדים שנולדו סקרנים / מלמדת אותם לשבת, לשתוק ולציית', 'provocative claim', False, 'none', 'none'),
 'DXSSgG-DI8_': ('למה "מכות" עם אבא זה דווקא דבר בריא ⬇️ בפוסט', 'counterintuitive claim + read the caption', True, 'none', 'read the caption'),
 'DcBnaTvslVM': ('את רוצה שהבת שלך תתחתן עם גבר? / תדאגי שאבא שלה גם יהיה גבר', 'question + turn', True, 'none', 'none'),
 'DYxWeYfMT35': ('מה איך גמלת אותם מחיתולים לפני גיל 2? / גם לילה גם יום / זה מה שחברות החיתולים לא רוצים שתדעו', 'quoted question + reveal + secret', False, 'voiceover, hook spoken at 0.2 s, CTA spoken at 41 s', 'comment keyword (כלים for 5 tools)'),
 # controls
 'DEf91ZWsVni': ('is this / i like this (English trend text)', 'trend text, no situation', False, 'none', 'none'),
 'DIJHvHpMwI1': ('קובעת חופשה לפי המרקם של החול, חצץ, אבנים', 'situation (mild)', False, 'none', 'none'),
 'DKUJiRKs4as': ('כשאתם מתווכים לבן 3 שלכם שיום למחרת חוזרים לארץ ואבא חוזר למילואים (20 words)', 'when X situation (long)', True, 'child talks', 'none'),
 'DMbILYBsQA2': ('איך נראה הפרש של שנה ו 8 חודשים', 'show-and-tell', False, 'none', 'none'),
 'DOl_CNbDBJC': ('כששואלים אותי מה הבן 3 שלי מפספס בגן', 'quoted question, ordinary answer', False, 'none', 'none'),
 'DShwTaejCtA': ('(no on-screen text)', 'none', True, 'none', 'none'),
 'DT2tz3FDHB_': ('(no on-screen text)', 'none', False, 'none', 'none'),
 'DVeruC8DJLl': ('תאמני את המוח שלך ... רק תתחילי לחפש', 'motivation over dance', False, 'music (transcript unusable)', 'none'),
 'DXkRprEDCis': ('שהגבר שלך הוא השראה לגברים שמכוונים גבוה יותר', 'praise (abstract)', True, 'none', 'none'),
 'DZ8C-9OK0Ml': ('reply-to-comment sticker + להלן נועה בת 2, הסופר מפונקת עם הקשיים החברתיים שלי 🙄', 'reply to a critic (sarcasm)', False, 'none', 'follow + ask me'),
 'DbTVmUrM5ku': ('״אבל מה עושים עם הילדים בחינוך ביתי כל היום?!״', 'quoted question, ordinary answer', False, 'none', 'follow'),
 'DcOj03nMwRl': ('״מה ילדים בחינוך ביתי לומדים?!״', 'quoted question, ordinary answer', False, 'none', 'comment question + follow'),
}

FAMILY = {  # hook type -> family used in report.md section 2
 'quoted judgement + reveal': 'quoted judgement, fact on screen', 'quoted disbelief + talking to camera': 'quoted judgement, fact on screen',
 'quoted question + reveal + secret': 'quoted judgement, fact on screen', 'quoted question, ordinary answer': 'quoted question, ordinary answer',
 'POV situation': 'when / POV situation', 'POV situation + dialogue subtitles': 'when / POV situation', 'when X + Y situation': 'when / POV situation',
 'when X situation (emotional)': 'when / POV situation', 'situation': 'when / POV situation', 'situation (mild)': 'when / POV situation', 'when X situation (long)': 'when / POV situation',
 'provocative claim + facts on screen': 'norm breaking or counterintuitive claim', 'provocative claim': 'norm breaking or counterintuitive claim',
 'manifesto: what we will not do': 'norm breaking or counterintuitive claim', 'counterintuitive claim + read the caption': 'norm breaking or counterintuitive claim',
 'question + turn': 'question then a turn', 'question someone asked her': 'question then a turn',
 'then and now (couple)': 'time contrast or life story', 'before and after life story': 'time contrast or life story',
 'cute moment + one word reaction': 'cute moment, one word reaction',
 'news moment': 'news moment, reminder or meme', 'reminder (before Shabbat flowers)': 'news moment, reminder or meme', 'contrast meme': 'news moment, reminder or meme',
 'reply to a critic (sarcasm)': 'reply to a critic', 'show-and-tell': 'weak or none', 'none': 'weak or none', 'trend text, no situation': 'weak or none',
 'motivation over dance': 'weak or none', 'praise (abstract)': 'weak or none',
}
R = '/Users/yarinbruner/Claude/Projects/Lumebook/research/adar-motherhood'
info = json.load(open(f'{R}/data/info_2026-11-11.json')); sel = {r['code']: r for r in json.load(open(f'{R}/data/selected.json'))}
out = []
for c, (hook, typ, hus, sp, cta) in H.items():
    v = info[c]
    out.append(dict(code=c, group=sel[c]['group'], date=sel[c]['date'], plays=v['pc'], likes=v['lk'], comments=v['cm'], dur=round(v['dur'] or 0, 1),
                    audio=v['audio'], hook_on_screen=hook, hook_type=typ, hook_family=FAMILY[typ], husband_central=hus, speech=sp, caption_cta=cta,
                    caption_words=len(v['cap'].split()), comments_per_1k=round(v['cm'] / v['pc'] * 1000, 2), likes_per_1k=round(v['lk'] / v['pc'] * 1000, 1)))
json.dump(out, open(f'{R}/data/coded.json', 'w'), ensure_ascii=False, indent=1)
import collections
for g in ('top', 'control'):
    print(g, collections.Counter(r['hook_family'] for r in out if r['group'] == g).most_common())
    x = [r for r in out if r['group'] == g]
    print(g, len(x), 'speech', sum(r['speech'] not in ('none','song only') and not r['speech'].startswith('music') for r in x), 'husband central', sum(r['husband_central'] for r in x), 'no on-screen hook', sum(r['hook_type'] == 'none' for r in x),
          'quoted judgement/question', sum('quoted' in r['hook_type'] for r in x), 'POV/when situation', sum(('POV' in r['hook_type']) or ('situation' in r['hook_type']) for r in x),
          'asks for an action', sum(not r['caption_cta'].startswith('none') and r['caption_cta'] != 'advice' for r in x),
          'median dur', st.median(r['dur'] for r in x), 'median caption words', st.median(r['caption_words'] for r in x))
