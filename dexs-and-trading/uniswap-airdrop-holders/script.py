# Uniswap's 2020 UNI airdrop: how many of the wallets that claimed it still hold UNI today, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 script.py
import collections
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
UNI = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
AIRDROP = "090d4613473dee047c3f2706764f49e0821d256e"  # the MerkleDistributor that paid out the September 2020 airdrop
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
UNI_DEPLOYED = 10_861_674
CHUNK = 500_000
FULL_DROP = 400 * 10**18  # 400 UNI, what each past user received


def post(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(URL + path, data, HEADERS)
    for attempt in range(12):
        try:
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception:  # rate limits and timeouts: wait and try again
            time.sleep(3 * (attempt + 1))
    sys.exit("HyperSync kept failing")


def replay(bounds):
    """Net UNI change per wallet over one block range, and who received from the airdrop contract."""
    lo, hi = bounds
    balance = collections.defaultdict(int)
    claimed = set()
    cursor = lo
    while cursor < hi:
        res = post("/query", {"from_block": cursor, "to_block": hi, "logs": [{"address": [UNI], "topics": [[TRANSFER]]}],
                              "field_selection": {"log": ["topic1", "topic2", "data"]}})
        for chunk in res["data"]:
            for log in chunk.get("logs", []):
                sender, receiver, value = log["topic1"][-40:], log["topic2"][-40:], int(log["data"], 16)
                balance[sender] -= value
                balance[receiver] += value
                if sender == AIRDROP:
                    claimed.add(receiver)
        if res["next_block"] <= cursor:
            break
        cursor = res["next_block"]
    return dict(balance), claimed


if __name__ == "__main__":
    head = post("/height")["height"]
    ranges = [(b, min(b + CHUNK, head)) for b in range(UNI_DEPLOYED, head, CHUNK)]
    balance = collections.defaultdict(int)
    claimed = set()
    with Pool(4) as pool:  # 4 workers keeps memory in check
        for i, (part, c) in enumerate(pool.imap_unordered(replay, ranges), 1):
            claimed |= c
            for k, v in part.items():
                balance[k] += v
            print(f"{i}/{len(ranges)} block ranges done", flush=True)
    still = [w for w in claimed if balance[w] > 0]
    full = [w for w in still if balance[w] >= FULL_DROP]
    holders = sum(1 for w, v in balance.items() if v > 0 and w != "0" * 40)
    print(f"\nAt Ethereum block {head:,}")
    print(f"{len(claimed):,} wallets claimed UNI from the 2020 airdrop")
    print(f"{len(still):,} ({100 * len(still) / len(claimed):.1f}%) still hold UNI")
    print(f"{len(full):,} still hold at least 400 UNI")
    print(f"{holders:,} wallets hold UNI in total")
