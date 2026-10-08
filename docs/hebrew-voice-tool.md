# Hebrew voice tooling for the nightly carousel pipeline

Research date: 2026-10-07

Scope: choose the best no-extra-cost Claude Code mechanism for producing natural everyday Hebrew in Yarin's voice while reliably enforcing RTL and a ban on em dashes, periods, and commas. This note covers the voice layer only, not pipeline implementation.

## Recommendation

Use a **project-scoped Claude Code custom skill** as the voice engine, built and evaluated with Anthropic's official **skill-creator** plugin, plus a small deterministic validator that runs before a draft is accepted or sent to image generation.

The proposed stack is:

1. `.claude/skills/hebrew-carousel-voice/SKILL.md`
   - The writing workflow
   - The two narrator modes: child point of view and expert point of view
   - Yarin's voice profile
   - Good and bad examples
   - Slide-level structure and self-review rubric
2. Supporting files inside the skill
   - `references/voice-profile.md`
   - `examples/approved-hebrew.md`
   - `examples/rejected-hebrew.md`
   - A compact list of preferred words, phrases, rhythm patterns, and banned habits
3. A deterministic validator
   - Rejects `—`, `.`, and `,` in audience-facing copy fields
   - Confirms every audience-facing string contains Hebrew where Hebrew is expected
   - Confirms the rendered template uses `dir="rtl"` or CSS `direction: rtl`
   - Runs after copy generation and before fal.ai image work
4. Optional development tools
   - Anthropic's `skill-creator` plugin to create and evaluate the voice skill
   - A Claude Code Stop hook or the official `hookify` plugin as a second guard during interactive runs

This is the best fit because Claude Code skills are designed for reusable instructions, workflows, reference material, examples, and bundled scripts. A project skill can be committed with the repository and is loaded by Claude Code cloud sessions and Routines. Anthropic also explicitly recommends scripts inside skills when deterministic reliability is needed. [Claude Code skills](https://code.claude.com/docs/en/skills) [Anthropic skill-development source](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md)

"Free" here means no separate voice product or third-party plugin subscription. Claude Code plan or API usage, the selected model, fal.ai generation, and any hosted scheduler still have their own costs.

## Why this beats the alternatives

| Option | Voice fidelity | Nightly automation fit | Hard rule enforcement | Added infrastructure | Verdict |
|---|---:|---:|---:|---:|---|
| Project custom skill | High when grounded in Yarin examples | High | Medium alone, high with validator | Low | Best core |
| Custom output style | Medium to high | Medium | Low | Low | Optional for interactive sessions |
| `CLAUDE.md` only | Medium | High | Low | Lowest | Keep only short always-on facts here |
| `skill-creator` official plugin | Indirect | Development-time only | Helps test | Low | Best tool for building the skill |
| `hookify` official plugin | None by itself | Medium | High for detectable patterns | Low | Optional guardrail |
| Mem0 or another style-memory layer | Potentially high over time | Medium | Low | High | Premature for this use case |
| Fine-tuning a model | Potentially high | Low to medium | Low | High | Not justified for six nightly concepts |

### Project custom skill

Claude Code loads a skill's body only when relevant or when invoked directly, so a detailed voice guide and examples do not have to live in every prompt. Skills support bundled references, examples, assets, and scripts. Project skills live in `.claude/skills/<name>/SKILL.md` and can be committed to the repository. Cloud sessions, including Routines, load committed project skills; machine-local skills under `~/.claude/skills/` do not. [Skills overview and structure](https://code.claude.com/docs/en/skills) [Cloud and Routine skill loading](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions)

This makes the skill the right place for the full voice workflow rather than `CLAUDE.md`. Anthropic positions `CLAUDE.md` as persistent project context and skills as reusable task-specific instructions and procedures. [Claude Code feature comparison](https://code.claude.com/docs/en/features-overview)

### Custom output style

A custom output style can set Claude's role, tone, and response format for every response in a session. It can be useful when Yarin is interactively editing carousel copy, but it is too broad for the nightly pipeline and does not guarantee compliance. Anthropic says output styles are instructions rather than enforcement and recommends hooks for behavior that must happen every time. Output styles also do not govern separate subagents. [Claude Code output styles](https://code.claude.com/docs/en/output-styles)

Verdict: optional convenience, not the source of truth.

### Official `skill-creator` plugin

Anthropic's official `skill-creator` plugin creates, improves, and measures skills. Claude Code's docs describe an evaluation loop that compares realistic prompts in fresh sessions with and without a skill. The plugin is published in Anthropic's official marketplace repository under Apache 2.0. [Skill evaluation docs](https://code.claude.com/docs/en/skills#evaluate-and-iterate-on-a-skill) [Official skill-creator plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) [License](https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/skill-creator/LICENSE)

Verdict: the best free tool for authoring and testing the custom voice skill, but not a runtime voice engine on its own.

### Hooks and `hookify`

Claude Code hooks run at lifecycle events and can block completion. A Stop hook receives the final assistant text as `last_assistant_message`; returning a blocking decision or exit code 2 prevents Claude from stopping and feeds the failure back so it can revise. This is suitable as an interactive guard against forbidden punctuation. [Hooks reference](https://code.claude.com/docs/en/hooks) [Hooks guide](https://code.claude.com/docs/en/hooks-guide)

Anthropic's official `hookify` plugin creates regex-based hook rules from plain-language instructions and can warn or block on matches. It is useful for quickly installing a secondary rule such as rejecting forbidden punctuation in carousel output files. It uses Python's standard library and is Apache-2.0 licensed. [Official hookify plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify) [License](https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/hookify/LICENSE)

For the production pipeline, a direct validator step is preferable to relying only on a Stop hook because the pipeline's source of truth will be a structured draft file, not necessarily Claude's final chat message.

### External memory tools such as Mem0

Mem0 is an Apache-2.0 open-source memory layer and provides an MCP integration with tools for storing and retrieving memories. It can support personalization that changes continuously over many conversations. However, the hosted MCP stores data in a Mem0 account, while self-hosting adds a server, database, retrieval, LLM, and embedding configuration. The project's own quickstart notes that Mem0 requires an LLM and defaults to paid OpenAI models unless configured otherwise. [Mem0 repository](https://github.com/mem0ai/mem0) [Mem0 MCP documentation](https://github.com/mem0ai/mem0/blob/main/docs/platform/mem0-mcp.mdx)

For a stable brand voice with a curated source corpus, semantic memory is less transparent than a version-controlled skill and can retrieve inconsistent fragments. Add memory only if Yarin later wants the voice to learn automatically from approvals and edits across many months.

## How to model Yarin's voice

The quality will come mainly from the corpus, not from the container that holds it.

Recommended source set:

- 30 to 100 authentic Hebrew messages, posts, scripts, or captions written by Yarin
- Prefer examples aimed at parents, education, children, products, or emotionally charged decisions
- Remove private details and messages written in a deliberately different persona
- Tag each example with audience, energy, intimacy, humor, sentence length, and whether Yarin still likes it
- Add 10 to 20 rejected or edited examples with a short reason such as too polished, too corporate, too therapist-like, too American, too cute, or not how I speak
- Preserve Yarin's actual code-switching and slang instead of translating everything into formal Hebrew

The skill should derive and record a compact voice profile from those examples, including:

- Common openings and endings
- Typical line length and pacing
- Preferred connective words
- Level of directness and warmth
- How Yarin expresses uncertainty, disagreement, humor, and empathy
- Phrases Yarin never uses
- Differences between Yarin's voice and the child or expert narrator

The child and expert directions should share Yarin's rhythm but not collapse into the same narrator:

- **Child direction:** first person, concrete sensory detail, a hidden need behind behavior, no adult clinical vocabulary, no manipulative cuteness
- **Expert direction:** plain language, one defensible idea per slide, specific observable behavior, no credential theater, no jargon unless immediately translated

## Enforcement design

Prompt instructions alone are not enough for the three punctuation bans. Anthropic explicitly distinguishes model instructions from hooks and scripts that enforce repeatable behavior. [Output style limitations](https://code.claude.com/docs/en/output-styles#choose-between-an-output-style-and-other-features) [Hooks behavior](https://code.claude.com/docs/en/hooks)

Use three layers:

1. **Generation rule in the skill**
   - Audience-facing Hebrew uses line breaks instead of commas or periods
   - Em dashes are forbidden
   - The rule applies to slide copy, cover, caption, CTA, and image text
   - Metadata, filenames, URLs, and machine-readable fields should be excluded from the punctuation scan where necessary
2. **Deterministic validation**
   - Scan only audience-facing text fields
   - Fail on Unicode em dash `U+2014`, ASCII period `U+002E`, and comma `U+002C`
   - Optionally fail on Hebrew maqaf `U+05BE` and en dash `U+2013` if Yarin wants a broader no-dash policy
   - Return the field name and offending character so Claude can rewrite only the failed lines
3. **RTL rendering validation**
   - Require `dir="rtl"` and `lang="he"` in HTML renderers
   - Require `direction: rtl` and `text-align: right` in carousel text containers
   - Test mixed Hebrew, numerals, emoji, and Latin brand names because Unicode bidirectional rendering can change visual order

Do not silently strip punctuation after generation. Removing characters can merge clauses and damage meaning. Reject and regenerate or rewrite the affected line.

## Evaluation before trusting the nightly run

Create a small fixed evaluation set covering both creative directions and likely edge cases:

- 10 brand topics
- Three versions per direction for at least three topics
- Short and long slide sequences
- Sensitive parenting behavior topics
- Mixed Hebrew and English product names
- Numerals, ages, percentages, and emoji

Score each output on:

1. Sounds like something Yarin would actually say aloud
2. Natural everyday Israeli Hebrew rather than translated English
3. Clear difference between child and expert narration
4. One idea per slide and strong swipe rhythm
5. No prohibited punctuation
6. Correct RTL rendering
7. No invented expert claims or fake child psychology

Use Yarin's edits as labeled feedback. Update the approved and rejected examples weekly at first, then less often once the evaluation scores stabilize. Anthropic recommends testing realistic prompts in fresh sessions and comparing results with and without the skill; its official `skill-creator` plugin automates that loop. [Skill evaluation guidance](https://code.claude.com/docs/en/skills#evaluate-and-iterate-on-a-skill)

## Fit with the 10 PM workflow

Claude Code Routines can run nightly from a saved prompt and support scheduled, API, and GitHub triggers. Daily times use the account's local timezone, although Anthropic warns that jobs scheduled exactly on the hour can start several minutes late. Routines are available on Pro, Max, Team, and Enterprise plans and count against account usage. [Claude Code Routines](https://code.claude.com/docs/en/routines)

For a cloud Routine:

- Commit the voice skill to `.claude/skills/`; do not rely on a machine-only `~/.claude/skills/` copy
- Keep the routine prompt self-contained and explicitly invoke the skill
- Produce a reviewable structured artifact with all six concepts before any morning publishing step
- Include only the connectors the run needs
- Verify that fal.ai is available to the cloud environment as a connector or reachable service; a local MCP process is not automatically available inside a cloud run

If the fal.ai MCP is local-only, use a local scheduler with Claude Code's non-interactive mode instead of a cloud Routine. The same committed skill and validator still apply. Do not use `--bare` unless all required skill, hook, and MCP configuration is supplied explicitly because bare mode skips normal project customizations. [Claude Code non-interactive mode](https://code.claude.com/docs/en/headless)

## Concrete choice

Build the first version with only:

- One committed project skill for Yarin's Hebrew carousel voice
- One curated local corpus of Yarin-approved and Yarin-rejected examples
- One deterministic copy and RTL validator
- Anthropic's official `skill-creator` plugin during development and evaluation

Do not add Mem0, Zep, or another memory service initially. Do not make a global output style the source of truth. Package the skill, validator, hook, and fal.ai configuration as a reusable plugin only if the same setup later needs to be installed across multiple repositories or distributed to other people. Anthropic describes plugins as the packaging layer for skills, hooks, agents, and MCP servers rather than a prerequisite for using those features. [Claude Code plugins](https://code.claude.com/docs/en/plugins)

This approach is transparent, version-controlled, cheap to operate, compatible with nightly runs, and easy to improve from Yarin's actual approvals rather than from a generic idea of natural Hebrew.
