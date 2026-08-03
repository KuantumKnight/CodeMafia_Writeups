---
title: "Dying Backup Node"
ctf: "Standalone challenge"
date: 2026-09-04
category: misc
difficulty: easy
points: "N/A"
flag_format: "flag{...}"
author: "Codex"
---

# Dying Backup Node

## Summary

The apparent status line is a decoy. Although its ROT13 text decodes to
`migration_verified_complete`, the log tail contains the real secret in the
trailing characters of lines written by `[node7]`.

## Solution

### Step 1: Ignore the misleading status line

ROT13-decoding the pinned line gives:

```text
migration_verified_complete
```

The note claims the rest of the file carries no information, but the log
entries contain a consistent `[node7]` tag and carefully chosen line endings.

### Step 2: Extract the trailing characters

Take the final non-whitespace character from each `[node7]` line, in order:

```python
from pathlib import Path

lines = Path("challenge-backup-1788442583911.txt").read_text().splitlines()
tail = lines[8:35]
secret = "".join(line.rstrip()[-1] for line in tail if "[node7]" in line)
print(f"flag{{{secret}}}")
```

This prints:

```text
flag{look_at_th3_3nd}
```

## Flag

```text
flag{look_at_th3_3nd}
```
