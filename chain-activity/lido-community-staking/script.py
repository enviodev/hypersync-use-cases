# Lido community staking: count the operators and validators of the Community Staking Module month by month, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 script.py
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

TOKEN = os.environ.get("ENVIO_API_TOKEN")
if not TOKEN:
    sys.exit("Set ENVIO_API_TOKEN (get one at https://envio.dev/app/api-tokens)")

URL = "https://eth.hypersync.xyz"
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
MODULES = [  # Lido's community staking modules, as listed by the Staking Router
    "0xdA7dE2ECdDfccC6c3AF10108Db212ACBBf9EA83F",  # Community Staking
    "0x792cd25e4ae3578375031fb55e048e163a804f7b",  # Community Staking 0x02
]
DEPOSITED = "0x24eb1c9e765ba41accf9437300ea91ece5ed3f897ec3cdee0e9debd7fe309b78"  # DepositedSigningKeysCountChanged(uint256,uint256)
EXITED = "0x0f67960648751434ae86bf350db61194f387fda387e7f568b0ccd0ae0c220166"  # ExitedSigningKeysCountChanged(uint256,uint256)
START_BLOCK = 21_000_000


def post(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(URL + path, data, HEADERS)
    for attempt in range(8):
        try:
            return json.load(urllib.request.urlopen(req, timeout=180))
        except Exception:  # rate limits and timeouts: wait and try again
            time.sleep(3 * (attempt + 1))
    sys.exit("HyperSync kept failing")


def num(v):
    return v if isinstance(v, int) else int(v, 16)


head = json.load(urllib.request.urlopen(urllib.request.Request(URL + "/height", headers=HEADERS), timeout=30))["height"]

events = []  # (block, log index, topic0, (module, operator id), count, timestamp)
cursor = START_BLOCK
while cursor < head:
    res = post("/query", {
        "from_block": cursor,
        "to_block": head,
        "logs": [{"address": MODULES, "topics": [[DEPOSITED, EXITED]]}],
        "field_selection": {
            "log": ["address", "block_number", "log_index", "topic0", "topic1", "data"],
            "block": ["number", "timestamp"],
        },
    })
    for chunk in res["data"]:
        stamp = {num(b["number"]): num(b["timestamp"]) for b in chunk.get("blocks", [])}
        for log in chunk.get("logs", []):
            block = num(log["block_number"])
            events.append((block, num(log["log_index"]), log["topic0"], (log["address"].lower(), log["topic1"]), int(log["data"][:66], 16), stamp.get(block)))
    if res["next_block"] <= cursor:
        break
    cursor = res["next_block"]

events.sort(key=lambda e: (e[0], e[1]))
deposited, exited = {}, {}  # latest count per operator
snapshots = {}  # month -> (deposited, exited, operators with active validators)
for block, _, topic0, operator, count, ts in events:
    (deposited if topic0 == DEPOSITED else exited)[operator] = count
    if ts is None:
        continue
    month = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m")
    active_ops = sum(1 for op, d in deposited.items() if d - exited.get(op, 0) > 0)
    snapshots[month] = (sum(deposited.values()), sum(exited.values()), active_ops)

print(f"{'Month end':<10} {'Deposited':>10} {'Exited':>8} {'Active':>8} {'Operators with active validators':>34}")
for month in sorted(snapshots):
    d, e, ops = snapshots[month]
    print(f"{month:<10} {d:>10,} {e:>8,} {d - e:>8,} {ops:>34,}")

d, e = sum(deposited.values()), sum(exited.values())
ops = sum(1 for op, v in deposited.items() if v - exited.get(op, 0) > 0)
print()
print(f"Up to block {head:,}: {d:,} validators deposited, {e:,} exited, {d - e:,} active, run by {ops:,} operators")
sizes = sorted(v - exited.get(op, 0) for op, v in deposited.items() if v - exited.get(op, 0) > 0)
print(f"Median operator: {sizes[len(sizes) // 2]:,} active validators. Operators running exactly one: {sizes.count(1):,}")
