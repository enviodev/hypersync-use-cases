"""Tokenized gold on Ethereum (PAXG + XAUT): ounces onchain, holders, growth.

Pulls every Transfer of PAXG and XAUT on Ethereum with HyperSync, rebuilds every
balance from scratch and compares today with one and two years ago.

Run:  ENVIO_API_TOKEN=... python3 script.py [to_block]
Standard library only. Uses 4 worker processes.
"""
import collections, datetime, json, os, sys, urllib.request, time
from multiprocessing import Pool

TOKEN = os.environ["ENVIO_API_TOKEN"]
URL = "https://eth.hypersync.xyz"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TOKENS = {  # name: (address, decimals, first block to scan)
    "PAXG": ("0x45804880De22913dAFE09f4980848ECE6EcbAf78", 18, 6_000_000),
    "XAUT": ("0x68749665FF8D2d112Fa859AA293F07A622782F38", 6, 9_000_000),
}
ZERO = "0" * 40
GRAMS_PER_OZ = 31.1034768
CUTOFFS = {"2024-11-25": 1732492800, "2025-11-25": 1764028800}


def call(path, body=None):
    for i in range(6):
        try:
            req = urllib.request.Request(URL + path, data=json.dumps(body).encode() if body else None,
                                         headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:
            print("retry", e, file=sys.stderr); time.sleep(2 * (i + 1))
    raise SystemExit("HyperSync request failed")


def pull(job):
    """Every Transfer of one token in [a, b) as (block, log_index, ts, from, to, value)."""
    addr, a, b = job
    out, blk = [], a
    while blk < b:
        r = call("/query", {"from_block": blk, "to_block": b, "max_num_logs": 200000,
                            "logs": [{"address": [addr], "topics": [[TRANSFER]]}],
                            "field_selection": {"log": ["block_number", "log_index", "topic1", "topic2", "data"],
                                                "block": ["number", "timestamp"]}})
        ts = {}
        for d in r["data"]:
            for bl in d.get("blocks") or []:
                ts[bl["number"]] = int(bl["timestamp"], 16) if isinstance(bl["timestamp"], str) else bl["timestamp"]
            for l in d.get("logs") or []:
                if not l.get("topic2"):
                    continue
                v = int(l["data"][:66], 16) if len(l["data"]) > 2 else 0
                out.append((l["block_number"], l["log_index"], ts[l["block_number"]], l["topic1"][-40:], l["topic2"][-40:], v))
        if r["next_block"] <= blk:
            break
        blk = r["next_block"]
    return out


def main():
    to_block = int(sys.argv[1]) if len(sys.argv) > 1 else call("/height")["height"]
    print(f"Ethereum up to block {to_block:,}\n")
    snaps = {}  # (token, label) -> {holder: balance}
    with Pool(4) as pool:
        for name, (addr, dec, start) in TOKENS.items():
            edges = [start + (to_block - start) * i // 40 for i in range(41)]
            bal = collections.defaultdict(int)
            labels = sorted(CUTOFFS.items(), key=lambda kv: kv[1])
            i = n = 0
            for part in pool.imap(pull, [(addr, a, b) for a, b in zip(edges, edges[1:])]):
                part.sort(key=lambda x: (x[0], x[1]))
                n += len(part)
                for bn, li, ts, f, t, v in part:
                    while i < len(labels) and ts >= labels[i][1]:
                        snaps[(name, labels[i][0])] = {a: x for a, x in bal.items() if x > 0}; i += 1
                    if f != ZERO: bal[f] -= v
                    if t != ZERO: bal[t] += v
            while i < len(labels):
                snaps[(name, labels[i][0])] = {a: x for a, x in bal.items() if x > 0}; i += 1
            snaps[(name, "now")] = {a: x for a, x in bal.items() if x > 0}
            print(f"{name}: {n:,} transfers pulled")
    print()
    for label in list(CUTOFFS) + ["now"]:
        oz, holders, holders_001 = 0.0, set(), set()
        for name, (addr, dec, _) in TOKENS.items():
            s = snaps[(name, label)]
            t_oz = sum(s.values()) / 10 ** dec
            h001 = {a for a, x in s.items() if x >= 10 ** dec // 100}
            print(f"{label} {name}: {t_oz:,.2f} oz, {len(s):,} holders, {len(h001):,} holding 0.01 oz or more")
            oz += t_oz; holders |= set(s); holders_001 |= h001
        print(f"{label} combined: {oz:,.0f} oz = {oz * GRAMS_PER_OZ / 1e6:,.1f} tonnes, "
              f"{len(holders):,} unique wallets, {len(holders_001):,} holding 0.01 oz or more\n")


if __name__ == "__main__":
    main()
