# Monad's first year by app: count the distinct wallets that sent a transaction to each app's main contracts, with Envio HyperSync.
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

APPS = {
    "Nad.fun": ["0x0b79d71ae99528d1db24a4148b5f4f865cc2b137", "0x6f6b8f1a20703309951a5127c45b49b1cd981a22", "0x8986c8fd44eb85294a725a7e61af35e76ba26f91"],
    "Unnamed router": ["0x81b8e2832d00381449223d9874f041114ebd36b8"],
    "Uniswap": ["0x0d97dc33264bfc1c226207428a79b26757fb9dc3", "0xfdf682f51fe81aa4898f0ae2163d8a55c127fbc7"],
    "Matcha": ["0x0000000000001ff3684f28c67538d4d072c22734"],
    "FastLane (shMonad)": ["0x1b68626dca36c7fe922fd2d55e4f631d962de19c"],
    "Pinot Finance": ["0x252b9c1a6c9867a514ea70fe9bbb23621acc1a50"],
    "Lumiterra": ["0xda4b24b5e1547d04ab9e4910a747f2d7f893d5ab"],
    "PancakeSwap": ["0x21114915ac6d5a2e156931e20b20b038ded0be7c", "0x23682a588cf2601aca977df200938634c9f7d552", "0x1b81d678ffb9c0263b24a97847620c99d213eb14"],
    "GMGN": ["0xc9ca80b5ea956afa98627963d1880033545d108e"],
    "LI.FI": ["0x026f252016a7c47cdef1f05a3fc9e20c92a49c37", "0x3c6b2e0b7421254846c53c118e24c65d59eae75e"],
    "OpenSea": ["0x00005ea00ac477b1030ce78506496e8c2de24bf5"],
}
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
