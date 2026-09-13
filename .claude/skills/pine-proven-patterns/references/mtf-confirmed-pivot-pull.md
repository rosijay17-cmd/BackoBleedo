# MTF confirmed-pivot pull via `ta.valuewhen()` + `lookahead_on` + `[1]` offset

## Problem

Pulling `ta.pivothigh()` / `ta.pivotlow()` from a higher timeframe through
`request.security()`, then hand-tracking "latest vs previous confirmed pivot" in
the calling script with `var`-state that watches the forward-filled pulled series
for a change, does **not reliably produce a real value in practice** — even with
`lookahead = barmerge.lookahead_off` (the textbook "safe" setting) and months of
fully-loaded, non-Replay history on the chart.

This was confirmed empirically in this repo: a dedicated diagnostic
(`pivotHighUpdateCount` / `pivotLowUpdateCount`, incremented every time the
hand-tracked "latest pivot" var actually changed) read **0** across an entire
4H-history backtest of `delta_break_retest/Stage4_MTFBiasStack.pine`. Replay mode
was explicitly ruled out as the cause — the user retested on a normal (non-Replay)
chart with the same result.

## Proven solution

Don't hand-track pivot state in the calling script at all. Compute the "most
recent confirmed pivot" and "previous confirmed pivot" **natively, inside the
function that gets pulled**, using `ta.valuewhen(condition, source, occurrence)`:

```pine
f_context() =>
    float ph = ta.pivothigh(highSourceLen, highSourceLen)
    float pl = ta.pivotlow(lowSourceLen, lowSourceLen)
    float latestHigh   = ta.valuewhen(not na(ph), ph, 0)
    float previousHigh = ta.valuewhen(not na(ph), ph, 1)
    float latestLow    = ta.valuewhen(not na(pl), pl, 0)
    float previousLow  = ta.valuewhen(not na(pl), pl, 1)
    [latestHigh, previousHigh, latestLow, previousLow, /* ...other signals... */]
```

Then pull the **whole function call** through `request.security()` with
`lookahead = barmerge.lookahead_on` (not `_off`) **plus** an explicit one-bar-back
offset applied to the entire function call before it's handed to
`request.security`:

```pine
[latestHigh, previousHigh, latestLow, previousLow, ...] = request.security(
     syminfo.tickerid,
     higherTimeframeInput,
     f_context()[1],
     gaps = barmerge.gaps_off,
     lookahead = barmerge.lookahead_on
     )
```

The `[1]` applied to `f_context()` — not to the individual return values — is
what makes `lookahead_on` safe here: it forces the security call to always read
the higher-timeframe function's value as of the *previous* completed higher-TF
bar, which combined with `ta.valuewhen`'s own internal confirmation lag gives a
value that is both non-repainting and actually populated on every bar once at
least one pivot has occurred, instead of staying `na` indefinitely.

## Source

`MTF_Second_Flip_Continuation_v1_2.pine`, function `f_structureBias()` (~line
390) and its `request.security()` call (~lines 505-506).

## Applied in this repo

`delta_break_retest/Stage4_MTFBiasStack.pine` — `f_get4hContext()` was rewritten
to this pattern (commit `cb53155`), replacing the previous hand-rolled
`var lastPivotHigh` / `prevPivotHigh` tracking block, which was deleted along
with its now-meaningless `pivotHighUpdateCount` diagnostic. The same
`lookahead_on` + `[1]`-offset call shape was also applied to the 1H trend
context pull (`f_get1hContext()`) in the same file for consistency, even though
that function doesn't use pivots — the offset pattern is the safe default for
any `request.security()` call wrapping a function with its own internal
confirmation/lag logic.

**Not yet independently re-confirmed by the user on a live chart** as of the fix
— pushed but the "4H Pivots Ready" dashboard reading has not been re-screenshotted
since. Next time this file is touched, check whether that confirmation happened;
if not, it's worth asking.

## When to use this pattern

Any time a higher-timeframe value is pulled through `request.security()` where
the source function has its OWN internal confirmation delay (pivots being the
classic case — a pivot at bar N isn't known until `rightBars` bars later, but
other "confirmed on a delay" constructs qualify too). Plain hand-rolled
`var`-state change-tracking against a `lookahead_off` pull is not a reliable
substitute for `ta.valuewhen()` computed natively inside the pulled function.
