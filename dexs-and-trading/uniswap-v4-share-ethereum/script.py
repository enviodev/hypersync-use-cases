# Uniswap on Ethereum: count every v2, v3 and v4 swap month by month since v4 launched, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 script.py               from v4's launch to now, 8 workers
#        python3 script.py FROM TO       a fixed block range
import collections
import datetime
import json
import os
import sys
import time
import urllib.request
from multiprocessing import Pool

TOKEN = os.environ.get("ENVIO_API_TOKEN")
if not TOKEN:
    sys.exit("Set ENVIO_API_TOKEN (get one at https://envio.dev/app/api-tokens)")

URL = "https://eth.hypersync.xyz"
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}

# Addresses from the Uniswap docs (docs.uniswap.org/contracts/v4/deployments and the v2 and v3 deployment pages)
POOL_MANAGER = "0x000000000004444c5dc75cb358380d2e3de08a90"  # v4, every v4 pool lives here
V3_FACTORY = "0x1f98431c8ad98523631ae4a59f267346ea31f984"
V2_FACTORY = "0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f"
V4_SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"  # Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)
V3_SWAP = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"  # Swap(address,address,int256,int256,uint160,uint128,int24)
V2_SWAP = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"  # Swap(address,uint256,uint256,uint256,uint256,address)
V3_POOL_CREATED = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"
V2_PAIR_CREATED = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
V4_LAUNCH_BLOCK = 21_688_329
CHUNK = 200_000


def post(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(URL + path, data, HEADERS)
    for attempt in range(10):
        try:
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception:  # rate limits and timeouts: wait and try again
            time.sleep(3 * (attempt + 1))
    sys.exit("HyperSync kept failing")


def num(v):
    return v if isinstance(v, int) else int(v, 16)


def scan(body, to_block):
    cursor = body["from_block"]
    while cursor < to_block:
        body["from_block"] = cursor
        res = post("/query", body)
        yield res
        if res["next_block"] <= cursor:
            break
        cursor = res["next_block"]


def created(factory, topic, start, head, slice_):
    """Every pool or pair address a factory has created."""
    out = set()
    body = {"from_block": start, "to_block": head, "logs": [{"address": [factory], "topics": [[topic]]}],
            "field_selection": {"log": ["data"]}}
    for res in scan(body, head):
        for chunk in res["data"]:
            for log in chunk.get("logs", []):
                out.add("0x" + log["data"][slice_].lower())
    return out


V3_POOLS = V2_PAIRS = None


CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".uniswap_pools.json")


def init():
    """Each worker reads the pool and pair lists the main process saved."""
    global V3_POOLS, V2_PAIRS
    with open(CACHE) as f:
        lists = json.load(f)
    V3_POOLS, V2_PAIRS = set(lists["v3"]), set(lists["v2"])


def count(bounds):
    lo, hi = bounds
    per_month = collections.defaultdict(collections.Counter)
    stamp = {}
    body = {"from_block": lo, "to_block": hi, "logs": [{"topics": [[V4_SWAP, V3_SWAP, V2_SWAP]]}],
            "field_selection": {"log": ["address", "topic0", "block_number"], "block": ["number", "timestamp"]}}
    for res in scan(body, hi):
        for chunk in res["data"]:
            for b in chunk.get("blocks", []):
                stamp[num(b["number"])] = num(b["timestamp"])
            for log in chunk.get("logs", []):
                addr, t = log["address"].lower(), log["topic0"]
                if t == V4_SWAP and addr == POOL_MANAGER:
                    version = "v4"
                elif t == V3_SWAP and addr in V3_POOLS:
                    version = "v3"
                elif t == V2_SWAP and addr in V2_PAIRS:
                    version = "v2"
                else:
                    continue  # forks and other DEXs that reuse the same event
                month = datetime.datetime.fromtimestamp(stamp[num(log["block_number"])], datetime.timezone.utc).strftime("%Y-%m")
                per_month[month][version] += 1
    return per_month


if __name__ == "__main__":
    head = post("/height")["height"]
    start, end = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) == 3 else (V4_LAUNCH_BLOCK, head)
    print("Listing every Uniswap v3 pool and v2 pair...", flush=True)
    v3 = created(V3_FACTORY, V3_POOL_CREATED, 12_369_621, end, slice(-40, None))
    v2 = created(V2_FACTORY, V2_PAIR_CREATED, 10_000_835, end, slice(26, 66))
    print(f"{len(v3):,} v3 pools and {len(v2):,} v2 pairs", flush=True)
    with open(CACHE, "w") as f:
        json.dump({"v3": sorted(v3), "v2": sorted(v2)}, f)
    ranges = [(b, min(b + CHUNK, end)) for b in range(start, end, CHUNK)]
    total = collections.defaultdict(collections.Counter)
    with Pool(8, initializer=init) as pool:
        for i, part in enumerate(pool.imap_unordered(count, ranges), 1):
            for month, c in part.items():
                total[month].update(c)
            print(f"{i}/{len(ranges)} block ranges done", flush=True)
    print()
    print(f"{'Month':<8} {'v4 swaps':>11} {'v3 swaps':>11} {'v2 swaps':>11} {'v4 share':>9}")
    for month in sorted(total):
        c = total[month]
        s = sum(c.values())
        print(f"{month:<8} {c['v4']:>11,} {c['v3']:>11,} {c['v2']:>11,} {100 * c['v4'] / s:>8.1f}%")
