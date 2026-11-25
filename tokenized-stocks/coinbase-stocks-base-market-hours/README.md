# How to find who trades Coinbase stock tokens on Base while Wall Street is closed, with HyperSync

This example pulls every transfer of the 415 Coinbase stock tokens listed in Base's docs and checks when each wallet moves them, against New York Stock Exchange hours. **Over the 10 days to 25 Nov 2026, 13,305 wallets moved a Coinbase stock token on Base. 11,236 of them (84.4%) moved one at least once while Wall Street was closed, and 7,717 only ever moved them while it was closed.**

## Why it's interesting

A stock on an exchange trades from 9:30 to 16:00 New York time on weekdays. A stock token on Base moves whenever its holder wants. Splitting every move by the exchange's hours shows how much of the activity happens in the hours the market is shut, from one query over the chain.

## What it pulls

- The 415 stock token addresses from Base's docs page (they are B20 tokens and all start with `0xb2000000`).
- Every `Transfer` event of those tokens over the window, with the block timestamp, from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview).
- For each sending wallet, how many moves happened during NYSE regular hours (9:30 to 16:00 New York time, Monday to Friday) and how many outside them. Mints and burns are left out.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py            # the last 10 days
python3 script.py 30         # the last 30 days
```

## Change the window or chain

Pass the number of days. Base makes a block every 0.2 seconds, so a day is 432,000 blocks (`BLOCKS_PER_DAY`). For another chain, change `URL`, the token list and `BLOCKS_PER_DAY`. US market holidays are treated as open days, so add them to `market_closed` if your window covers one.

## Check the numbers

Over Base blocks 62,162,907 to 62,164,906, a public RPC (`eth_getLogs` on one stock token) returned 431 transfers, and HyperSync returned the same 431.

## Build your own with an AI agent

Paste this into Claude Code or Cursor:

```
Adapt script.py in this folder to also count how many wallets hold each stock token right now (sum every transfer in and out per wallet), and print the 20 tokens with the most holders. Keep it standard library only and read ENVIO_API_TOKEN from the environment.
```

## Links

- [HyperSync docs](https://docs.envio.dev/docs/HyperSync/overview)
- [Tokenized stocks on Base, token list](https://docs.base.org/base-chain/specs/reference/b20/tokenized-stocks-on-base)
- [Tokenized stocks on Base, overview](https://docs.base.org/base-chain/asset-issuance/tokenized-stocks-on-base)
- [Envio Discord](https://discord.gg/envio)
