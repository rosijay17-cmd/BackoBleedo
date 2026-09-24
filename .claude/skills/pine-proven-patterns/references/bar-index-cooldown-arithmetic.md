# Bar-index-arithmetic cooldown (reset on ENTRY, not exit)

## Problem

Cooldowns implemented as a decrementing countdown variable (`cooldownBarsLeft -=
1` each bar, reset to N on a trigger) are fragile in Pine: they're easy to
desync across `barstate.isconfirmed` vs. intrabar updates, easy to double-decrement
or skip a decrement on session boundaries, and hard to reason about when multiple
independent cooldown timers exist (per-direction, per-signal-type, etc.).

Separately: a cooldown that resets on **exit** (waiting for
`strategy.closedtrades` to increment, or for `strategy.position_size` to return to
0) silently does nothing if trades aren't actually closing the way the script
expects — the exact failure mode diagnosed at length in
`Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine` this session, where
`strategy.position_size` never left 0 across an entire backtest and so no
exit-based cooldown could ever arm in the first place. An entry-based reset
doesn't have this dependency.

## Proven solution

No countdown variable at all. Store only the bar index of the last accepted
signal, and compute "still in cooldown" via plain bar-index subtraction, read
fresh every bar:

```pine
var int lastAcceptedSignalBar = na

int barsSinceLastSignal =
     na(lastAcceptedSignalBar)
         ? 1000000                      // effectively "never" — always clears cooldown
         : bar_index - lastAcceptedSignalBar

bool cooldownActive =
     useCooldownInput and
     cooldownBarsInput > 0 and
     not na(lastAcceptedSignalBar) and
     barsSinceLastSignal < cooldownBarsInput

bool cooldownOK = not cooldownActive
```

Cooldown timer state is written **once, immediately, at the moment a signal is
accepted** — not on exit, not on a delay:

```pine
if longSignalAccepted or shortSignalAccepted
    lastAcceptedSignalBar := bar_index   // start cooldown IMMEDIATELY
```

`cooldownBarsLeft` (for display only, never for logic) is derived the same way,
never stored:

```pine
int cooldownBarsLeft =
     not useCooldownInput or cooldownBarsInput == 0 or na(lastAcceptedSignalBar)
         ? 0
         : math.max(cooldownBarsInput - barsSinceLastSignal, 0)
```

## Source

`Trend_Following_Strategy_v6_Signal_Cooldown_FIX.pine`, section "05 — COOLDOWN"
(~lines 394-433). The file's own header comment explicitly documents the bug this
fixes: *"The old version waited for strategy.closedtrades. That is why the
dashboard stayed BARS LEFT = n/a while entry signals continued."* — i.e. this is
the same failure class as the P0 script's exit-detection bug, already diagnosed
and fixed once in this repo before this session's debugging even started. This
was the file the user pointed to as "glue" for the P0 cooldown bug.

## Applied in this repo

`delta_break_retest/Stage3_CooldownModule.pine` — `CooldownState` type stores
`lastExitBarIndex`, `lastLongLossBar`, `lastShortLossBar` etc. as plain bar
indices (not countdowns); `f_canTrade()` is a pure query function that computes
"in cooldown" via bar-index subtraction against `bar_index` at read time, never
via a stored/decremented counter. State mutation (`f_recordExit()`) is gated by
`barstate.isconfirmed` per the build spec's cooldown module rules. Passed 11/11
of the module's standalone synthetic test harness.

Also generalizes to **per-signal-type, independent cooldown timers** — see the
`Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine` fix this session, which replaced
two shared timers (`lastLongExitBar` / `lastShortExitBar`) with four independent
ones (`lastAcceptanceLongExitBar`, `lastAcceptanceShortExitBar`,
`lastRejectionLongExitBar`, `lastRejectionShortExitBar`) using this exact
bar-index-subtraction shape for each.

## When to use this pattern

Any cooldown, lockout, or "don't re-trigger for N bars" logic. Never use a
decrementing variable for this in Pine. If the cooldown is meant to represent
"time since last trade closed" specifically (not last signal), still store the
bar index and subtract — just make sure the bar index actually gets written
reliably (see `references/broker-verified-exit-detection.md` for how to detect a
real exit rather than inferring one from `strategy.position_size`).
