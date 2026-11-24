# How to count Lido community staking operators and validators with HyperSync

This example counts the operators and validators of Lido's community staking on Ethereum, month by month, from the modules' own onchain events. It covers both community staking modules in Lido's Staking Router: Community Staking (`0xdA7dE2ECdDfccC6c3AF10108Db212ACBBf9EA83F`) and Community Staking 0x02 (`0x792cd25e4ae3578375031fb55e048e163a804f7b`). **It found 437 operators running 24,280 active validators (27,694 deposited, 3,414 exited), up from 395 operators and 11,414 active validators a year earlier. The median operator runs 12 validators, and 82 operators run exactly one.**

| Month end | Deposited | Exited | Active | Operators with active validators |
| --- | --- | --- | --- | --- |
| 2024-10 | 909 | 0 | 909 | 143 |
| 2025-03 | 6,007 | 150 | 5,857 | 312 |
| 2025-11 | 11,884 | 470 | 11,414 | 395 |
| 2026-03 | 21,604 | 1,066 | 20,538 | 392 |
| 2026-06 | 24,914 | 1,547 | 23,367 | 430 |
| 2026-09 | 27,256 | 1,988 | 25,268 | 431 |
| 2026-11 | 27,694 | 3,414 | 24,280 | 437 |

## Why it's interesting

Community staking is permissionless, so anyone can run Ethereum validators through it, and every operator's validator count is written to the chain as an event. Two events per operator are enough to rebuild the whole picture, and replaying them in block order gives the state at the end of any month.

## What it pulls

- Every `DepositedSigningKeysCountChanged` and `ExitedSigningKeysCountChanged` event from both modules, from [HyperSync](https://docs.envio.dev/docs/HyperSync/overview), with the block timestamp joined on.
- The latest deposited and exited count per operator (per module), replayed in block order.
- The size of each operator today: the median, and how many run exactly one validator.
- A snapshot at the end of each month: validators deposited, exited, active (deposited minus exited) and operators with at least one active validator.

## Check it

Each module's own `getStakingModuleSummary()` agrees with the HyperSync counts. Community Staking returns 3,414 exited and 27,661 deposited, and Community Staking 0x02 returns 0 exited and 33 deposited, 27,694 deposited in total. `getNodeOperatorSummary()` on Community Staking 0x02 gives 13 operators with active validators, matching too.

## Run it

You need Python 3.9 or newer (standard library only) and a free HyperSync API token from [envio.dev/app/api-tokens](https://envio.dev/app/api-tokens).

```
export ENVIO_API_TOKEN=your_token_here
python3 script.py
```

## Sample output

```
Month end   Deposited   Exited   Active   Operators with active validators
2025-11        11,884      470   11,414                                395
2026-11        27,694    3,414   24,280                                437

Up to block 26,487,455: 27,694 validators deposited, 3,414 exited, 24,280 active, run by 437 operators
Median operator: 12 active validators. Operators running exactly one: 82
```
