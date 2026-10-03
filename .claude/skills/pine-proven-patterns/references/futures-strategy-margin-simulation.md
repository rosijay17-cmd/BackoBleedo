# Futures `strategy()` orders can silently never fill without explicit margin settings

## Problem

A `strategy()` script calls `strategy.entry()` correctly, on schedule, with
sane parameters — and the orders simply never become real trades. No compile
error, no runtime error, no warning. The only visible symptom is
`strategy.opentrades + strategy.closedtrades` staying at 0 forever, no matter
how many times `strategy.entry()` is called.

This is the exact same failure signature the old `Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine`
hit earlier in this repo's history (`strategy.position_size` never leaving 0
across an entire backtest) — except that saga never reached a root cause. This
time it did.

## Root cause

Pine's `strategy()` simulates its own internal account, and by default assumes
**100% margin** — meaning the *full notional value* of a position must be
covered by `initial_capital`, unless `margin_long`/`margin_short` are set
explicitly to a lower percentage. For a full-size index future, notional value
can be enormous relative to a typical `initial_capital`:

- E-mini Nasdaq (`NQ1!`), point value $20, price ~29,000 → notional ≈
  **$580,000 per contract**.
- A script declared with `initial_capital = 100000` (a completely reasonable-
  looking number) can't cover even a fraction of that under the default
  margin model, so every single order is silently rejected for insufficient
  equity.

## Proven fix (confirmed on-device, both parts were needed)

1. **Set `margin_long`/`margin_short` explicitly** in the `strategy()`
   declaration, as a rough percentage of notional value approximating the
   instrument's real margin requirement:

   ```pine
   strategy(title = "...", ..., initial_capital = 100000, margin_long = 3, margin_short = 3)
   ```

2. **Trade the instrument you'll actually trade, not just "a" liquid proxy.**
   In this repo's case, the user's real account trades Micro Nasdaq futures
   (`MNQ1!`, 1/10th the point value of `NQ1!`) through a prop firm, but the
   chart was set to the full-size `NQ1!` contract. Switching the chart symbol
   to `MNQ1!` — on top of the `margin_long`/`margin_short` fix — is what
   actually got fills to 1:1 match script-side entry calls
   (`Stage7_OrdersRisk.pine`, confirmed 17 `strategy.entry()` calls / 17 real
   broker-side trades). `margin_long = 3` alone, still on the full-size
   contract, was NOT enough by itself on-device — the exact reason isn't
   fully pinned down (Pine's margin math for a continuous full-size future
   may behave differently than a simple "3% of point-value × price"
   calculation suggests), but empirically, matching chart symbol to the
   actual traded instrument's size resolved it where the margin parameter
   alone did not.

## How this was diagnosed (reusable technique)

**Without needing Strategy Tester access at all** — the user's plan didn't
have it. Two dashboard-only diagnostics did the job:

1. A plain script-side counter (`entryCallCount`, incremented every time
   `strategy.entry()` is called) compared against the broker's own
   `strategy.opentrades + strategy.closedtrades` on the dashboard. A mismatch
   (script count higher) proves orders are being submitted but not becoming
   real trades — a more specific finding than "Position: FLAT" alone, and one
   that needs no Strategy Tester tab.
2. A completely unconditional **sanity order** — 1 contract, no bracket, no
   gating of any kind, fired every N bars whenever flat — isolated whether
   the problem was fundamental (nothing fills, ever) versus specific to the
   real signal's own entry parameters. In this case the sanity order was
   never actually needed to diverge from the real signal (both were broken
   the same way, by the same margin issue), but it's the right tool for
   telling those two failure modes aport when they're NOT the same cause.

## When to check this file

Before declaring ANY `strategy()` on a futures instrument in this repo,
especially a full-size (not micro) continuous contract. Set
`margin_long`/`margin_short` explicitly from the start rather than leaving
Pine's 100%-margin default in place, and double check the chart symbol
actually matches the instrument size you intend to trade — a proxy of the
"same market" at a different contract size is not a safe stand-in once
margin/fill mechanics are in play, even though it's usually fine for pure
price-action/indicator work (Stages 1-6 in this rebuild never cared, because
none of them ever submitted an order).
