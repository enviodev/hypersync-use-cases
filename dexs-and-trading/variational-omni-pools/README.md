# How to count every Variational Omni settlement pool on Arbitrum, with HyperSync

This example pulls every pool created by Variational's Omni Settlement Pool Factory on Arbitrum. On Omni, each user gets their own settlement pool contract with the OLP. **Between Arbitrum blocks 300,000,000 and 527,500,000 (30 Jan 2025 to 25 Nov 2026), the factory deployed 212,335 settlement pools for 212,330 unique user wallets. January 2026 was the busiest month, with 41,351 new users.**

## Why it's interesting

Most perp DEXs keep every trader's margin in one shared contract. Omni deploys a separate settlement pool per user, so every new trader shows up onchain as a new contract from one factory. Counting those creation events gives you a signup curve straight from the chain.

## What it pulls

- Every pool-created event (topic `0x0b33722ea9d97f05fb7128e0987e4060c182350308a3d0a19f8ec53512fe1493`) from the Settlement Pool Factory (`0x0F820B9afC270d658a9fD7D16B1Bdc45b70f074C`), from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview).
- The pool address (data word 1) and the user wallet (data word 4) from each event.
- Pools created per day and each wallet's first day.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py
```

A full run takes about 3 minutes. Pass a block number to stop at that block.

## Check the numbers

The official Arbitrum RPC returns exactly 212,335 pool-created events from the factory over the same block range with `eth_getLogs`.

## Build your own with an AI agent

Paste this into Claude Code or Cursor:

```
Adapt script.py in this folder to also pull USDC Transfer events into each settlement pool and print how many pools have ever been funded, by month. Keep it standard library only and read ENVIO_API_TOKEN from the environment.
```

## Links

- [HyperSync docs](https://docs.envio.dev/docs/HyperSync/overview)
- [Variational docs](https://docs.variational.io)
- [Envio Discord](https://discord.gg/envio)
