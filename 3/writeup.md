---
title: "Base Conversion"
ctf: "Standalone challenge (event not specified)"
date: 2026-09-04
category: misc
difficulty: easy
points: "N/A"
flag_format: "CTF{...}"
author: "Codex"
---

# Base Conversion

## Summary

The PDF contains a visible Base64 payload and hidden white text. Extracting the
PDF text reveals a poem whose leftmost characters form the flag body. The
visible payload can then be decoded separately with Base64.

## Solution

### Step 1: Extract the hidden poem acrostic

The poem is rendered in white, so it is not visible in a normal PDF viewer.
Extracting the text with `mutool` reveals its lines. Taking the first
non-whitespace character from each poem line gives:

```text
r34d_b3tw33n_th3_l1n35
```

This is the hidden flag body, written in leetspeak.

### Step 2: Decode the Base64 payload

The payload from the log is:

```text
dHI0bnNtMXNzMTBuX3IzYzB2M3IzZF92M3IxZjEzZA==
```

A complete extraction and decoding script is:

```python
import base64
import re
import subprocess

pdf_text = subprocess.run(
    ["mutool", "draw", "-F", "txt", "-o", "-", "challenge-easy1.pdf"],
    check=True,
    capture_output=True,
    text=True,
).stdout

payload = re.search(r"Base64\):\s*([A-Za-z0-9+/=]+)", pdf_text).group(1)
poem = re.search(
    r"Accompanying poem .*?:\n(.*?)\nAUTOMATED ANALYST NOTE",
    pdf_text,
    re.DOTALL,
).group(1)

flag_body = "".join(
    match.group(1)
    for line in poem.splitlines()
    if (match := re.match(r"\s*([A-Za-z0-9_])", line))
)
decoded = base64.b64decode(payload).decode()

print(f"Flag: CTF{{{flag_body}}}")
print(f"Base64 decoded value: {decoded}")
```

Output:

```text
Flag: CTF{r34d_b3tw33n_th3_l1n35}
Base64 decoded value: tr4nsm1ssion_r3c0v3r3d_v3r1f13d
```

## Flag

```text
CTF{r34d_b3tw33n_th3_l1n35}
```
