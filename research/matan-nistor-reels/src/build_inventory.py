"""Inventory of every item in @matan.nistor's Reels tab, read 09 Nov 2026 from the logged-in browser pane
(PolarisProfileReelsTabContentQuery_connection, 171 pages of 12). Adds the post date decoded from the media pk,
splits Reels (product_type clips) from older feed and IGTV videos, ranks Reels by Instagram's play_count."""
import json, datetime, statistics as st, csv
a = json.load(open('inventory_raw_2026-11-09.json'))
EPOCH = 1314220021721
for x in a:
    ms = (int(x['pk']) >> 23) + EPOCH
    x['date'] = datetime.datetime.utcfromtimestamp(ms / 1000).strftime('%Y-%m-%d')
    x['collab'] = x['owner'] != 'matan.nistor' or bool(x['coauthors'])
clips = [x for x in a if x['product_type'] == 'clips']
other = [x for x in a if x['product_type'] != 'clips']
clips.sort(key=lambda x: -x['play_count'])
for i, x in enumerate(clips, 1):
    x['rank_all'] = i
json.dump({'collected': '2026-11-09', 'clips': clips, 'other_video': other}, open('inventory.json', 'w'), ensure_ascii=False, indent=0)
print('items', len(a), 'clips', len(clips), 'feed/igtv', len(other))
print('date range all', min(x['date'] for x in a), max(x['date'] for x in a))
print('date range clips', min(x['date'] for x in clips), max(x['date'] for x in clips))
pc = [x['play_count'] for x in clips]
print('plays median', st.median(pc), 'p90', sorted(pc)[int(.9*len(pc))], 'max', max(pc))
top = clips[:100]
print('top100 min plays', top[-1]['play_count'], 'collab', sum(x['collab'] for x in top), 'owner!=matan', sum(x['owner']!='matan.nistor' for x in top))
print('top100 years', {y: sum(x['date'][:4]==y for x in top) for y in sorted(set(x['date'][:4] for x in top))})
print('clips by year', {y: sum(x['date'][:4]==y for x in clips) for y in sorted(set(x['date'][:4] for x in clips))})
print('median plays by year', {y: st.median([x['play_count'] for x in clips if x['date'][:4]==y]) for y in sorted(set(x['date'][:4] for x in clips))})
ov = [x for x in other if x.get('view_count')]
ov.sort(key=lambda x: -x['view_count'])
print('feed/igtv max view_count', [(x['code'], x['view_count'], x['date']) for x in ov[:5]])
print('pinned', [(x['code'], x['rank_all'], x['play_count']) for x in clips if x['pinned']])
for x in top[:15]: print(x['rank_all'], x['code'], x['play_count'], x['like_count'], x['comment_count'], x['date'], x['owner'], x['coauthors'])
