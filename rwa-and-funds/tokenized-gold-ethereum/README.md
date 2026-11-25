# How to track tokenized gold on Ethereum (PAXG and XAUT), with HyperSync

This example pulls every PAXG and XAUT transfer on Ethereum, rebuilds every balance from zero and compares today with one and two years ago. **At Ethereum block 26,493,718 (25 Nov 2026), PAXG and XAUT add up to 1,270,328 oz, which is 39.5 tonnes of gold, up from 13.8 tonnes two years earlier. 146,215 wallets hold at least one of them, against 76,330 a year earlier.**

| | 25 Nov 2024 | 25 Nov 2025 | 25 Nov 2026 |
| --- | --- | --- | --- |
| PAXG oz / holders | 197,564 / 34,676 | 333,757 / 62,758 | 442,911 / 87,854 |
| XAUT oz / holders | 246,524 / 2,987 | 522,089 / 15,837 | 827,418 / 63,898 |
| Gold onchain | 13.8 tonnes | 26.6 tonnes | 39.5 tonnes |
| Unique wallets | 37,260 | 76,330 | 146,215 |

## Why it's interesting

Each PAXG and XAUT token is one troy ounce of allocated gold. Rebuilding balances from every transfer shows how much gold has moved onchain and how many wallets hold it, at any point in time, from the tokens' own events.

## What it pulls

- Every `Transfer` event of Paxos Gold, PAXG (`0x45804880De22913dAFE09f4980848ECE6EcbAf78`), and Tether Gold, XAUT (`0x68749665FF8D2d112Fa859AA293F07A622782F38`), from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview).
- Every holder's balance today, a year ago and two years ago.
- Ounces converted to tonnes at 31.1034768 grams per troy ounce.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py
```

It replays nearly 10M transfers with 4 worker processes, so a full run takes about 10 minutes. Pass a block number to stop at that block.

## Change the token or dates

Add any token to `TOKENS` with its address, decimals and a block before it was deployed. Edit `CUTOFFS` to compare other dates.

## Check the numbers

Rebuilt supply matches `totalSupply()` read over a public RPC: 442,910.644131 PAXG and 827,417.63 XAUT. The XAUT figure also matches Tether Gold's attested ounces.

## Build your own with an AI agent

Paste this into Claude Code or Cursor:

```
Adapt script.py in this folder to print PAXG and XAUT holders bucketed by size (under 0.01 oz, 0.01 to 1 oz, 1 to 10 oz, over 10 oz) for each date. Keep it standard library only and read ENVIO_API_TOKEN from the environment.
```

## Links

- [HyperSync docs](https://docs.envio.dev/docs/HyperSync/overview)
- [Paxos Gold](https://www.paxos.com/pax-gold)
- [Tether Gold](https://gold.tether.to)
- [Envio Discord](https://discord.gg/envio)
