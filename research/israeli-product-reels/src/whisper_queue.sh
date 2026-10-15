#!/bin/zsh
# Two queues walk priority.txt; the lock file in process.py stops both from taking the same Reel.
PY=/Users/yarinbruner/.claude/skills/watch-video/.venv/bin/python
for c in $(cat priority.txt); do $PY process.py whisper $c; done
echo QUEUE $1 DONE
