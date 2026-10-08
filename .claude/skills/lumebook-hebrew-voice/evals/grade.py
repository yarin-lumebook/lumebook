#!/usr/bin/env python3
"""Grade lumebook-hebrew-voice eval runs with the pipeline's deterministic rules.

    python3 .claude/skills/lumebook-hebrew-voice/evals/grade.py carousel/carousel-pipeline/voice-eval-workspace/iteration-N

Writes grading.json (fields text, passed, evidence) next to each run's outputs/ folder
(layout eval-N-name/<with_skill|without_skill>/run-K/outputs/, as skill-creator's aggregate_benchmark expects).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "carousel/carousel-pipeline" / "scripts"))
import carousel_lib as lib  # noqa: E402

SPEC = {
    "kid-bedtime-water": {"keys": ["hook", "second_hook", "slide3", "caption", "cta"], "code": "מים", "hooks": ["hook", "second_hook"], "first_person": ["hook", "second_hook", "slide3"]},
    "expert-short-goodbye": {"keys": ["hook", "slide3", "slide4", "slide5", "caption", "cta"], "code": "פרידה", "hooks": ["hook"], "first_person": []},
    "rewrite-guru-caption": {"keys": ["caption", "cta"], "code": "מוצץ", "hooks": [], "first_person": []},
}


def grade(run_dir, spec):
    out = run_dir / "outputs" / "output.json"
    exp = []
    try:
        data = json.loads(out.read_text(encoding="utf-8"))
        ok = all(isinstance(data.get(k), str) and data[k].strip() for k in spec["keys"])
        exp.append({"text": "Output is JSON with every requested key", "passed": ok, "evidence": f"keys: {sorted(data)}"})
    except Exception as exc:  # noqa: BLE001
        return [{"text": "Output is JSON with every requested key", "passed": False, "evidence": str(exc)}]
    fields = {k: data[k] for k in spec["keys"] if isinstance(data.get(k), str)}
    punct = [str(i) for k, v in fields.items() for i in lib.forbidden_char_issues(k, v)]
    exp.append({"text": "No em dash, period or comma in any audience field", "passed": not punct, "evidence": "; ".join(punct[:6]) or "none found"})
    lex = [str(i) for k, v in fields.items() if k != "cta" for i in lib.lexicon_issues(k, v, allow_cta=True) if i.level == "ERROR"]
    exp.append({"text": "No jargon, diagnosis, guarantee, universality or brand misspelling", "passed": not lex, "evidence": "; ".join(lex[:6]) or "none found"})
    cta_err = [str(i) for i in lib.cta_issues("cta", fields.get("cta", ""), spec["code"]) if i.level == "ERROR"]
    exp.append({"text": f"CTA keeps the brief's idea with the code word {spec['code']} and has no second CTA", "passed": not cta_err, "evidence": "; ".join(cta_err[:6]) or fields.get("cta", "")})
    cap = lib.lines_of(fields.get("caption", ""))
    ends = bool(cap) and lib.collapse(cap[-1]) == lib.collapse(fields.get("cta", ""))
    second = [l for l in cap[:-1] for p, _ in lib.SECOND_CTA_PATTERNS if __import__("re").search(p, l)]
    exp.append({"text": "Caption ends with the exact CTA and adds no other CTA", "passed": ends and not second, "evidence": f"last line: {cap[-1] if cap else ''}; extra CTA lines: {second}"})
    long_lines = [f"{k}: {l}" for k, v in fields.items() if k != "cta" for l in lib.lines_of(v) if len(lib.words(l)) > lib.LINE_MAX_WORDS]
    exp.append({"text": "Every line has at most 12 words (one thought per line)", "passed": not long_lines, "evidence": "; ".join(long_lines[:4]) or "all lines short"})
    for h in spec["hooks"]:
        first = lib.lines_of(fields.get(h, ""))[:1]
        n = len(lib.words(first[0])) if first else 0
        total = len(lib.words(fields.get(h, "")))
        exp.append({"text": f"{h}: main line up to 8 words and up to 12 words in total", "passed": 0 < n <= 8 and total <= 12, "evidence": f"main {n} words, total {total}"})
    if spec["first_person"]:
        fp = sum(1 for k in spec["first_person"] if lib.FIRST_PERSON_RE.search(fields.get(k, "")))
        exp.append({"text": "Kid slides are in the child's first person", "passed": fp >= len(spec["first_person"]) - 1, "evidence": f"{fp} of {len(spec['first_person'])} fields use first person"})
    return exp


def main():
    it = Path(sys.argv[1])
    for eval_dir in sorted(p for p in it.iterdir() if p.is_dir() and p.name.startswith("eval-")):
        meta = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))
        spec = SPEC[meta["eval_name"]]
        for run in sorted(p.parent for p in eval_dir.glob("**/outputs") if p.is_dir()):
            exp = grade(run, spec)
            passed = sum(e["passed"] for e in exp)
            result = {"expectations": exp, "summary": {"passed": passed, "failed": len(exp) - passed, "total": len(exp), "pass_rate": round(passed / len(exp), 3)}}
            (run / "grading.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{run.relative_to(it)}: {passed}/{len(exp)}")


if __name__ == "__main__":
    main()
