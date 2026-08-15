# Bellkeeper client

The original workspace had no challenge source files. These reconstructed
artifacts are:

- `bellkeeper_client.py` — a serial, token-chained binary-search client.
- `writeup.md` — the successful trace and recovered flag.

Run the client with:

```sh
python3 bellkeeper_client.py
```

It starts a fresh 15-query session, searches `/0`–`/999`, and stops when the
returned `syn` is `6767`. The live tunnel can hold a request for about a
minute, so the default request timeout is 120 seconds.
