---
title: "Cursed OS Terminal"
ctf: "Unknown"
date: 2026-09-04
category: misc
difficulty: medium
points: "N/A"
flag_format: "CTF{...}"
author: "Codex"
---

# Cursed OS Terminal

## Summary

The download contained four native packages for different operating systems. Each package embeds the output and artifacts of a hostile hybrid terminal. The clearance fragments were recovered from the Windows Registry, Linux shadow cache, macOS quarantine data, and PowerShell environment output.

## Solution

### Step 1: Identify the four vaults

List the archive contents:

```bash
unzip -l terminal-download-1788444688711.zip
```

The archive contains RPM, DEB, DMG, and EXE packages. Extracting them and inspecting the native executables with `strings` reveals the platform-specific command vocabulary and the embedded vault artifacts:

```bash
strings -a cursed-os-terminal | grep -E 'Part1_B64|PART2_FRAGMENT|PATH_REF|FLAG_FINAL'
```

The relevant evidence is:

| Subsystem | Artifact | Fragment |
|---|---|---|
| Windows | `RegistryBackup.reg`, `Part1_B64` | `Q1RGe3doNHRf` |
| Linux | `/etc/.shadow_cache`, `PART2_FRAGMENT` | `0s_4r3_` |
| macOS | `/Volumes/MacintoshHD/Quarantine.plist` | `y0u_3v3n_` |
| PowerShell | `FLAG_FINAL` output | `runn1ng?}` |

The Windows value is Base64. Decoding it gives `CTF{wh4t_`.

### Step 2: Reassemble the flag

The following validator starts from the supplied ZIP, unwraps the packages with `7z`, and extracts the embedded evidence from the native payloads:

```python
#!/usr/bin/env python3
import base64
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

archive = sys.argv[1] if len(sys.argv) > 1 else "terminal-download-1788444688711.zip"

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    packages = root / "packages"
    payloads = root / "payloads"
    packages.mkdir()
    payloads.mkdir()

    with zipfile.ZipFile(archive) as zf:
        zf.extractall(packages)

    for package in packages.iterdir():
        out = payloads / package.name
        out.mkdir()
        subprocess.run(
            ["7z", "x", "-y", f"-o{out}", str(package)],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # RPM and DEB contain one additional cpio/tar layer.
        expanded = set()
        while True:
            nested = [
                p for p in out.rglob("*")
                if p.is_file() and p.suffix in {".cpio", ".tar"}
                and p not in expanded
            ]
            if not nested:
                break
            for nested_archive in nested:
                expanded.add(nested_archive)
                subprocess.run(
                    ["7z", "x", "-y", f"-o{out}", str(nested_archive)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )

    corpus = b"\n".join(
        path.read_bytes() for path in payloads.rglob("*") if path.is_file()
    )

def capture(pattern):
    match = re.search(pattern, corpus)
    if not match:
        raise SystemExit(f"missing evidence: {pattern!r}")
    return match.group(1)

part1 = base64.b64decode(capture(rb'"Part1_B64"="([^"]+)"'))
part2 = capture(rb'PART2_FRAGMENT="([^"]+)"')
part3 = capture(rb'(y0u_3v3n_)')
part4 = capture(rb'FLAG_FINAL\s+([^\s]+)')

flag = part1 + part2 + part3 + part4
print(flag.decode())
```

Output:

```text
CTF{wh4t_0s_4r3_y0u_3v3n_runn1ng?}
```

## Flag

```text
CTF{wh4t_0s_4r3_y0u_3v3n_runn1ng?}
```
