# Coinbase stock tokens on Base: who moves them while Wall Street is closed, with Envio HyperSync.
# Python 3.9+ standard library only. Set ENVIO_API_TOKEN first.
# Usage: python3 script.py            the last 10 days
#        python3 script.py DAYS       another window
import collections
import datetime
import json
import os
import re
import sys
import time
import urllib.request
from multiprocessing import Pool
from zoneinfo import ZoneInfo

TOKEN = os.environ.get("ENVIO_API_TOKEN")
if not TOKEN:
    sys.exit("Set ENVIO_API_TOKEN (get one at https://envio.dev/app/api-tokens)")

URL = "https://base.hypersync.xyz"
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
LIST = "https://docs.base.org/base-chain/specs/reference/b20/tokenized-stocks-on-base"  # Base's list of stock token addresses
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 40
NEW_YORK = ZoneInfo("America/New_York")
BLOCKS_PER_DAY = 432_000  # Base makes a block every 0.2 seconds


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


def stock_tokens():
    """Every Coinbase stock token address on Base's docs page (they all start 0xb2000000)."""
    page = urllib.request.urlopen(LIST, timeout=60).read().decode("utf-8", "ignore")
    return sorted({a.lower() for a in re.findall(r"0x[0-9a-fA-F]{40}", page) if a.lower().startswith("0xb2000000")})


TOKENS = None


def init(tokens):
    global TOKENS
    TOKENS = tokens


def pull(bounds):
    lo, hi = bounds
    out = []
    cursor = lo
    while cursor < hi:
        res = post("/query", {"from_block": cursor, "to_block": hi, "logs": [{"address": TOKENS, "topics": [[TRANSFER]]}],
                              "field_selection": {"log": ["topic1", "topic2", "block_number"], "block": ["number", "timestamp"]}})
        stamp = {}
        for chunk in res["data"]:
            for b in chunk.get("blocks", []):
                stamp[num(b["number"])] = num(b["timestamp"])
            for log in chunk.get("logs", []):
                out.append((stamp[num(log["block_number"])], "0x" + log["topic1"][-40:], "0x" + log["topic2"][-40:]))
        if res["next_block"] <= cursor:
            break
        cursor = res["next_block"]
    return out


def market_closed(ts):
    """Outside NYSE regular hours, 9:30 to 16:00 New York time, Monday to Friday."""
    t = datetime.datetime.fromtimestamp(ts, NEW_YORK)
    if t.weekday() >= 5:
        return True
    minute = t.hour * 60 + t.minute
    return not (570 <= minute < 960)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) == 2 else 10
    tokens = stock_tokens()
    head = post("/height")["height"]
    start = head - days * BLOCKS_PER_DAY
    ranges = [(b, min(b + 500_000, head)) for b in range(start, head, 500_000)]
    transfers = []
    with Pool(8, initializer=init, initargs=(tokens,)) as pool:
        for part in pool.imap_unordered(pull, ranges):
            transfers += part
    senders = collections.defaultdict(lambda: [0, 0])  # [moves while open, moves while closed]
    for ts, sender, to in transfers:
        if sender == ZERO or to == ZERO:
            continue  # mints and burns
        senders[sender][1 if market_closed(ts) else 0] += 1
    total = len(senders)
    any_closed = sum(1 for v in senders.values() if v[1])
    only_closed = sum(1 for v in senders.values() if v[1] and not v[0])
    print(f"{len(tokens)} stock tokens, last {days} days, {len(transfers):,} transfers")
    print(f"{total:,} wallets moved a stock token")
    print(f"{any_closed:,} ({100 * any_closed / total:.1f}%) moved one while Wall Street was closed")
    print(f"{only_closed:,} only ever moved them while it was closed")
