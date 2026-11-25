"""Variational Omni on Arbitrum: every user's settlement pool, counted with HyperSync.

On Omni each user gets their own bilateral settlement pool with the OLP, created by the
Settlement Pool Factory (docs.variational.io, Mainnet Contracts). This pulls every pool
creation event from the factory and counts pools, unique user wallets and daily signups.

Run:  ENVIO_API_TOKEN=... python3 script.py [to_block]
Standard library only.
"""
import collections, datetime, json, os, sys, time, urllib.request

TOKEN = os.environ["ENVIO_API_TOKEN"]
URL = "https://arbitrum.hypersync.xyz"
FACTORY = "0x0F820B9afC270d658a9fD7D16B1Bdc45b70f074C"
POOL_CREATED = "0x0b33722ea9d97f05fb7128e0987e4060c182350308a3d0a19f8ec53512fe1493"
START = 300_000_000  # factory deployed at block 300,692,000 (30 Jan 2025)


def call(path, body=None):
    for i in range(6):
        try:
            req = urllib.request.Request(URL + path, data=json.dumps(body).encode() if body else None,
                                         headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:
            print("retry", e, file=sys.stderr); time.sleep(2 * (i + 1))
    raise SystemExit("HyperSync request failed")


def main():
    to_block = int(sys.argv[1]) if len(sys.argv) > 1 else call("/height")["height"]
    pools, users = set(), set()
    first_day = {}
    per_day = collections.Counter()
    blk = START
    while blk < to_block:
        r = call("/query", {"from_block": blk, "to_block": to_block, "max_num_logs": 200000,
                            "logs": [{"address": [FACTORY], "topics": [[POOL_CREATED]]}],
                            "field_selection": {"log": ["block_number", "data"], "block": ["number", "timestamp"]}})
        ts = {}
        for d in r["data"]:
            for b in d.get("blocks") or []:
                ts[b["number"]] = int(b["timestamp"], 16) if isinstance(b["timestamp"], str) else b["timestamp"]
            for l in d.get("logs") or []:
                w = l["data"][2:]
                pool, user = "0x" + w[64 + 24:128], "0x" + w[4 * 64 + 24:5 * 64]  # data words 1 and 4
                day = datetime.datetime.fromtimestamp(ts[l["block_number"]], datetime.UTC).strftime("%Y-%m-%d")
                pools.add(pool)
                per_day[day] += 1
                if user not in users:
                    users.add(user); first_day[user] = day
        if r["next_block"] <= blk:
            break
        blk = r["next_block"]
    new_users = collections.Counter(first_day.values())
    days = sorted(per_day)
    print(f"Arbitrum blocks {START:,} to {to_block:,} ({days[0]} to {days[-1]} UTC)")
    print(f"settlement pools created: {len(pools):,}")
    print(f"unique user wallets: {len(users):,}")
    best = max(days, key=lambda d: new_users[d])
    print(f"record day for new users: {best} with {new_users[best]:,}")
    for since in ("2026-11-11", "2026-11-16"):
        n = sum(new_users[d] for d in days if d >= since)
        print(f"new user wallets since {since}: {n:,}")
    print("\nlast 30 days (day, pools created, first-time user wallets)")
    for d in days[-30:]:
        print(d, per_day[d], new_users[d])
    by_month = collections.Counter()
    for d in days:
        by_month[d[:7]] += new_users[d]
    print("\nnew user wallets by month")
    for m in sorted(by_month):
        print(m, by_month[m])


if __name__ == "__main__":
    main()
