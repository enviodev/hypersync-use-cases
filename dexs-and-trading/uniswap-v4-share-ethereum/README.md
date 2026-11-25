# How to count every Uniswap v2, v3 and v4 swap on Ethereum with HyperSync

This example counts every swap on Uniswap v2, v3 and v4 on Ethereum, month by month, from the block v4 launched (21,688,329) to 24 Nov 2026. **Uniswap v4 handled 47.0% of all Uniswap swaps on Ethereum from 1 to 24 Nov 2026, its highest month so far. In its first full month, Feb 2025, it was 4.1%. It has handled more swaps than v3 every day from 31 Oct to 24 Nov 2026, 25 days in a row.**

| Month | v4 swaps | v3 swaps | v2 swaps | v4 share |
| --- | --- | --- | --- | --- |
| 2025-01 | 663 | 833,354 | 922,363 | 0.0% |
| 2025-02 | 271,922 | 3,440,837 | 2,997,342 | 4.1% |
| 2025-03 | 408,070 | 3,459,048 | 2,972,247 | 6.0% |
| 2025-04 | 458,541 | 3,484,789 | 3,157,063 | 6.5% |
| 2025-05 | 530,772 | 3,215,678 | 5,119,939 | 6.0% |
| 2025-06 | 621,125 | 2,910,318 | 4,729,359 | 7.5% |
| 2025-07 | 827,495 | 3,542,749 | 4,793,159 | 9.0% |
| 2025-08 | 1,312,607 | 3,662,113 | 4,816,614 | 13.4% |
| 2025-09 | 1,428,024 | 3,181,034 | 3,589,398 | 17.4% |
| 2025-10 | 1,933,313 | 3,731,751 | 2,821,441 | 22.8% |
| 2025-11 | 1,729,423 | 4,099,141 | 2,428,772 | 20.9% |
| 2025-12 | 1,776,736 | 3,592,191 | 2,782,832 | 21.8% |
| 2026-01 | 2,194,434 | 3,613,076 | 3,124,866 | 24.6% |
| 2026-02 | 2,550,168 | 3,915,179 | 2,344,281 | 28.9% |
| 2026-03 | 2,536,004 | 3,652,893 | 2,317,463 | 29.8% |
| 2026-04 | 2,880,213 | 3,217,456 | 3,738,381 | 29.3% |
| 2026-05 | 4,222,119 | 3,161,783 | 2,963,679 | 40.8% |
| 2026-06 | 3,324,301 | 3,406,526 | 2,086,253 | 37.7% |
| 2026-07 | 3,254,949 | 3,107,672 | 1,802,349 | 39.9% |
| 2026-08 | 3,403,459 | 3,549,170 | 1,570,099 | 39.9% |
| 2026-09 | 3,731,479 | 4,121,099 | 1,615,715 | 39.4% |
| 2026-10 | 4,433,982 | 3,988,412 | 1,512,227 | 44.6% |
| 2026-11 | 3,291,954 | 2,701,643 | 1,005,649 | 47.0% |

Jan 2025 starts at the v4 launch block, and Nov 2026 runs to 24 Nov.

## Why it's interesting

v4 moved every pool into one contract, the PoolManager, and added hooks, so a pool can run its own code on every swap. Watching its share of swaps grow month by month shows how fast traders and routers have moved over, without waiting for anyone's dashboard.

## What it pulls

- Every pool the Uniswap v3 factory created and every pair the v2 factory created, from their `PoolCreated` and `PairCreated` events, with [HyperSync](https://docs.envio.dev/docs/HyperSync/overview).
- Every `Swap` event on the v4 PoolManager, on those v3 pools and on those v2 pairs. Forks and other DEXs that reuse the same event are left out, because only Uniswap's own pools count.
- Counts by UTC month for each version, using the block timestamp.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py                    # from v4's launch to now, 8 workers
python3 script.py FROM TO            # a fixed block range
```

The first step lists every v3 pool and v2 pair from the two factories, which takes a few minutes. The full run from v4's launch takes about an hour.

## Change the window or chain

Pass a block range to count any stretch. For another chain, change `URL` to that chain's HyperSync endpoint and the four addresses to the ones in Uniswap's deployment docs for that chain.

## Check the numbers

Over Ethereum blocks 26,491,793 to 26,492,292, a public RPC (`eth_getLogs`) returned 8,957 v4 swaps on the PoolManager and 777 swaps on the two biggest v3 pools (USDC/WETH and WETH/USDT, 0.05%). HyperSync returned the same 8,957 and 777.

## Build your own with an AI agent

Paste this into Claude Code or Cursor:

```
Adapt script.py in this folder to count Uniswap v4 swaps per pool instead of per month, and list the 20 v4 pools with the most swaps in the last 30 days, with their poolId. Keep it standard library only and read ENVIO_API_TOKEN from the environment.
```


## Links

- [HyperSync docs](https://docs.envio.dev/docs/HyperSync/overview)
- [Uniswap v4 deployments](https://docs.uniswap.org/contracts/v4/deployments)
- [Uniswap v3 deployments](https://docs.uniswap.org/contracts/v3/reference/deployments/ethereum-deployments)
- [Uniswap v2 deployments](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/v2-deployments)
- [Envio Discord](https://discord.gg/envio)
