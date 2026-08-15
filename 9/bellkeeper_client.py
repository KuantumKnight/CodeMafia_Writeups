#!/usr/bin/env python3
"""Sequential binary-search client for Buddy: The Bellkeeper's Sequence.

The passage values are monotonic by endpoint. A response's ``next_token``
must be sent with the next request, so the search remains strictly serial.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE = "https://recipient-gizmo-ecology.ngrok-free.dev"
TARGET_SYN = 6767


def masked(value: str) -> str:
    """Show enough of a credential to identify rotation without leaking it."""
    if len(value) <= 12:
        return "<redacted>"
    return f"{value[:8]}...{value[-4:]}"


def request_json(base: str, path: str, *, method: str = "GET",
                 headers: dict[str, str] | None = None,
                 timeout: int = 120) -> tuple[int, dict]:
    request = Request(base.rstrip("/") + path, method=method,
                      headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
        return exc.code, payload
    except URLError as exc:
        raise RuntimeError(f"network error for {path}: {exc.reason}") from exc


def reset(base: str, timeout: int) -> tuple[str, str]:
    status, payload = request_json(base, "/session/reset", method="POST",
                                    timeout=timeout)
    if status != 200:
        raise RuntimeError(f"session reset failed ({status}): {payload}")
    token = payload.get("current_token")
    session_id = payload.get("session_id", "")
    if not token:
        raise RuntimeError(f"reset response has no token: {payload}")
    return token, session_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--direct", type=int, metavar="PASSAGE",
                        help="query one known passage instead of searching")
    parser.add_argument("--max-queries", type=int, default=15)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=2.5,
                        help="seconds between passage requests")
    parser.add_argument("--retry-wait", type=int, default=65,
                        help="seconds to wait after a 429 response")
    args = parser.parse_args()

    if args.direct is not None and not 0 <= args.direct <= 999:
        parser.error("--direct must be between 0 and 999")

    token, session_id = reset(args.base, args.timeout)

    if args.direct is not None:
        endpoint = args.direct
        print("[session] reset succeeded")
        print(f"[direct] querying /{endpoint} with the chained token")
        headers = {"X-Session-Token": token}
        if session_id:
            headers["X-Session-ID"] = session_id
        status, payload = request_json(args.base, f"/{endpoint}",
                                        headers=headers,
                                        timeout=args.timeout)
        if status != 200:
            print(f"[error] /{endpoint}: HTTP {status}: {payload}",
                  file=sys.stderr)
            return 2
        print(f"[response] /{endpoint} -> syn={payload.get('syn')}; "
              f"remaining={payload.get('queries_remaining', 'unknown')}")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload.get("syn") == TARGET_SYN else 1

    low, high = 0, 999
    print("[session] reset succeeded")
    print(f"[session] id={masked(session_id) if session_id else '<not provided'}")
    print("[search] binary search over passages /0 through /999")
    print(f"[search] target syn={TARGET_SYN}; budget={args.max_queries}")

    for query_number in range(1, args.max_queries + 1):
        if low > high:
            print("[search] bounds crossed; target is not present")
            break
        endpoint = (low + high) // 2
        if query_number > 1:
            print(f"[wait] sleeping {args.delay:g}s before next request")
            time.sleep(args.delay)
        print(f"\n[query {query_number}/{args.max_queries}] bounds={low}..{high}; "
              f"trying /{endpoint}")
        print(f"[query] sending token={masked(token)}")
        headers = {"X-Session-Token": token}
        # This header is not in the public challenge description, but the
        # live service exposes a session_id and has shown worker-affinity
        # problems.  Supplying it improves reproducibility when accepted.
        if session_id:
            headers["X-Session-ID"] = session_id

        status, payload = request_json(args.base, f"/{endpoint}",
                                        headers=headers,
                                        timeout=args.timeout)
        if status == 429:
            print(f"query {query_number}: server still has a request in flight; "
                  f"waiting {args.retry_wait}s", file=sys.stderr)
            time.sleep(args.retry_wait)
            print(f"[retry] repeating /{endpoint} with the same token")
            status, payload = request_json(args.base, f"/{endpoint}",
                                            headers=headers,
                                            timeout=args.timeout)

        if status != 200:
            print(f"query {query_number} /{endpoint}: HTTP {status}: {payload}",
                  file=sys.stderr)
            return 2

        syn = payload.get("syn")
        next_token = payload.get("next_token")
        if not isinstance(syn, int) or not next_token:
            print(f"unexpected passage response: {payload}", file=sys.stderr)
            return 2

        used = payload.get("queries_used", query_number)
        remaining = payload.get("queries_remaining", "unknown")
        print(f"[response] /{endpoint} -> syn={syn}; used={used}; "
              f"remaining={remaining}")
        if syn == TARGET_SYN:
            print(f"[success] target found at /{endpoint}")
            print(json.dumps(payload, indent=2, sort_keys=True))
            print("TARGET REACHED")
            return 0

        token = next_token
        if syn < TARGET_SYN:
            low = endpoint + 1
            print(f"[compare] {syn} < {TARGET_SYN}; next bounds={low}..{high}")
        else:
            high = endpoint - 1
            print(f"[compare] {syn} > {TARGET_SYN}; next bounds={low}..{high}")

    print(f"target syn {TARGET_SYN} was not reached within {args.max_queries} queries",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
