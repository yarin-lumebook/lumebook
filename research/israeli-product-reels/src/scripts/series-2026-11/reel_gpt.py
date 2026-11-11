#!/usr/bin/env python3
"""Funny pictures for the daily reels, made with the OpenAI Images API under Yarin's budget rules (11 Nov 2026).

Yarin, 11 Nov 2026: "incorporate funny generated images using gpt api in the editing, suggest minimal budget for each reel".
Each reel in reels.json has a "gpt" block: up to two scenes (a gag that matches its script, 3D cartoon, no real people, no text)
and a suggested budget (the estimate of its pictures plus one retry). Yarin's rules for the key (memory
feedback-openai-api-key-rules) apply to every call:

  - always ask for a budget, never exceed it, tell him the estimated tokens and cost before generating,
    create nothing without his explicit yes (a yes covers the reels he names, up to the budget he names);
  - so `plan` spends nothing, and `run` refuses without --max-usd and without --yes, and refuses when the logged spend
    plus the estimate would pass --max-usd. A call whose outcome is unknown (a timeout) counts at its estimate.

    python3 research/israeli-product-reels/src/scripts/series-2026-11/reel_gpt.py plan            # every reel, no spend
    python3 .../reel_gpt.py plan 1.2 7.1                                                         # some reels
    zsh -ic 'python3 .../reel_gpt.py run 1.2 7.1 --max-usd 0.08 --yes'                           # only after Yarin said yes
    python3 .../reel_gpt.py fixbooks-plan [--all]        # the 11 Nov pictures with a generic book: one edit each puts the
                                                         # reel's drawn LumeBook book in its place (no spend; --all adds the
                                                         # two pictures no reel uses now)
    zsh -ic 'python3 .../reel_gpt.py fixbooks-run --max-usd 0.35 --yes'                          # only after Yarin said yes

Every picture is kept once, named for what it shows, in the reels' media library (Yarin, 11 Nov 2026: "name everything you
create/generate and save it with the rest so you can always reuse it to save api cost"): media/projects/2026-11-11-reel-broll-pool/
gpt/gpt-<name>.png, listed in library.json with its scene, prompt, cost and the reels that use it (library.py). The reel's
source/gpt-<n>.png is a link to it. Before anything is generated, the library is searched for the same scene: a picture that
exists is linked at no cost (plan shows "in the library, $0"). The name is the image's "name" in reels.json, else the scene's
first words.

No books in a GPT picture (Yarin, 11 Nov 2026: "always make books look like lumebook books"): a generated book is never a
LumeBook book, so plan flags a scene that mentions one and run refuses it; the book is drawn by broll.py instead (an open 3D
LumeBook book, or the closed cover when the words are about the cover) and the gag picture leaves it out.

`run` logs the real cost from the usage OpenAI returns in gpt/ledger.json and moves the reel's edit.json "gpt_pending" entries
into "inserts" (each shows as a card over the darkened child video for its script line, in place of the clip that held that
line). Then `reels.py make <id>` builds the reel with them.
OPENAI_API_KEY comes from the environment (Keychain item openai-api-key through ~/.zshrc, so run through zsh -ic) and is never
printed or written.
"""
import argparse, json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SER = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "carousel/carousel-pipeline/scripts"))
import openai_pictures as op  # noqa: E402
sys.path.insert(0, str(SER))
import library  # noqa: E402

BOOK = re.compile(r"\b(story ?books?|books?|pages?|picture ?books?)\b", re.I)   # a generated book is never a LumeBook book


def pic_name(i):
    return i.get("name") or library.slug(" ".join(i["scene"].split()[:9]))


def in_library(i):
    return library.find("gpt", library.key_of(i["scene"]))


def load():
    return json.loads((SER / "reels.json").read_text())


def job_for(d, scene, cfg):
    prompt = d["defaults"]["gpt"]["style"] + scene
    return {"mode": "generate", "model": cfg["model"], "input": {"prompt": prompt, "size": cfg["size"], "quality": cfg["quality"], "n": 1}}


def reels_with_gpt(d, ids):
    out = []
    for r in d["reels"]:
        if r.get("gpt") and (r["id"] in ids if ids else r["status"] != "posted"):
            out.append(r)
    missing = [i for i in ids if i not in {r["id"] for r in out}]
    if missing:
        sys.exit(f"no gpt plan for: {', '.join(missing)}")
    return out


def ledger_path(r):
    return ROOT / r["project"] / "gpt" / "ledger.json"


def spent(r):
    p = ledger_path(r)
    if not p.exists():
        return 0.0
    return round(sum(x.get("usd", 0) for x in json.loads(p.read_text())), 5)


def todo(r):
    base = ROOT / r["project"] / "source"
    return [i for i in r["gpt"]["images"] if not (base / f"gpt-{i['n']}.png").exists()]


def cmd_plan(args):
    d, cfg = load(), op.config()
    tot_usd, tot_tok, tot_n = 0.0, 0, 0
    for r in reels_with_gpt(d, args.ids):
        print(f"{r['id']:>5}  {r.get('date') or 'spare':10}  budget ${r['gpt']['budget_usd']:.2f}   {r['hook'].splitlines()[0][:40]}")
        for i in r["gpt"]["images"]:
            at = f"line {i['line']}" if i["line"] is not None else "line chosen at the edit"
            have = in_library(i)
            if have:
                print(f"         #{i['n']} {at:22} in the library, $0: {have['file']}")
                continue
            est = op.estimate_job(job_for(d, i["scene"], cfg), cfg)
            tot_usd += est["usd"]
            tot_tok += est["input_text_tokens"] + est["output_tokens"]
            tot_n += 1
            flag = "  BOOK IN THE SCENE: draw the book with broll.py, leave it out of the picture" if BOOK.search(i["scene"]) else ""
            print(f"         #{i['n']} {at:22} ${est['usd']:.4f}  ~{est['input_text_tokens'] + est['output_tokens']} tokens  {i['scene'][:70]}{flag}")
    print(f"\n{tot_n} pictures, estimate ${tot_usd:.4f}, about {tot_tok} tokens "
          f"({cfg['model']}, {cfg['size']}, {cfg['quality']}; estimate is on the high side: measured $0.0053 a picture)")


def cmd_run(args):
    if not args.max_usd:
        sys.exit("--max-usd is required: the budget Yarin approved")
    if not args.yes:
        sys.exit("--yes is required, and only once Yarin has said yes to these reels and this budget (nothing is generated without it)")
    d, cfg = load(), op.config()
    rs = reels_with_gpt(d, args.ids)
    plan = []
    for r in rs:
        if not r.get("project") or not (ROOT / r["project"] / "edit.json").exists():
            sys.exit(f"{r['id']} has no edit.json yet: make its pictures after the reel is filmed and edited")
        for i in todo(r):
            have = in_library(i)
            if have:   # made before for this or another reel: link it, spend nothing
                library.link(library.path_of(have), ROOT / r["project"], f"source/gpt-{i['n']}.png")
                library.used_in(have["file"], r["id"])
                log(r, {"reel": r["id"], "n": i["n"], "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "reused", "usd": 0.0,
                        "file": have["file"], "scene": i["scene"]})
                print(f"{r['id']} #{i['n']} from the library, $0: {have['file']}")
                continue
            if BOOK.search(i["scene"]):
                sys.exit(f"{r['id']} #{i['n']}: the scene has a book, and a generated book is never a LumeBook book. Draw the book "
                         "with broll.py and write the scene without it.")
            plan.append((r, i, op.estimate_job(job_for(d, i["scene"], cfg), cfg)))
    est = round(sum(e["usd"] for _, _, e in plan), 4)
    already = round(sum(spent(r) for r in rs), 5)
    print(f"{len(plan)} pictures to make, estimate ${est:.4f}, already spent on these reels ${already:.4f}, budget ${args.max_usd:.4f}")
    if already + est > args.max_usd + 1e-9:
        sys.exit("stop: that would pass the approved budget. Ask Yarin for a bigger one.")
    client = op.OpenAIImages()
    running = already
    for r, i, e in plan:
        if running + e["usd"] > args.max_usd + 1e-9:
            sys.exit(f"stop before {r['id']} #{i['n']}: ${running:.4f} spent + ${e['usd']:.4f} would pass ${args.max_usd:.4f}")
        base = ROOT / r["project"]
        (base / "gpt").mkdir(parents=True, exist_ok=True)
        rec = {"reel": r["id"], "n": i["n"], "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pre_estimate_usd": e["usd"]}
        job = job_for(d, i["scene"], cfg)
        try:
            rid, png, usage = client.generate(job, cfg)
        except op.ApiError as exc:
            rec.update(status="error", error=str(exc)[:300], usd=e["usd"] if exc.billed else 0.0)
            log(r, rec)
            running += rec["usd"]
            print(f"{r['id']} #{i['n']} failed: {exc}")
            continue
        usd = op.usage_cost(usage, cfg)
        # one copy, named, in the library; the reel links to it
        out = library.free_name(library.POOL / "gpt", "gpt-" + pic_name(i), ".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png)
        line = r["vo"][i["line"]] if isinstance(i.get("line"), int) and i["line"] < len(r["vo"]) else ""
        library.put({"file": str(out.relative_to(library.POOL)), "kind": "gpt", "about": i["scene"],
                     "words": re.sub(r"[.,?!]", "", line).split()[:8], "key": library.key_of(i["scene"]), "prompt": job["input"]["prompt"],
                     "cost_usd": usd, "request_id": rid, "made": rec["at"][:10], "reels": [r["id"]]})
        library.link(out, base, f"source/gpt-{i['n']}.png")
        rec.update(status="ok", usd=usd, request_id=rid, usage=usage, scene=i["scene"], file=str(out.relative_to(library.POOL)))
        log(r, rec)
        running += usd
        print(f"{r['id']} #{i['n']} -> {out.relative_to(ROOT)}  ${usd:.4f}  (total ${running:.4f} of ${args.max_usd:.4f})")
    for r in rs:
        join(r)


# ---------- the LumeBook book in the pictures made before the rule (fixbooks) ----------
# 9 of the 16 pictures of 11 Nov 2026 show a generic cartoon book (library.json note). Yarin, 11 Nov 2026: "always make books look
# like lumebook books" and, asked whether to plan a budget to redo them: "Yes, plan it". One edit per picture: the picture plus a
# reference of the reel's own drawn LumeBook book (broll.py, on white), asking for that book in place of the old one, open, and
# nothing else changed. The old picture stays in the library; the reel's source/gpt-<n>.png then links to the new one.

FIX_PROMPT = ("Edit the first picture. Replace the book in it with the book shown in the second picture: a LumeBook personalised "
              "children's book, square, soft cover, shown open, the left page a full-page illustration of the child and the right "
              "page white with a few short lines of text. Put it exactly where the old book is, at the same size and angle, held or "
              "lying the same way, and open. Copy the illustration on its left page from the second picture and keep the text on the "
              "right page small. Change nothing else: the same characters, faces, poses, clothes, light, background and the same 3D "
              "animated cartoon style. No other text, no logos.")


def book_ref(r):
    """The reel's own drawn open book (story page first, else title page, else dedication) as a library file, or None."""
    e = json.loads((ROOT / r["project"] / "edit.json").read_text())
    for kind in ("open", "page", "title", "dedication"):
        for rel, spec in (e.get("mockups") or {}).items():
            p = ROOT / r["project"] / rel
            if spec.get("kind") == kind and p.exists():
                return p.resolve()
    return None


def ref_on_white(drawn):
    """The reel's drawn book, whole (nothing cut off) on white, as the edit's second picture. Drawn by broll.py under
    /usr/bin/python3 (it needs python-bidi and numpy) into the pool's .cache, once."""
    import subprocess
    out = library.POOL / ".cache" / "refs" / (drawn.stem + "-whole-on-white.png")
    if not out.exists():
        subprocess.run(["/usr/bin/python3", str(SER / "broll.py"), "ref", str(drawn), str(out)], check=True)
    return out


def fix_list(d, ids, everything):
    """(reel, image, its library entry, in use, reference drawing) for every picture whose library entry says it shows a generic
    book and that has no LumeBook version yet."""
    out = []
    for r in reels_with_gpt(d, ids):
        if not r.get("project") or not (ROOT / r["project"] / "edit.json").exists():
            continue
        inserts = json.dumps(json.loads((ROOT / r["project"] / "edit.json").read_text()).get("inserts", []))
        for i in r["gpt"]["images"]:
            e = in_library(i)
            if not e or "generic cartoon book" not in (e.get("note") or "") or e.get("replaced_by"):
                continue
            used = f"source/gpt-{i['n']}.png" in inserts
            if used or everything:
                out.append((r, i, e, used, book_ref(r)))
    return out


def fix_job(cfg, ref):
    return {"mode": "edit", "model": cfg["model"], "refs": ["picture", str(ref)],
            "input": {"prompt": FIX_PROMPT, "size": cfg["size"], "quality": cfg["quality"], "n": 1}}


def fix_spent(rs):
    tot = 0.0
    for r in rs:
        p = ledger_path(r)
        if p.exists():
            tot += sum(x.get("usd", 0) for x in json.loads(p.read_text()) if x.get("kind") == "bookfix")
    return round(tot, 5)


def cmd_fixbooks(args):
    d, cfg = load(), op.config()
    todo_ = fix_list(d, args.ids, args.all)
    if not todo_:
        print("no picture with a generic book left")
        return
    rows, tot, tok, tot_used = [], 0.0, 0, 0.0
    for r, i, e, used, ref in todo_:
        if not ref:
            sys.exit(f"{r['id']} #{i['n']}: the reel has no drawn open book to copy (broll.py render {r['id']})")
        est = op.estimate_job(fix_job(cfg, ref), cfg)
        rows.append((r, i, e, used, ref, est))
        tot += est["usd"]
        tok += est["input_text_tokens"] + est["input_image_tokens"] + est["output_tokens"]
        tot_used += est["usd"] if used else 0
    if args.cmd == "fixbooks-plan":
        for r, i, e, used, ref, est in rows:
            print(f"{r['id']:>5} #{i['n']}  {'in the reel' if used else 'not used  '}  ${est['usd']:.4f}  ~{est['input_text_tokens'] + est['input_image_tokens'] + est['output_tokens']} tokens"
                  f"  {Path(e['file']).stem[4:]}  <- {ref.name}")
        print(f"\n{len(rows)} edits, estimate ${tot:.4f}, about {tok} tokens ({cfg['model']}, {cfg['size']}, {cfg['quality']}, "
              f"2 pictures in each: the old picture and the reel's drawn LumeBook book). The estimate is on the high side: the one "
              f"measured edit (one picture in, 04 Nov 2026) cost $0.0178.")
        return
    if not args.max_usd:
        sys.exit("--max-usd is required: the budget Yarin approved")
    if not args.yes:
        sys.exit("--yes is required, and only once Yarin has said yes to this budget (nothing is generated without it)")
    rs = list({r["id"]: r for r, *_ in rows}.values())
    running = fix_spent(rs)
    print(f"{len(rows)} edits, estimate ${tot:.4f}, already spent on book fixes ${running:.4f}, budget ${args.max_usd:.4f}")
    client = op.OpenAIImages()
    for r, i, e, used, ref, est in rows:
        if running + est["usd"] > args.max_usd + 1e-9:
            sys.exit(f"stop before {r['id']} #{i['n']}: ${running:.4f} spent + ${est['usd']:.4f} would pass ${args.max_usd:.4f}")
        old = library.path_of(e)
        rec = {"reel": r["id"], "n": i["n"], "kind": "bookfix", "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pre_estimate_usd": est["usd"]}
        try:
            rid, png, usage = client.edit(fix_job(cfg, ref), [old, ref_on_white(ref)], cfg)
        except op.ApiError as exc:
            rec.update(status="error", error=str(exc)[:300], usd=est["usd"] if exc.billed else 0.0)
            log(r, rec)
            running += rec["usd"]
            print(f"{r['id']} #{i['n']} failed: {exc}")
            continue
        usd = op.usage_cost(usage, cfg)
        out = library.free_name(library.POOL / "gpt", old.stem + "-lumebook-book", ".png")
        out.write_bytes(png)
        new = {k: v for k, v in e.items() if k not in ("note", "file", "key", "request_id", "cost_usd", "made")}
        library.put({**new, "file": str(out.relative_to(library.POOL)), "about": e["about"] + " (the book is a LumeBook book, open)",
                     "key": library.key_of(i["scene"] + " | lumebook book"), "edited_from": e["file"], "book_ref": str(ref.relative_to(ROOT)),
                     "prompt": FIX_PROMPT, "cost_usd": usd, "request_id": rid, "made": rec["at"][:10]})
        library.put({**e, "replaced_by": str(out.relative_to(library.POOL))})
        library.link(out, ROOT / r["project"], f"source/gpt-{i['n']}.png")
        rec.update(status="ok", usd=usd, request_id=rid, usage=usage, file=str(out.relative_to(library.POOL)))
        log(r, rec)
        running += usd
        print(f"{r['id']} #{i['n']} -> {out.relative_to(ROOT)}  ${usd:.4f}  (total ${running:.4f} of ${args.max_usd:.4f})")
    print("then rebuild the reels that use them: reels.py make <id>")


def log(r, rec):
    p = ledger_path(r)
    rows = json.loads(p.read_text()) if p.exists() else []
    rows.append(rec)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")


def join(r):
    """Move the pictures that exist from gpt_pending into inserts, in script order. A funny picture takes its line over from
    the clip that held it until then (the clip stays listed under "replaced_by_gpt", so it can come back)."""
    ej = ROOT / r["project"] / "edit.json"
    e = json.loads(ej.read_text())
    made = {i["n"] for i in r["gpt"]["images"] if (ROOT / r["project"] / "source" / f"gpt-{i['n']}.png").exists()}
    keep, add = [], []
    for p in e.get("gpt_pending", []):
        n = int(Path(p["src"]).stem.split("-")[1])
        (add if n in made else keep).append({k: v for k, v in p.items() if k != "fill"})   # a card over the darkened child
    if add:
        lines = {p["at"] for p in add}
        out = [i for i in e.get("inserts", []) if i.get("gpt") or i["at"] not in lines]
        e.setdefault("replaced_by_gpt", []).extend(i for i in e.get("inserts", []) if not i.get("gpt") and i["at"] in lines)
        e["inserts"] = sorted(out + add, key=lambda i: i["at"] if isinstance(i["at"], int) else 0)
    e["gpt_pending"] = keep
    if not keep:
        e.pop("gpt_pending")
    ej.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n")
    print(f"{r['id']}: {len(add)} picture(s) added to edit.json inserts")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("ids", nargs="*"); p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run"); p.add_argument("ids", nargs="+"); p.add_argument("--max-usd", type=float); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_run)
    for name in ("fixbooks-plan", "fixbooks-run"):   # the LumeBook book in the 11 Nov pictures; plan spends nothing
        p = sub.add_parser(name); p.add_argument("ids", nargs="*"); p.add_argument("--all", action="store_true", help="also pictures no reel uses now")
        p.add_argument("--max-usd", type=float); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_fixbooks)
    a = ap.parse_args()
    a.fn(a)
