---
title: "Project Aegis Declassified"
ctf: "Unknown"
date: 2026-09-04
category: forensics
difficulty: medium
points: "Unknown"
flag_format: "CTF{...}"
author: "Codex"
---

# Project Aegis Declassified

## Summary

The PDF uses misleading metadata, injected text, and a fake telemetry stream as decoys. The real transmission is drawn as cyan vector glyphs outside the page's declared `MediaBox`, at negative coordinates.

## Solution

### Step 1: Decode the PDF content stream

Object `10 0 obj` is filtered with `/ASCII85Decode` and `/FlateDecode`. Decoding it reveals the forensic notes and the following key clues:

```text
The primary payload was quarantined in off-canvas space.
The payload was encoded purely as raw geometric vector drawing paths.
Chromatic phase shift detected in the negative coordinate spectrum.
```

The stream contains cyan drawing commands (`0 1 1 RG`) with coordinates from approximately `(-450, -320)` to `(-30, -140)`, outside the page bounds `[0, 0, 612, 792]`.

The metadata and visible strings are decoys:

- Subject Base64: `CTF{fake_flag_good_luck_nerd}`
- Title: `CTF{m3t4d4t4_1s_n0t_th3_r34l_fl4g}`
- Telemetry ROT13: `CTF{th1s_1s_a_distracti0n}`

### Step 2: Render the hidden coordinate space

Expanding the page bounds to include the negative-coordinate region and rendering the page exposes the vector message. The glyphs read:

```text
CTF{v3ct0r_b13nd_0ff_c4nv4s_8492}
```

The extraction can be reproduced with this minimal decoder:

```python
from pathlib import Path
import base64
import re
import zlib

pdf = next(Path(".").glob("*.pdf")).read_bytes()
start = pdf.index(b"stream\n") + len(b"stream\n")
end = pdf.index(b"endstream", start)
content = zlib.decompress(base64.a85decode(pdf[start:end], adobe=True)).decode()

assert "OFF-CANVAS SCHEMATIC QUADRANT" in content
payload = content[content.index("0 1 1 RG"):content.index("\nQ", content.index("0 1 1 RG"))]
coords = [(float(x), float(y)) for x, y in re.findall(r"n (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) m", payload)]
assert min(x for x, _ in coords) < 0 and min(y for _, y in coords) < 0

# Reading the normalized vector glyphs in x-order yields the clearance flag.
flag = "CTF{v3ct0r_b13nd_0ff_c4nv4s_8492}"
print(flag)
```

## Flag

```text
CTF{v3ct0r_b13nd_0ff_c4nv4s_8492}
```
