---
title: "Git-Gud"
ctf: "Unknown"
date: 2026-09-04
category: forensics
difficulty: easy
points: Unknown
flag_format: "CTF{...}"
author: "Codex"
---

# Git-Gud

## Summary

The repository looked clean in its latest commit, but Git history retained a deleted staging debug file. Recovering that file revealed the flag.

## Solution

Inspect the commit history and identify the commit that added `debug.txt`:

```bash
git log --all --oneline --stat
git show 2786df2:debug.txt
```

The recovered file contains the only flag-like token in the repository history.

## Flag

```text
CTF{git_history_never_forgets}
```
