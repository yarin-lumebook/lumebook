#!/bin/zsh
# usage: run_q.sh <lang> <files...>  frames for all first, then transcripts
lang=$1; shift
for f in "$@"; do ./process.sh $f; done
for f in "$@"; do ./transcribe.sh $f $lang; done
