# How to count every transaction on Monad with HyperSync

This example counts Monad's first year of mainnet, from the block at the 14:00:00 UTC launch time on 24 Nov 2025 (block 37,700,069) to block 125,021,856, the last block before the one-year mark. **It found 1,225,783,292 transactions from 4,483,033 sending addresses across 87,321,788 blocks.** The launch block alone carried 47 transactions from 38 addresses.

The busiest stretch came at the end. The last two weeks (blocks 120,700,069 to 124,700,068, 9 to 23 Nov 2026) carried 130,386,432 transactions over 14.1 days, about 9.24M a day. The first million blocks after launch carried 18,000,687 over 4.65 days, about 3.87M a day, so the last two weeks ran at 2.4 times the launch pace. No earlier million blocks came close (the next highest is 25,602,921).

Zooming out ten times at a time from the launch block:

| Blocks | Time after launch | Transactions | Sending addresses |
| --- | --- | --- | --- |
| 1 | at launch | 47 | 38 |
| 1,000 | 6 min 41 s | 42,961 | 8,730 |
| 10,000 | 1 h 7 min | 405,536 | 38,635 |
| 100,000 | 11 h 11 min | 3,187,974 | 132,751 |
| 1,000,000 | 4 d 15 h | 18,000,687 | 459,164 |
| 10,000,000 | 46 d 12 h | 92,487,520 | 2,015,163 |
| 87,321,788 (the first year) | 1 year | 1,225,783,292 | 4,483,033 |

## Apps by wallets (`apps.py`)

The distinct wallets that sent a transaction to each app's main contracts in the first year. Contract names come from Monad's protocol registry ([monad-crypto/protocols](https://github.com/monad-crypto/protocols)) and the Monad dApp list. One router with 152,782 wallets has no public name, so it is listed as unnamed.

| App | Wallets in the first year |
| --- | --- |
| Nad.fun | 2,427,905 |
| Unnamed router | 152,782 |
| Uniswap | 142,725 |
| Matcha | 140,455 |
| FastLane (shMonad) | 127,240 |
| Pinot Finance | 109,564 |
| Lumiterra | 85,704 |
| PancakeSwap | 84,487 |
| GMGN | 57,619 |
| LI.FI | 47,117 |
| OpenSea | 45,975 |

Nad.fun had more than twice the wallets of the next ten apps combined (993,668), and 54% of all 4,483,033 sending addresses in the first year used it. Tokens (USDC, WMON, meme tokens) and plain deposit addresses are not apps, so they are left out.

```
python3 apps.py                    # the first year, 8 workers
python3 apps.py FROM TO            # a fixed block range
```

To count your own app, add its name and contract addresses to the `APPS` dict at the top of `apps.py` and run it again.

## Why it's interesting

Every transaction on a chain, and the address that sent it, is one HyperSync query over a block range. The same script counts a year on any chain if you swap the endpoint and the starting block, and you can pick the range, so the launch block, the first hour or the whole year are all the same code.

## What it pulls

- Every transaction in the range from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview), with only the `from` field selected so the response stays small.
- One million blocks at a time, so the pull can be stopped and the totals are printed shard by shard.
- A set of the first 8 bytes of each sending address, which keeps memory small (the chance of two different addresses sharing a prefix is below one in a million).

## Check it

We compared the HyperSync counts with Monad's public RPC (`rpc.monad.xyz`) block by block. The first 1,000 blocks (42,961 transactions), the first 10,000 blocks (405,536) and two 1,000-block windows (blocks 50,000,000 to 50,001,000 with 8,547 transactions, and blocks 110,000,000 to 110,001,000 with 16,699) all matched exactly. Any of them is a quick run:

```
python3 script.py 37700069 37701069
```

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py                  # Monad's first year
python3 script.py FROM TO          # a fixed block range
```

The full first year is a large download, so start with a small range to see it work.

## Sample output

```
blocks  50,000,000 to  50,001,000:        8,547 transactions   running total          8,547

Blocks 50,000,000 to 50,001,000 (1,000 blocks)
8,547 transactions from 692 sending addresses
```
