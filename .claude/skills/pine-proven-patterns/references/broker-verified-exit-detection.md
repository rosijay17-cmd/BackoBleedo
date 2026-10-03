# Broker-verified exit detection via `strategy.closedtrades`

## Problem

Detecting a trade exit by watching for `strategy.position_size` to transition
(e.g. from nonzero back to 0, or a sign flip) is an *inference* — it assumes the
script's own understanding of "am I in a trade" always matches the broker's. When
it doesn't (a bug elsewhere in the entry/state logic, an unexpected `strategy.close`
call, pyramiding interactions, etc.), the inference silently breaks and anything
built on it — exit logging, cooldown arming, alerts — goes dead without an
obvious symptom. This was the actual root cause diagnosed at length in
`Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine` this session: `strategy.position_size`
never left `0` across an entire backtest, so every downstream consumer that
inferred exits from it (cooldown timers included) never fired, even though the
surface symptom looked like "the cooldown isn't working."

## Proven solution

Read exits directly from Pine's own broker-side trade history instead of
inferring them, using `strategy.closedtrades` (a count) plus the per-trade
accessor functions `strategy.closedtrades.entry_id()`,
`strategy.closedtrades.exit_bar_index()`, and `strategy.closedtrades.profit()`.
Track how many closed trades have already been processed so each new one is
handled exactly once:

```pine
var int processedClosedTrades = 0

bool closedTradeThisUpdate = strategy.closedtrades > processedClosedTrades

if closedTradeThisUpdate
    int closedTradeNumber = strategy.closedtrades - 1     // most recent index
    string closedEntryId = strategy.closedtrades.entry_id(closedTradeNumber)
    int closedExitBar    = strategy.closedtrades.exit_bar_index(closedTradeNumber)
    float closedProfit   = strategy.closedtrades.profit(closedTradeNumber)

    if closedEntryId == "Acceptance Long"
        lastAcceptanceLongExitBar := closedExitBar
        acceptanceLongCooldownArmed := false
        acceptanceLongClosedNow := true
    // ...mirrored per entry_id for every distinct signal type...

    processedClosedTrades := strategy.closedtrades
```

Because this reads directly from the broker's own trade ledger, it can never
disagree with "did a trade actually close" — unlike inferring from
`strategy.position_size`, which only tells you the CURRENT net position, not
whether a specific tagged entry closed.

`strategy.opentrades` / `strategy.closedtrades` (the plain counts, not the
per-trade accessors) are also useful as an independent cross-check layer in a
dashboard — display them alongside any custom position-tracking state so a
divergence between "what the script thinks" and "what the broker recorded" is
visible at a glance rather than requiring a full diagnostic chain to discover, as
happened this session.

## Source

Pattern appears (with minor variations) in `Ranger_V2_POC_State_Delta_Session_Profiles.pine`,
`Ranger_V2_1_POC_State_LTF_Delta_Session_Profiles.pine`,
`Ranger_V2_2_Clean_POC_State_Delta_Profiles.pine`, and
`P0_Rebuild_Stage0_SanityCheck.pine` — this is an established idiom across
several of this repo's own strategies, not a one-off.

## Applied in this repo

`Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine` — the user supplied this exact
pattern directly to replace the script's previous `strategy.position_size`-based
exit detection. Integrated with `closedEntryIdThisUpdate` / `closedExitBarThisUpdate`
variables and four entry-id branches (Acceptance Long/Short, Rejection
Long/Short), each writing its own independent `last*ExitBar` cooldown timer (see
`references/bar-index-cooldown-arithmetic.md`) and a `*ClosedNow` flag consumed
by the exit log, exit label, and alertconditions.

## When to use this pattern

Any time downstream logic (cooldown arming, exit logging, per-signal-type
statistics, alerts) needs to know **that a specific tagged entry closed**, not
just "the net position changed." Always prefer this over inferring exits from
`strategy.position_size` transitions when multiple distinct entry types/IDs are
in play, or when exit-triggered state (cooldowns, counters) has ever been
observed to silently stop updating — that symptom is the signature of this
inference breaking, and checking `strategy.opentrades`/`strategy.closedtrades`
directly is the fastest way to confirm or rule it out.
