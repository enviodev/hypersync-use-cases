# Monad's first year: count every transaction and every sending address since the block at launch, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 script.py            Monad's first year, from the launch block up to the one-year mark (a full pull, one million blocks at a time)
#        python3 script.py FROM TO    a fixed block range
import json
import os
import sys
import time
import urllib.request

TOKEN = os.environ.get("ENVIO_API_TOKEN")
if not TOKEN:
    sys.exit("Set ENVIO_API_TOKEN (get one at https://envio.dev/app/api-tokens)")

URL = "https://monad.hypersync.xyz"
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
LAUNCH_BLOCK = 37_700_069  # the block at the announced mainnet launch time, timestamp 24 Nov 2025 14:00:00 UTC
ONE_YEAR_END = 125_021_857  # one past the last block before 24 Nov 2026 14:00:00 UTC
SHARD = 1_000_000


def post(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(URL + path, data, HEADERS)
    for attempt in range(8):
        try:
            return json.load(urllib.request.urlopen(req, timeout=300))
        except Exception:  # rate limits and timeouts: wait and try again
            time.sleep(3 * (attempt + 1))
    sys.exit("HyperSync kept failing")


if len(sys.argv) == 3:
    start, end = int(sys.argv[1]), int(sys.argv[2])
else:
    start, end = LAUNCH_BLOCK, ONE_YEAR_END

transactions = 0
senders = set()  # the first 8 bytes of each sending address, which keeps memory small (collision odds are below one in a million)
block = start
while block < end:
    shard_end = min(block + SHARD, end)
    shard_tx = 0
    cursor = block
    while cursor < shard_end:
        res = post("/query", {
            "from_block": cursor,
            "to_block": shard_end,
            "transactions": [{}],
            "field_selection": {"transaction": ["from"]},
        })
        for chunk in res["data"]:
            for tx in chunk.get("transactions", []):
                shard_tx += 1
                senders.add(int(tx["from"][2:18], 16))
        if res["next_block"] <= cursor:
            break
        cursor = res["next_block"]
    transactions += shard_tx
    print(f"blocks {block:>11,} to {shard_end:>11,}: {shard_tx:>12,} transactions   running total {transactions:>14,}", flush=True)
    block = shard_end

print()
print(f"Blocks {start:,} to {end:,} ({end - start:,} blocks)")
print(f"{transactions:,} transactions from {len(senders):,} sending addresses")
