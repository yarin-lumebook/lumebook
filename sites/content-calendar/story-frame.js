/* LBStory (19 Nov 2026): ONE renderer for a story frame, 1080 x 1920. The calendar's story editor draws the live preview with it and
   tools/stories.py draws the PNG that goes to Postiz with it (the same file in headless Chrome), so the preview is the export.
   A frame is data: {bg: {src, x, y, zoom, fill}, scrim: {top, bottom}, layers: [text | image | shape | sticker]}.
   Positions are canvas pixels (left x, top y, width w). Text keeps **word** as a gold emphasis and \n as a line break.
   Stickers are placeholders for what Instagram adds by hand (link, poll, question, countdown): the editor shows them dashed,
   the export never draws them (Postiz cannot send stickers). */
(function (root) {
  "use strict";
  var W = 1080, H = 1920, SAFE_TOP = 250, SAFE_BOTTOM = 340;
  var STICKERS = { link: "מדבקת קישור", poll: "סקר", question: "תיבת שאלה", countdown: "ספירה לאחור", mention: "תיוג", emoji: "מחוון אימוג'י" };

  function esc(t) { return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function num(v, d) { v = +v; return isFinite(v) ? v : d; }
  function url(base, src) { return /^(https?:|data:|blob:|file:)/.test(src) ? src : (base || "/") + String(src).split("/").map(encodeURIComponent).join("/"); }

  /* dates written dd / mm (/ yyyy) stay left to right inside Hebrew, or the line shows 12 / 04 for 04 / 12 */
  function dates(h) { return h.replace(/(\d{1,2} \/ \d{1,2}(?: \/ \d{2,4})?)/g, '<span dir="ltr" style="unicode-bidi:isolate">$1</span>'); }
  function rich(text, accent) {
    return dates(esc(text)).replace(/\*\*(.+?)\*\*/g, '<b class="hl" style="color:' + esc(accent || "#F5C26B") + '">$1</b>').replace(/\n/g, "<br>");
  }

  function css(base) {
    var f = (base || "/") + "shared/brand/fonts/";
    return '@font-face{font-family:"LBHeebo";src:url("' + f + 'Heebo-Black.ttf");font-weight:900}' +
      '@font-face{font-family:"LBHeebo";src:url("' + f + 'Heebo-Bold.ttf");font-weight:700}' +
      '@font-face{font-family:"LBAssistant";src:url("' + f + 'Assistant-VariableFont_wght.ttf");font-weight:200 800}' +
      ".stf{position:relative;width:1080px;height:1920px;overflow:hidden;direction:rtl;background:#2B0E6E;font-family:LBHeebo,Heebo,Assistant,'Arial Hebrew',sans-serif;color:#fff;-webkit-font-smoothing:antialiased}" +
      ".stf *{box-sizing:border-box}.stf-bg{position:absolute;inset:0;width:100%;height:100%}.stf-bg img{width:100%;height:100%;object-fit:cover;display:block}" +
      ".stf-l{position:absolute;margin:0}.stf-t{white-space:normal;overflow-wrap:break-word;unicode-bidi:plaintext}" +
      ".stf-l img{display:block;width:100%;height:auto}.stf .hl{font-weight:inherit}" +
      ".stf-blur{position:absolute;overflow:hidden}.stf-l .stf-blur img{position:absolute;max-width:none;display:block}" +
      ".stf-st{border:5px dashed rgba(255,255,255,.9);border-radius:36px;background:rgba(0,0,0,.28);display:flex;align-items:center;justify-content:center;text-align:center;font:700 38px/1.2 LBHeebo,sans-serif;color:#fff;padding:12px}" +
      ".stf-safe{position:absolute;left:0;right:0;pointer-events:none;border:0 dashed}";   /* its colours: the editor's page.css */
  }

  function bgHtml(fr) {
    var b = fr.bg || {}, o = fr.__o || {};
    var h = '<div class="stf-bg" style="background:' + esc(b.fill || "#2B0E6E") + '">';
    if (b.src) {
      var x = num(b.x, 50), y = num(b.y, 50), z = num(b.zoom, 100) / 100;
      h += '<img src="' + esc(url(o.base, b.src)) + '" alt="" style="object-position:' + x + "% " + y + "%;transform:scale(" + z + ");transform-origin:" + x + "% " + y + '%">';
    }
    h += "</div>";
    var sc = fr.scrim || {};
    if (num(sc.top, 0) > 0) h += '<div class="stf-l" style="left:0;top:0;width:1080px;height:760px;background:linear-gradient(rgba(14,4,48,' + num(sc.top, 0) + '),rgba(14,4,48,0))"></div>';
    if (num(sc.bottom, 0) > 0) h += '<div class="stf-l" style="left:0;bottom:0;width:1080px;height:760px;background:linear-gradient(rgba(14,4,48,0),rgba(14,4,48,' + num(sc.bottom, 0) + '))"></div>';
    return h;
  }

  function layerHtml(l, o) {
    var x = num(l.x, 0), y = num(l.y, 0), w = num(l.w, 800), op = num(l.op, 100) / 100;
    var base = "left:" + x + "px;top:" + y + "px;width:" + w + "px;" + (op < 1 ? "opacity:" + op + ";" : "") + (l.rot ? "transform:rotate(" + num(l.rot, 0) + "deg);" : "");
    var at = ' data-lid="' + esc(l.id || "") + '"';
    if (l.type === "text") {
      var sz = num(l.size, 80), st = base + "font-size:" + sz + "px;line-height:" + num(l.lh, 1.12) + ";font-weight:" + (+l.weight === 700 ? 700 : 900) + ";color:" + esc(l.color || "#FFFFFF") + ";text-align:" + (["left", "right", "center"].indexOf(l.align) >= 0 ? l.align : "center") + ";";
      if (l.font === "assistant") st += "font-family:LBAssistant,Assistant,sans-serif;";
      if (l.shadow) st += "text-shadow:0 4px 24px rgba(10,2,40,.65),0 2px 4px rgba(10,2,40,.5);";
      if (l.pill) st += "background:" + esc(l.pill) + ";border-radius:" + num(l.pillr, 40) + "px;padding:" + num(l.pad, 28) + "px;";
      return '<div class="stf-l stf-t"' + at + ' dir="rtl" style="' + st + '">' + rich(l.text, l.accent) + "</div>";
    }
    if (l.type === "image") {
      var st2 = base + (l.radius ? "border-radius:" + num(l.radius, 0) + "px;overflow:hidden;" : "") + (l.shadow ? "box-shadow:0 24px 70px rgba(10,2,40,.5),0 4px 14px rgba(10,2,40,.35);" : "") + (l.bg ? "background:" + esc(l.bg) + ";" : "");
      /* blurs: boxes in % of the picture (names and faces on a review screenshot, Yarin 19 Nov 2026: "blur the names"); each is the same
         picture, blurred and clipped to the box, so it moves and scales with the picture and is part of the PNG */
      var src = esc(url(o.base, l.src || "")), bl = "";
      (l.blurs || []).forEach(function (b, i) {
        var bx = num(b.x, 0), by = num(b.y, 0), bw = Math.max(0.5, num(b.w, 10)), bh = Math.max(0.5, num(b.h, 10));
        bl += '<div class="stf-blur' + (o.editor ? " is-ed" : "") + '" data-bi="' + i + '" style="left:' + bx + "%;top:" + by + "%;width:" + bw + "%;height:" + bh + '%">' +
          '<img src="' + src + '" alt="" style="left:' + (-bx / bw * 100) + "%;top:" + (-by / bh * 100) + "%;width:" + (10000 / bw) + "%;height:" + (10000 / bh) + "%;filter:blur(" + num(l.blur, 16) + 'px)"></div>';
      });
      return '<div class="stf-l"' + at + ' style="' + st2 + '"><img src="' + src + '" alt="">' + bl + "</div>";
    }
    if (l.type === "shape") {
      return '<div class="stf-l"' + at + ' style="' + base + "height:" + num(l.h, 200) + "px;background:" + esc(l.fill || "#FFFFFF") + ";border-radius:" + num(l.radius, 0) + "px;" + (l.border ? "border:" + num(l.bw, 4) + "px solid " + esc(l.border) + ";" : "") + '"></div>';
    }
    if (l.type === "sticker") {
      if (!o.editor) return "";
      return '<div class="stf-l stf-st"' + at + ' style="' + base + "height:" + num(l.h, 150) + 'px">' + dates(esc(l.label || STICKERS[l.kind] || "מדבקה")) + "<br>(להוסיף באפליקציה)</div>";
    }
    return "";
  }

  /* o: {base: where files are served from ("/" in the page, file:///<project>/ in the export), editor: show stickers and the safe zones} */
  function frameHtml(fr, o) {
    o = o || {};
    fr = Object.assign({}, fr, { __o: o });
    var h = '<div class="stf" data-frame="1" translate="no" dir="rtl">' + bgHtml(fr);
    (fr.layers || []).forEach(function (l) { h += layerHtml(l, o); });
    if (o.editor && o.safe) {
      h += '<div class="stf-safe" style="top:0;height:' + SAFE_TOP + 'px;border-bottom-width:4px"></div><div class="stf-safe" style="bottom:0;height:' + SAFE_BOTTOM + 'px;border-top-width:4px"></div>';
    }
    return h + "</div>";
  }

  root.LBStory = { W: W, H: H, SAFE_TOP: SAFE_TOP, SAFE_BOTTOM: SAFE_BOTTOM, STICKERS: STICKERS, frameHtml: frameHtml, css: css, rich: rich };
})(window);
