"""Send a finished carousel to Postiz (Yarin, 26 Oct 2026).

Instagram gets all the slides with caption.txt. Facebook gets slide 1 only, with the text of slides 2 to the last written out
as the post above it. Both go in one Postiz post, scheduled for the date and time Yarin picks in Carousel Machine, or
saved as a draft (then it waits in Postiz until she schedules it there). Without a time it is the carousel's own day at
default_hour (shared/facts.json postiz).

    python3 carousel/carousel-pipeline/scripts/postiz_export.py approved/DATE-ID --dry-run                    # show what would be sent
    python3 carousel/carousel-pipeline/scripts/postiz_export.py approved/DATE-ID --at 2026-10-27T20:30         # schedule it
    python3 carousel/carousel-pipeline/scripts/postiz_export.py approved/DATE-ID --draft                      # a draft only

The words always come from caption.txt and the slides; their punctuation and the two emojis (hook, and 🔖 on the CTA; Yarin,
26 Oct 2026) from the option's post_text, which the pipeline writes since 26 Oct 2026, or a hand written
RUN_DIR/final/postiz-text.json ({"caption": ..., "fb_text": ...}), so a later edit keeps them (carousel_lib.post_texts).

Carousel Machine calls send() from its "לתזמן" and "טיוטה בלבד" buttons (review_server.py /api/production/postiz).
The result is kept in RUN_DIR/postiz.json. Needs the postiz CLI signed in (`postiz auth:status`).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel_lib as lib  # noqa: E402
import compose_slides  # noqa: E402  (story copy: is_story, plain_text)
import drive_export  # noqa: E402  (final_slides: this carousel's own slide count)

CLI_DIRS = (Path.home() / ".local" / "bin", Path("/usr/local/bin"), Path("/opt/homebrew/bin"))


def config():
    return lib.read_json(lib.ROOT / "shared" / "facts.json").get("postiz") or {}


def slides_of(run_dir):
    return drive_export.final_slides(run_dir)


def _plain(frozen):
    """The option as a parent reads it: a story option's slides without the ## label, > card and **emphasis** markup
    (story-format.md section 3), so the Facebook text never shows the asterisks. Other options are returned as they are."""
    option = frozen["option"]
    if not compose_slides.is_story(frozen):
        return option
    return {**option, "slides": [dict(s, headline=compose_slides.plain_text(s.get("headline", "")),
                                         body=compose_slides.plain_text(s.get("body", ""))) for s in option.get("slides", [])]}


def texts(run_dir):
    """The Instagram caption and the Facebook text from the current caption and slides, punctuated and with the hook
    and save emojis as in postiz-text.json (hand written) or the option's post_text (the pipeline's, since 26 Oct 2026)."""
    run_dir = Path(run_dir)
    option = _plain(lib.read_json(run_dir / "approved.json"))
    own = run_dir / "final" / "postiz-text.json"
    option = {**option, "caption": (run_dir / "final" / "caption.txt").read_text(encoding="utf-8").strip() or option.get("caption", "")}
    return lib.post_texts(option, lib.read_json(own) if own.exists() else None)


def fb_text(run_dir):
    return lib.fb_source(_plain(lib.read_json(Path(run_dir) / "approved.json")))


def default_date(run_dir, now=None):
    """The carousel's day at default_hour, Israel time; a day already past moves to an hour from now."""
    now = now or lib.now_local()
    day = dt.date.fromisoformat(lib.read_json(Path(run_dir) / "approved.json")["date"])
    when = dt.datetime.combine(day, dt.time(int(config().get("default_hour", 6))), tzinfo=now.tzinfo)
    if when < now + dt.timedelta(minutes=30):
        when = (now + dt.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return when


def slots(count, first=None, every=2, hour=None):
    """The next `count` posting times (Yarin, 28 Oct 2026: "every other day starting friday morning and skipping every
    saturday"): `first` (a date, default the next Friday on or after today), then every `every` days at default_hour,
    Israel time. A slot that lands on a Saturday moves to the Sunday and the count restarts there (Fri 30 Oct, Sun 1,
    Tue 3, Thu 5, Sun 8, Tue 10, Thu 12, Sun 15, ...). Only a plan: nothing is sent or changed in Postiz by this."""
    now = lib.now_local()
    day = first or now.date() + dt.timedelta(days=(4 - now.date().weekday()) % 7)   # Monday 0, Friday 4
    hour = int(config().get("default_hour", 6)) if hour is None else hour
    out = []
    while len(out) < count:
        if day.weekday() == 5:
            day += dt.timedelta(days=1)
        out.append(dt.datetime.combine(day, dt.time(hour), tzinfo=now.tzinfo))
        day += dt.timedelta(days=every)
    return out


def parse_when(text, now=None):
    """A time from the page's picker (2026-10-27T20:30, this Mac's time zone). A scheduled time has to be ahead."""
    now = now or lib.now_local()
    try:
        when = dt.datetime.fromisoformat(str(text))
    except ValueError:
        raise ValueError("תאריך ושעה לא תקינים")
    return when if when.tzinfo else when.replace(tzinfo=now.tzinfo)


def _env():
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([str(d) for d in CLI_DIRS] + [env.get("PATH", "")])
    return env


def _cli(*args, timeout=120):
    exe = shutil.which("postiz", path=_env()["PATH"])
    if not exe:
        raise RuntimeError("הכלי postiz לא מותקן במחשב (npm install -g --prefix ~/.local postiz)")
    p = subprocess.run([exe, *args], capture_output=True, text=True, timeout=timeout, env=_env())
    out = p.stdout.strip()
    if p.returncode != 0:
        raise RuntimeError(f"Postiz: {(p.stderr or out).strip()[-600:]}")
    start = min((i for i in (out.find("{"), out.find("[")) if i >= 0), default=-1)
    if start < 0:
        raise RuntimeError(f"Postiz: unexpected answer: {out[-300:]}")
    return json.loads(out[start:])


def _upload(path, tries=4):
    """postiz upload, again after a pause when Postiz answers 502 (26 Oct 2026: two runs in a row failed that way)."""
    for n in range(tries):
        try:
            return _cli("upload", str(path))["path"]
        except RuntimeError as exc:
            if n == tries - 1 or "502" not in str(exc):
                raise
            time.sleep(15 * (n + 1))


def payload(run_dir, paths, when=None, draft=False, now=None):
    """The posts:create body: one post with an Instagram carousel and a Facebook post (slide 1 + the written slides)."""
    run_dir = Path(run_dir)
    cfg = config()
    text = texts(run_dir)
    image = lambda p, i: {"id": f"s{i + 1:02d}", "path": p}  # noqa: E731
    return {
        "type": "draft" if draft else "schedule",
        "date": (when or default_date(run_dir, now)).isoformat(),
        "shortLink": False,
        "tags": [],
        "posts": [
            {"integration": {"id": cfg["instagram"]},
             "value": [{"content": text["caption"], "image": [image(p, i) for i, p in enumerate(paths)]}],
             "settings": {"__type": "instagram", "post_type": "post"}},
            {"integration": {"id": cfg["facebook"]},
             "value": [{"content": text["fb_text"], "image": [image(paths[0], 0)]}],
             "settings": {"__type": "facebook", "post_type": "post"}},
        ],
    }


def preview(run_dir):
    """What Carousel Machine's preview shows: the slides as page addresses, the Instagram caption and the Facebook text."""
    run_dir = Path(run_dir).resolve()
    avatar = next((c for c in (lib.PIPELINE / "assets").rglob("*") if c.suffix.lower() in (".png", ".jpg") and "logo" in c.name.lower()), None)
    return {"slides": [f"/approved/{run_dir.name}/final/{p.name}" for p in slides_of(run_dir)],
            **texts(run_dir), "avatar": "/" + str(avatar.relative_to(lib.PIPELINE)) if avatar else ""}


def send(run_dir, when=None, draft=False, dry_run=False):
    run_dir = Path(run_dir).resolve()
    slides = slides_of(run_dir)
    if not slides or not (run_dir / "final" / "caption.txt").exists():
        raise ValueError("אין עדיין שקופיות וכיתוב לקרוסלה הזאת")
    when = parse_when(when) if when else None
    if when and not draft and when < lib.now_local() + dt.timedelta(minutes=5):
        raise ValueError("השעה שנבחרה כבר עברה או קרובה מדי. בחרו שעה מאוחרת יותר")
    if dry_run:
        return payload(run_dir, [str(p) for p in slides], when, draft)
    old = lib.read_json(run_dir / "postiz.json") if (run_dir / "postiz.json").exists() else {}
    paths = old.get("media") if len(old.get("media") or []) == len(slides) else [_upload(p) for p in slides]
    body = payload(run_dir, paths, when, draft)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    try:
        created = _cli("posts:create", "--json", f.name)
    finally:
        os.unlink(f.name)
    record = {"sent_at": lib.now_local().isoformat(timespec="seconds"), "date": body["date"], "status": body["type"],
              "slides": len(paths), "media": paths, "result": created}
    lib.write_json(run_dir / "postiz.json", record)
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", nargs="?", help="approved/DATE-ID")
    ap.add_argument("--slots", type=int, help="print the next N posting times (every other day from Friday 06:00, Saturdays skipped) and exit; sends nothing")
    ap.add_argument("--at", help="date and time to publish, e.g. 2026-10-27T20:30 (default: the carousel's day at default_hour)")
    ap.add_argument("--draft", action="store_true", help="save as a draft in Postiz instead of scheduling")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent without uploading anything")
    args = ap.parse_args()
    if args.slots:
        print("\n".join(w.strftime("%a %Y-%m-%d %H:%M") for w in slots(args.slots)))
        return
    if not args.run_dir:
        ap.error("run_dir is needed unless --slots is given")
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute() and not run_dir.exists():
        run_dir = lib.PIPELINE / run_dir
    print(json.dumps(send(run_dir, when=args.at, draft=args.draft, dry_run=args.dry_run), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
