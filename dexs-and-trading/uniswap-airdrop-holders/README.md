# How to find which wallets from the 2020 UNI airdrop still hold UNI, with HyperSync

This example replays every UNI transfer on Ethereum since the token launched, finds every wallet that claimed UNI from the September 2020 airdrop, and checks how many still hold it. **At Ethereum block 26,493,601 (25 Nov 2026), 252,390 wallets had claimed from the airdrop. 47,992 of them still hold UNI, and 33,570 hold at least the 400 UNI each past user received.**

## Why it's interesting

The UNI airdrop sent 400 UNI to every wallet that had used Uniswap before September 2020. Following those same wallets six years on shows who held through every cycle since, from the token's own transfers.

## What it pulls

- Every `Transfer` event of UNI (`0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984`) since it was deployed, from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview).
- Every wallet that received UNI from the airdrop contract, the MerkleDistributor at `0x090D4613473dEE047c3f2706764f49E0821D256e`.
- Each wallet's balance today, rebuilt from every transfer in and out.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py
```

It replays more than 10M transfers, so a full run takes about 15 minutes.

## Change the token

Swap `UNI`, `AIRDROP` and `UNI_DEPLOYED` for any token with a Merkle airdrop to see how many of its airdrop wallets still hold.

## Check the numbers

We read 65 random wallets' UNI balances with `balanceOf` over a public RPC. 25 that HyperSync shows still holding, 25 that it shows at zero and 15 that it shows at 400 UNI or more all matched.

## Build your own with an AI agent

Paste this into Claude Code or Cursor:

```
Adapt script.py in this folder to split the airdrop wallets that still hold UNI by how much they hold (under 400, 400 to 1,000, over 1,000) and print each group's size. Keep it standard library only and read ENVIO_API_TOKEN from the environment.
```

## Links

- [HyperSync docs](https://docs.envio.dev/docs/HyperSync/overview)
- [Uniswap governance and UNI](https://docs.uniswap.org/concepts/governance/overview)
- [Introducing UNI, Uniswap blog](https://blog.uniswap.org/uni)
- [Envio Discord](https://discord.gg/envio)
