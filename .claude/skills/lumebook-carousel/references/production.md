# Production mode, step by step

**Since 03 Nov 2026 the only picture source is the OpenAI Images API, under Yarin's four rules for the key** (always ask for a budget, never exceed it, tell the estimated tokens and cost before generating, create nothing without his explicit permission). The older flows are retired: fal.ai (standing approval $0.50, story cap $1.00, until 30 Oct 2026) and ChatGPT in Chrome (30 Oct to 03 Nov 2026). Their scripts are in `_to-delete/carousel/carousel-pipeline/`. SKILL.md, Mode 2, and `carousel/carousel-pipeline/README.md` section 2b are the main text; this file is the command reference.

Scripts live in `carousel/carousel-pipeline/scripts/`. Run everything that calls OpenAI through `zsh -ic '...'` so `OPENAI_API_KEY` comes from the Keychain, and never print the key.

## 1 · Freeze and estimate (free)

```bash
python3 carousel/carousel-pipeline/scripts/prepare_picture_jobs.py carousel/carousel-pipeline/drafts/DATE/pack.json OPTION
zsh -ic 'python3 carousel/carousel-pipeline/scripts/openai_generate.py carousel/carousel-pipeline/approved/DATE-OPTION plan'
```

`prepare_picture_jobs.py` writes `approved/DATE-OPTION/` (approved.json, jobs.json, state.json, APPROVAL.md, README.md) with no network call; refreeze after a copy edit with `--refreeze` (pictures whose prompt did not change are kept). `plan` prints the model, the pictures still to make, the estimated tokens and dollars and the spend so far. Show Yarin both, ask for a budget, wait for a yes.

## 2 · The picture, or the cover

```bash
zsh -ic 'python3 .../openai_generate.py RUN_DIR run picture --max-usd BUDGET'      # one-picture packs
zsh -ic 'python3 .../openai_generate.py RUN_DIR run slide-01 --max-usd BUDGET'     # story packs: the cover alone first
python3 .../openai_generate.py RUN_DIR qa JOB pass
zsh -ic 'python3 .../openai_generate.py RUN_DIR replace JOB --note "what is wrong" --max-usd BUDGET'
```

`--max-usd` is the amount Yarin approved for the carousel in total, what is already logged included, and has no default. `run` and `replace` refuse a call that the logged spend, the calls in flight and this call's estimate would push past it. `--dry-run` prints the prompt and estimate and calls nothing. A job may be replaced twice.

## 3 · The other slides (story packs, after the cover passes)

Show the estimate for them (`plan`), get Yarin's yes for that stage, then:

```bash
zsh -ic 'python3 .../openai_generate.py RUN_DIR run --max-usd BUDGET'
```

Finished slides are skipped, so the same command resumes. They are edits of the approved cover, run in parallel (`--workers`, default 4). Mark each `qa slide-NN pass|fail`.

## 4 · Export

```bash
python3 carousel/carousel-pipeline/scripts/compose_slides.py RUN_DIR
```

1080 x 1350 slides, contact sheet, RTL check, caption, sources, alt text and the ZIP. View the contact sheet and the RTL check yourself.

## Money

The log `generated-assets/generation-log.jsonl` holds, per call, the model, request id, token usage, real cost (`cost_basis: "usage"`), and for a failed call whether it was billed (an error answer is not; a timeout is counted as spent). Report estimated and real cost, and the budget Yarin gave, in the final message.
