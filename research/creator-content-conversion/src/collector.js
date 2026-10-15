// Instagram collector used on 14 Oct 2026 in the built-in browser pane, signed in, read-only
// (no follows, likes, comments or messages). Paste each block into the page with the javascript tool;
// Instagram's CSP blocks eval, so code goes inline, and a hard page load wipes these functions.
//
// Step 0: capture three request bodies Instagram's own profile page sends. Install a fetch/XHR hook
// that stores {url, body, text} in window.__cap, move to a profile with
//   history.pushState({}, '', '/<handle>/'); dispatchEvent(new PopStateEvent('popstate', {state: {}}));
// (and to '/<handle>/reels/'), then copy the POST bodies whose fb_api_req_friendly_name is
// PolarisProfilePostsQuery -> window.__tlbody, PolarisProfileReelsTabContentQuery -> window.__rlbody,
// PolarisProfilePageContentQuery -> window.__pcbody. They expire with the session.

(() => {
  const H = (p, name, root) => ({'content-type': 'application/x-www-form-urlencoded', 'x-fb-friendly-name': name,
    'x-ig-app-id': '936619743392459', 'x-csrftoken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1],
    'x-fb-lsd': p.get('lsd'), 'x-asbd-id': '359341', ...(root ? {'x-root-field-name': root} : {})});
  const post = async (url, p, name, root) => {
    const r = await fetch(url, {method: 'POST', credentials: 'include', body: p.toString(), headers: H(p, name, root)});
    const t = await r.text(); if (t[0] !== '{') throw new Error('HTTP ' + r.status + ' ' + t.slice(0, 80)); return JSON.parse(t);
  };
  const pickImg = (iv) => { const c = (iv && iv.candidates) || []; if (!c.length) return null;
    return c.slice().sort((a, b) => Math.abs(a.width - 720) - Math.abs(b.width - 720))[0].url; };
  const pickVid = (vv) => { if (!vv || !vv.length) return null; const s = vv.slice().sort((a, b) => (a.width || 0) - (b.width || 0));
    return (s.find(x => x.width >= 480) || s[s.length - 1]).url; };
  const compact = (n) => ({
    code: n.code, pk: n.pk, t: n.taken_at, pt: n.product_type, mt: n.media_type, ncar: n.carousel_media_count,
    likes: n.like_count, com: n.comment_count, fbl: n.fb_like_count, fbc: n.fb_comment_count, rep: n.media_repost_count,
    hid: n.like_and_view_counts_disabled, paid: n.is_paid_partnership,
    spons: (n.sponsor_tags || []).map(s => s.sponsor && s.sponsor.username || s.username),
    coa: (n.coauthor_producers || []).map(u => u.username), owner: n.user && n.user.username, ownerpk: n.owner_id && n.owner_id.pk,
    tags: ((n.usertags && n.usertags.in) || []).map(u => u.user && u.user.username).slice(0, 15),
    pin: (n.timeline_pinned_user_ids || []).length > 0,
    cap: n.caption && n.caption.text, alt: n.accessibility_caption, loc: n.location && n.location.name,
    aud: n.clips_metadata && n.clips_metadata.music_info ? 'music' : (n.clips_metadata && n.clips_metadata.original_sound_info ? 'original' : null),
    img: pickImg(n.image_versions2), vid: pickVid(n.video_versions),
    slides: (n.carousel_media || []).slice(0, 20).map(m => ({img: pickImg(m.image_versions2), vid: pickVid(m.video_versions), alt: m.accessibility_caption}))
  });

  // Posts (grid order is not date order: stop after 2 pages with nothing newer than 200 days, max 7 pages),
  // profile (exact follower count, bio) and reels-tab play counts (max 5 pages).
  window.__collect = async (username) => {
    const now = Date.now() / 1000, cut = now - 200 * 86400;
    const posts = []; let after = null, pages = 0, emptyRun = 0, pk = null;
    while (pages < 7) {
      const p = new URLSearchParams(window.__tlbody); const v = JSON.parse(p.get('variables')); v.username = username;
      if (after) { v.after = after; v.before = null; v.first = 12; v.last = null; }
      p.set('variables', JSON.stringify(v));
      const j = await post('https://www.instagram.com/graphql/query', p, 'PolarisProfilePostsQuery', 'xdt_api__v1__feed__user_timeline_graphql_connection');
      const conn = j.data && j.data.xdt_api__v1__feed__user_timeline_graphql_connection;
      if (!conn) return {username, err: 'no timeline'};
      pages++;
      const ns = conn.edges.map(e => e.node);
      if (!pk && ns.length) pk = ns[0].owner_id && ns[0].owner_id.pk;
      ns.forEach(n => posts.push(compact(n)));
      const recent = ns.filter(n => n.taken_at > cut && !(n.timeline_pinned_user_ids || []).length).length;
      emptyRun = recent ? 0 : emptyRun + 1;
      if (!conn.page_info.has_next_page || (pages >= 2 && emptyRun >= 2)) break;
      after = conn.page_info.end_cursor;
    }
    let prof = null;
    if (pk) {
      const p = new URLSearchParams(window.__pcbody); const v = JSON.parse(p.get('variables')); v.id = pk; p.set('variables', JSON.stringify(v));
      const j = await post('https://www.instagram.com/api/graphql', p, 'PolarisProfilePageContentQuery'); const u = j.data && j.data.user;
      if (u) prof = {pk, fc: u.follower_count, fwing: u.following_count, mc: u.media_count, bio: u.biography, cat: u.category, priv: u.is_private};
    }
    const plays = {}; let rafter = null, rpages = 0;
    while (pk && rpages < 5) {
      const p = new URLSearchParams(window.__rlbody); const v = JSON.parse(p.get('variables'));
      v.data.target_user_id = pk; v.user_id = pk; if (rafter) v.after = rafter; p.set('variables', JSON.stringify(v));
      const j = await post('https://www.instagram.com/graphql/query', p, 'PolarisProfileReelsTabContentQuery');
      const cc = j.data && j.data.fetch__XDTUserDict && j.data.fetch__XDTUserDict.clips_connection; if (!cc) break;
      rpages++; let old = 0;
      cc.edges.forEach(e => { const m = e.node.media; plays[m.code] = {pc: m.play_count, pin: (m.clips_tab_pinned_user_ids || []).length > 0};
        const ts = m.taken_at || (Number(BigInt(m.pk) >> 23n) + 1314220021721) / 1000;
        if (ts < cut && !(m.clips_tab_pinned_user_ids || []).length) old++; });
      if (!cc.page_info.has_next_page || old >= 6) break;
      rafter = cc.page_info.end_cursor;
    }
    const out = {username, at: Math.floor(now), pages, rpages, prof, posts, plays};
    localStorage.setItem('__dj_c_' + username, JSON.stringify(out));
    return {username, n: posts.length, fc: prof && prof.fc};
  };

  // Up to 30 top-level comments in Instagram's default web order (ranked), with preview replies.
  window.__comments = async (pk, max = 30) => {
    const out = []; let min_id = null, pages = 0, meta = null;
    while (out.length < max && pages < 4) {
      const url = `/api/v1/media/${pk}/comments/?can_support_threading=true&permalink_enabled=false` + (min_id ? `&min_id=${encodeURIComponent(min_id)}` : '');
      const r = await fetch(url, {headers: {'x-ig-app-id': '936619743392459', 'x-requested-with': 'XMLHttpRequest'}, credentials: 'include'});
      const t = await r.text(); if (t[0] !== '{') return {pk, err: r.status, comments: out};
      const j = JSON.parse(t); pages++;
      if (!meta) meta = {total: j.comment_count, filter: j.comment_filter_param};
      (j.comments || []).forEach(c => out.push({id: c.pk, u: c.user && c.user.username, t: c.text, at: c.created_at,
        likes: c.comment_like_count, kids: c.child_comment_count, ranked: c.is_ranked_comment,
        replies: (c.preview_child_comments || []).map(x => ({u: x.user && x.user.username, t: x.text}))}));
      if (!j.next_min_id) break; min_id = j.next_min_id;
    }
    return {pk, meta, comments: out.slice(0, max)};
  };
  return 'ready';
})();

// Run one creator at a time (about 20 s each); export with
//   '[' + Object.keys(localStorage).filter(k => k.startsWith('__dj_c_')).map(k => localStorage.getItem(k)).join(',') + ']'
// in batches, then remove the __dj* keys.
