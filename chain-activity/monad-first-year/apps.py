# Monad's first year by app: count the distinct wallets that sent a transaction to any of each app's contracts, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 apps.py            the first year (launch block to the one-year mark), 8 workers
#        python3 apps.py FROM TO    a fixed block range
# Contract names come from Monad's protocol registry (github.com/monad-crypto/protocols) and the Monad dApp list.
import json
import os
import sys
import time
import urllib.request
from multiprocessing import Pool

TOKEN = os.environ.get("ENVIO_API_TOKEN")
if not TOKEN:
    sys.exit("Set ENVIO_API_TOKEN (get one at https://envio.dev/app/api-tokens)")

URL = "https://monad.hypersync.xyz"
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
LAUNCH_BLOCK, ONE_YEAR_END = 37_700_069, 125_021_857
SHARD = 1_000_000

# Every contract listed for each app in Monad's protocol registry and the Monad dApp list (apps.json).
# Add your own app to apps.json as "Name": ["0x...", "0x..."] and run the script again.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps.json")) as f:
    APPS = {app: [a.lower() for a in addrs] for app, addrs in json.load(f).items()}
OWNER = {a: app for app, addrs in APPS.items() for a in addrs}


def post(body):
    req = urllib.request.Request(URL + "/query", json.dumps(body).encode(), HEADERS)
    for attempt in range(12):
        try:
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception:  # rate limits and timeouts: wait and try again
            time.sleep(2 * (attempt + 1))
    sys.exit("HyperSync kept failing")


def shard(bounds):
    lo, hi = bounds
    wallets = {app: set() for app in APPS}
    cursor = lo
    while cursor < hi:
        res = post({
            "from_block": cursor,
            "to_block": hi,
            "transactions": [{"to": list(OWNER)}],
            "field_selection": {"transaction": ["to", "from"]},
        })
        for chunk in res["data"]:
            for tx in chunk.get("transactions", []):
                app = OWNER.get((tx.get("to") or "").lower())
                if app:
                    wallets[app].add(int(tx["from"][2:18], 16))  # first 8 bytes of the address
        if res["next_block"] <= cursor:
            break
        cursor = res["next_block"]
    return wallets


if __name__ == "__main__":
    start, end = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) == 3 else (LAUNCH_BLOCK, ONE_YEAR_END)
    ranges = [(b, min(b + SHARD, end)) for b in range(start, end, SHARD)]
    total = {app: set() for app in APPS}
    with Pool(8) as pool:
        for i, part in enumerate(pool.imap_unordered(shard, ranges), 1):
            for app, s in part.items():
                total[app] |= s
            print(f"{i}/{len(ranges)} block ranges done", flush=True)
    print()
    for app, s in sorted(total.items(), key=lambda kv: -len(kv[1])):
        print(f"{app:<20} {len(s):>10,} wallets")
