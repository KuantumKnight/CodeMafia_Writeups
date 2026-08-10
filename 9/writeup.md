# The Bellkeeper's Sequence — Write-up

**Category:** Web / API logic
**Flag:** `FLAG{r0t4t3d_syn_ch41n_budd13s_m4st3r3d}`
**Answer passage:** `/942`
**Queries used:** 9 / 15

---

## 1. The Challenge

The target exposes 1,000 numbered "passages" (`/0`–`/999`), each returning a
unique value in `0–10000` under the JSON key `syn`. The goal is to find the
passage whose `syn` equals **6767** and read the flag it returns.

Backend: `https://recipient-gizmo-ecology.ngrok-free.dev`

Rules that shape the solution:

- **Limited budget** — 15 queries per session, then `403`.
- **Rotating seal** — every request needs an `X-Session-Token`; each response
  returns a *new* token (`next_token`) that must be used on the very next call.
- **One at a time** — concurrent requests get `429 Too Many Requests`
  ("Only 1 in-flight request allowed per IP").

Endpoints:

| Path              | Method | Purpose                       |
|-------------------|--------|-------------------------------|
| `/session`        | GET    | Start / retrieve a session    |
| `/session/reset`  | POST   | Fresh session, 15-query budget|
| `/ping`           | GET    | Health check                  |
| `/0`–`/999`       | GET    | Question a passage            |

---

## 2. The Key Insight

A 15-query budget against 1,000 passages rules out any linear scan. The puzzle
text — *"trace the sequence"* — plus a quick sample confirmed the values are
**monotonically increasing with index**:

```
/499 -> 475
/749 -> 3907
```

Sorted values + indexed lookup = **binary search**. log2(1000) ≈ 9.97, so ~10
queries pin the target — which is exactly what the 15-query budget is tuned for.

The token seal just forces the search to be **sequential**: response N's
`next_token` is the credential for request N+1.

---

## 3. The Traps (and why early attempts failed)

The machine actively punishes any deviation from "one client, in order":

- **`401 invalid or out-of-order HMAC session token`** — the token is an HMAC
  chain the server expects consumed in strict order. Running the solver in a
  second terminal/tab issued its own `reset`, bumping the server's expected
  token and desyncing the first run's chain.
- **`401 no active session found`** — a client-side timeout on the slow tunnel
  fired *after* the server had already advanced the chain, leaving the local
  token stale.
- **`429 Anti-Spray: only 1 in-flight request`** — two overlapping requests
  from the same IP (often a stuck request from a prior run still holding the
  lock).
- **`ERR_NGROK_3200 (offline)`** — at one point the tunnel's backend was simply
  down; every path returned ngrok's HTML offline page.
- **ngrok browser interstitial** — browser-origin requests hit the "You are
  about to visit" page instead of the API. Fixed by sending the
  `ngrok-skip-browser-warning` header (curl avoided this automatically via its
  non-browser User-Agent).

**Takeaway:** none of these were bugs in the solve logic. They were all
symptoms of *parallelism / overlap* against a strictly-serial, IP-keyed,
rotating-token session. The cure was discipline, not cleverness: **one client,
one request at a time, chain every `next_token`, and space the hops** so the
1-in-flight lock always clears.

---

## 4. Working Solution

Run from the browser console **on the ngrok origin** (so the skip-warning header
applies and requests use Windows-native networking):

```js
const B="https://recipient-gizmo-ecology.ngrok-free.dev", TARGET=6767;
const H={"ngrok-skip-browser-warning":"1"};
const wait=ms=>new Promise(r=>setTimeout(r,ms));

async function q(path,tok,post){
  for(let a=0;a<8;a++){
    let o={headers:{...H}};
    if(post)o.method="POST";
    if(tok)o.headers["X-Session-Token"]=tok;
    let r=await (await fetch(B+path,o)).json();
    if(r.syn!==undefined||r.current_token) return r;  // good response
    console.log("  retry("+path+"):", r.message);
    await wait(6000);                                 // back off 429/401
  }
  throw "stuck "+path;
}

(async()=>{
  let s=await q("/session/reset",null,true);
  let t=s.current_token;
  console.log("start budget",s.queries_remaining);
  let lo=0,hi=999;
  while(lo<=hi){
    await wait(2500);                                 // stay under 1-in-flight
    let mid=(lo+hi)>>1, r=await q("/"+mid,t);
    t=r.next_token;                                   // chain the seal
    console.log("/"+mid+" -> "+r.syn+"  (left "+r.queries_remaining+")");
    if(r.syn===TARGET){console.log("=== FOUND /"+mid+" ===",JSON.stringify(r));return;}
    r.syn<TARGET?lo=mid+1:hi=mid-1;
  }
})();
```

Why it works:
- **Single chained session** — one `reset`, then each response's `next_token`
  feeds the next request. No second client, so the HMAC chain never desyncs.
- **2.5 s between hops** — guarantees the previous request finished, so the
  1-in-flight lock is clear.
- **6 s retry on any 429/401 blip** — absorbs tunnel hiccups without breaking
  the chain (it retries the *same* index with the *same* token).

---

## 5. The Trace

```
start budget 15
/499 -> 475   (left 14)
/749 -> 3907  (left 13)
/874 -> 5747  (left 12)
/937 -> 6660  (left 11)
/968 -> 6904  (left 10)
/952 -> 6829  (left 9)
/944 -> 6784  (left 8)
/940 -> 6715  (left 7)
/942 -> 6767  (left 6)
=== FOUND /942 ===
```

Server response at `/942`:

```json
{
  "endpoint": 942,
  "syn": 6767,
  "queries_used": 9,
  "queries_remaining": 6,
  "hint": "FLAG{r0t4t3d_syn_ch41n_budd13s_m4st3r3d}",
  "message": "Target SYN 6767 found in 9 queries! Challenge Solved."
}
```

---

## 6. Flag

```
FLAG{r0t4t3d_syn_ch41n_budd13s_m4st3r3d}
```

Format `XXXX{7_3_5_7_8}`:
`r0t4t3d`(7) · `syn`(3) · `ch41n`(5) · `budd13s`(7) · `m4st3r3d`(8) ✓

The flag is self-describing: a **rotated syn-chain**. The seal rotated on every
hop, so any overlapping ("buddies") client desynced it — every `401`/`429` we
hit was the chain enforcing strict, single-client ordering. Solve it serially
and it falls in 9 queries.
