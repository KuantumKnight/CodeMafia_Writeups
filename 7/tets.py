import requests
import re
import json
import sys
import time

BASE = "https://recipient-gizmo-ecology.ngrok-free.dev"
TARGET = 6767

s = requests.Session()

COMMON_HEADERS = {
    "Accept": "application/json",
    "ngrok-skip-browser-warning": "1",
    "Connection": "close"
}


def extract_token(response, data):
    token = response.headers.get("X-Session-Token")

    if token:
        return token

    for key in [
        "current_token",
        "token",
        "session_token",
        "sessionToken",
        "next_token",
        "nextToken",
        "x_session_token",
        "seal"
    ]:
        if isinstance(data, dict) and isinstance(data.get(key), str):
            return data[key]

    return None


def extract_value(data):
    for key in [
        "syn",
        "value",
        "sequence",
        "sequence_value",
        "sequence_number",
        "sequenceNumber",
        "synchronized_sequence_number"
    ]:
        if key in data:
            try:
                return int(data[key])
            except:
                pass

    return None


def find_flag(data):
    text = json.dumps(data)

    m = re.search(r'[A-Za-z0-9_-]+\{[^}]+\}', text)

    if m:
        return m.group(0)

    return None


def start_session():
    print("[*] Resetting session...")

    r = s.post(
        BASE + "/session/reset",
        headers=COMMON_HEADERS,
        timeout=20
    )

    print("[+] Status:", r.status_code)

    try:
        data = r.json()
    except:
        print(r.text)
        sys.exit(1)

    print(json.dumps(data, indent=2))

    token = extract_token(r, data)

    if not token:
        print("[!] No current_token found")
        sys.exit(1)

    print("\n[*] Waiting for anti-spray lock to clear...")
    time.sleep(2)

    return token


def query(index, token):
    for attempt in range(1, 8):

        try:
            r = requests.get(
                f"{BASE}/{index}",
                headers={
                    **COMMON_HEADERS,
                    "X-Session-Token": token
                },
                timeout=20
            )
        except requests.RequestException as e:
            print("[!] Request error:", e)
            time.sleep(2)
            continue

        try:
            data = r.json()
        except:
            data = {"raw": r.text}

        if r.status_code == 429:
            print(
                f"[!] /{index} -> 429 anti-spray lock "
                f"(attempt {attempt}/7)"
            )

            # IMPORTANT:
            # retry the SAME request with SAME token
            time.sleep(1.5 * attempt)
            continue

        print(f"\n[>] /{index} -> HTTP {r.status_code}")
        print(json.dumps(data, indent=2))

        if r.status_code != 200:
            return None, token, data

        new_token = extract_token(r, data)
        value = extract_value(data)

        print(f"[+] Value: {value}")

        if not new_token:
            print("[!] Response did not contain next token")
            print("[!] Full response above.")
            sys.exit(1)

        # Give backend time to release its per-IP lock
        time.sleep(0.8)

        return value, new_token, data

    print(f"[!] /{index} stayed locked after retries.")
    sys.exit(1)


def win(index, data):
    print("\n" + "=" * 60)
    print("TARGET FOUND")
    print("=" * 60)

    print("Passage:", f"/{index}")
    print("Value  :", TARGET)

    flag = find_flag(data)

    if flag:
        print("FLAG   :", flag)
    else:
        print("\nWinning response:")
        print(json.dumps(data, indent=2))

    print("=" * 60)


token = start_session()

#
# Probe endpoints to determine sequence direction
#

v0, token, d0 = query(0, token)

if v0 == TARGET:
    win(0, d0)
    sys.exit(0)

if v0 is None:
    print("\n[!] First successful response was unexpected.")
    sys.exit(1)


v999, token, d999 = query(999, token)

if v999 == TARGET:
    win(999, d999)
    sys.exit(0)

if v999 is None:
    sys.exit(1)


print("\n[*] /0   =", v0)
print("[*] /999 =", v999)

ascending = v0 < v999

print(
    "[+] Direction:",
    "ASCENDING" if ascending else "DESCENDING"
)


#
# Binary search
#

lo = 1
hi = 998

while lo <= hi:

    mid = (lo + hi) // 2

    value, token, data = query(mid, token)

    if value is None:
        print("[!] Query failed")
        sys.exit(1)

    if value == TARGET:
        win(mid, data)
        sys.exit(0)

    if ascending:

        if value < TARGET:
            lo = mid + 1
        else:
            hi = mid - 1

    else:

        if value > TARGET:
            lo = mid + 1
        else:
            hi = mid - 1


print("\n[!] Binary search ended without finding 6767.")
print("[!] Paste the passage responses above here.")
