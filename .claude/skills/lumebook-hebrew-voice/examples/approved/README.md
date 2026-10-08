# Approved samples

Real Hebrew written by Yarin that Yarin says sounds like them. One sample per file. Calibration needs 15.

Good sources: WhatsApp messages, captions, voice note transcripts, emails, and nightly carousel options after Yarin's own edits. Avoid text that was heavily edited by someone else or written in a deliberate persona.

Before saving: remove names of other people, phone numbers, addresses and sensitive family details. Do not fix spelling; the writer is told not to imitate mistakes.

File name: `NNN-short-context.md`, for example `001-whatsapp-to-parent-group.md`

Template:

```markdown
---
context: WhatsApp to a friend about bedtime
audience: one parent
date: 2026-10
why_approved: sounds exactly like me, short and dry
---

<the exact text>
```

Count and status: `python3 carousel/carousel-pipeline/scripts/nightly.py voice`
