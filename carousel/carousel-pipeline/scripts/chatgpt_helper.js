/* Carousel Machine: the ChatGPT picture helper (30 Oct 2026; Yarin: "use my chatgpt in chrome to create the images so
   everything will be free"). Claude pastes this whole file into one ChatGPT tab with the Claude in Chrome javascript tool,
   one tab and one new chat per carousel run, then:

     LB.add([{name: "<download_as>", prompt: "<prompt>"}, ...])   // the run's jobs from chatgpt_pictures.py next
     LB.next()                                                   // types the first prompt into the message box
     ...press Return with the computer tool (the only thing that sends; a synthetic Enter or requestSubmit does not)
     LB.status()                                                 // {state, current, queued, saved, waiting_s, log}

   Every few seconds the helper looks at the newest img[alt^="Generated image"]. A src it has not seen, unchanged on two
   polls in a row, is the finished picture: it is fetched to a blob and downloaded under the job's name (into
   ~/Downloads), and the next prompt is typed. Then state is "press Return" again. Pictures already in the chat when the
   helper starts are never saved, and saved pictures are tracked by src, not by count, because long chats drop old
   images from the page. Pasting the file again keeps the queue and what was saved. */
(() => {
  const old = window.LB;
  if (old && old.timer) clearInterval(old.timer);
  const POLL_MS = 5000;
  const imgs = () => [...document.querySelectorAll('img[alt^="Generated image"]')];
  const srcOf = i => i.currentSrc || i.src || '';
  const box = () => document.querySelector('#prompt-textarea[contenteditable="true"]') || document.querySelector('[contenteditable="true"]');
  const boxText = () => { const b = box(); return b ? b.innerText.trim() : ''; };
  const LB = window.LB = {
    version: 1,
    queue: old ? old.queue : [],
    seen: new Set(old ? [...old.seen] : imgs().map(srcOf)),
    saved: old ? old.saved : [],
    current: old ? old.current : null,
    typedAt: old ? old.typedAt : 0,
    log: old ? old.log : [],
    candidate: null,
    busy: false,
  };
  LB.note = m => { LB.log.push(new Date().toTimeString().slice(0, 8) + ' ' + m); if (LB.log.length > 80) LB.log.shift(); };
  LB.add = items => {
    for (const it of [].concat(items || [])) {
      if (!it || !it.name || !it.prompt) continue;
      if (LB.queue.some(q => q.name === it.name) || (LB.current && LB.current.name === it.name)) continue;
      LB.queue.push({name: String(it.name), prompt: String(it.prompt)});
    }
    return LB.status();
  };
  LB.type = text => {
    const b = box();
    if (!b) throw new Error('ChatGPT message box not found');
    b.focus();
    document.execCommand('selectAll', false, null);
    document.execCommand('insertText', false, text);
    return b.innerText.length;
  };
  LB.next = () => {
    if (LB.current || !LB.queue.length) return LB.status();
    LB.current = LB.queue.shift();
    LB.type(LB.current.prompt);
    LB.typedAt = Date.now();
    LB.candidate = null;
    LB.note('typed ' + LB.current.name + ', press Return');
    return LB.status();
  };
  LB.retype = () => { if (LB.current) LB.type(LB.current.prompt); return LB.status(); };   // when the box was cleared by hand
  LB.skip = () => { if (LB.current) LB.note('skipped ' + LB.current.name); LB.current = null; return LB.next(); };
  LB.download = async (src, name) => {
    const blob = await (await fetch(src)).blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; a.style.display = 'none';
    document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    return blob.size;
  };
  LB.poll = async () => {
    if (!LB.current || LB.busy) return;
    const all = imgs();
    const img = all[all.length - 1];   // only the newest picture in the chat; an old one coming back is never taken for it
    const src = img ? srcOf(img) : '';
    if (!img || !src || LB.seen.has(src) || !img.complete || !img.naturalWidth) { LB.candidate = null; return; }
    if (src !== LB.candidate) { LB.candidate = src; return; }   // a new src: save it only when the next poll sees the same one
    LB.busy = true;
    const name = LB.current.name;
    try {
      const bytes = await LB.download(src, name);
      LB.seen.add(src);
      LB.saved.push({name, bytes, at: new Date().toISOString()});
      LB.note('saved ' + name + ' (' + Math.round(bytes / 1024) + ' KB)');
      LB.current = null; LB.candidate = null;
      if (LB.queue.length) LB.next();
    } catch (e) {
      LB.note('download failed for ' + name + ': ' + e.message);
    } finally {
      LB.busy = false;
    }
  };
  LB.status = () => ({
    state: !LB.current ? (LB.queue.length ? 'idle, call LB.next()' : 'done') : (boxText() ? 'press Return' : 'generating'),
    current: LB.current ? LB.current.name : null,
    queued: LB.queue.map(q => q.name),
    saved: LB.saved.map(s => s.name),
    waiting_s: LB.current ? Math.round((Date.now() - LB.typedAt) / 1000) : 0,
    log: LB.log.slice(-6),
  });
  LB.timer = setInterval(LB.poll, POLL_MS);
  return 'LB ready ' + JSON.stringify(LB.status());
})();
