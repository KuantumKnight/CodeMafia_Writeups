---
title: "Precision Engine"
ctf: "Unknown"
date: 2026-09-04
category: web
difficulty: "Unknown"
points: "Unknown"
flag_format: "CTF{...}"
author: "Codex"
---

# Precision Engine

## Summary

The Sepolia contract exposes a target-burn getter and a simulator. Querying the getter gives `535480`; searching the simulator identifies RPM `350` as the unique tested input producing that burn. Calling `revEngine(350)` returns the flag.

## Solution

### Query and calibrate

The target contract is `0xac7c5dd349a6239c7b98a3ceaa4a9439408456Bb` on Sepolia.

```python
import json
from urllib.request import Request, urlopen

rpc = "https://ethereum-sepolia-rpc.publicnode.com"
address = "0xac7c5dd349a6239c7b98a3ceaa4a9439408456bb"
target = 535480  # eth_call selector 0x7c1b4797 returns 0x82bb8

def call(data):
    body = json.dumps({"jsonrpc":"2.0", "method":"eth_call",
                       "params":[{"to":address, "data":data}, "latest"},
                       "id":1}).encode()
    req = Request(rpc, data=body, headers={"content-type":"application/json"})
    return json.loads(urlopen(req).read())["result"]

for rpm in range(1000):
    burn = int(call("0x17980b41" + f"{rpm:064x}"), 16)
    if burn == target:
        result = call("0x3b387aad" + f"{rpm:064x}")
        payload = bytes.fromhex(result[2:])
        offset = int.from_bytes(payload[:32], "big")
        length = int.from_bytes(payload[offset:offset+32], "big")
        print(payload[offset+32:offset+32+length].decode())
        break
```

Output:

```text
SUCCESS: CTF{g4s_m4st3r_ch40s_pwl3d!}
```

## Flag

```text
CTF{g4s_m4st3r_ch40s_pwl3d!}
```
