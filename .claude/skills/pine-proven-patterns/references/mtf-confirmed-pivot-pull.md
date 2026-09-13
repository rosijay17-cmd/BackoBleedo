# MTF confirmed-pivot pull via `ta.valuewhen()` + `lookahead_on` + `[1]` offset

> **CORRECTION (2026-09-13, same day as original entry):** the "Proven solution"
> section below, as first written, was wrong in one detail and does not compile
> as shown — see "Correction: the `[1]` offset goes INSIDE the function for
> multi-value tuples" further down before copying this pattern. The core idea
> (`ta.valuewhen()` inside the pulled function, `lookahead_on`, one-bar-back
> offset) is still correct and still the fix; only WHERE the `[1]` gets applied
> was wrong for a function that returns more than one value.

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

The one-bar-back offset is what makes `lookahead_on` safe here: it forces the
security call to always read the higher-timeframe function's value as of the
*previous* completed higher-TF bar, which combined with `ta.valuewhen`'s own
internal confirmation lag gives a value that is both non-repainting and
actually populated on every bar once at least one pivot has occurred, instead
of staying `na` indefinitely.

## Correction: the `[1]` offset goes INSIDE the function for multi-value tuples

The code above (`f_context()[1]`, applying `[1]` to the whole function call)
is only valid when the pulled function returns a **single** value, e.g. an
`int` bias like `MTF_Second_Flip_Continuation_v1_2.pine`'s `f_structureBias()`
does. Pine's `[]` history-reference operator ("operator SQBR") only accepts a
single series argument — it cannot be applied to a tuple.

Applying it to a function that returns multiple values, as first written above
(4 or 7 return values), fails to compile with:

```
Cannot call "operator SQBR" with argument "expr0"=... An argument of
"[series float, series float, ...]" type was used but a "series na" is
expected. (CE10123)
```

This is exactly what happened porting the pattern into
`delta_break_retest/Stage4_MTFBiasStack.pine`, whose context functions return
7 values (4H) and 4 values (1H) — caught on-device in the TradingView mobile
Pine Editor, not in this skill's own code sample.

**The actual fix for a multi-value context function:** apply `[1]` to each
return value INDIVIDUALLY, on the function's own last line, still inside the
function (so it's still evaluated in the pulled higher-timeframe context) —
then pass the bare function call (no outer `[1]`) to `request.security`:

```pine
f_context() =>
    float ph = ta.pivothigh(highSourceLen, highSourceLen)
    float pl = ta.pivotlow(lowSourceLen, lowSourceLen)
    float latestHigh   = ta.valuewhen(not na(ph), ph, 0)
    float previousHigh = ta.valuewhen(not na(ph), ph, 1)
    float latestLow    = ta.valuewhen(not na(pl), pl, 0)
    float previousLow  = ta.valuewhen(not na(pl), pl, 1)
    // offset applied per-value HERE, not on the outer call:
    [latestHigh[1], previousHigh[1], latestLow[1], previousLow[1]]

[latestHigh, previousHigh, latestLow, previousLow] = request.security(
     syminfo.tickerid,
     higherTimeframeInput,
     f_context(),                       // no [1] out here -- it's baked in above
     gaps = barmerge.gaps_off,
     lookahead = barmerge.lookahead_on
     )
```

If the pulled function returns exactly one value, `f_context()[1]` (offset on
the outer call) is fine and slightly simpler — that's the
`f_structureBias()[1]` shape in the Source file below. Once a function grows a
second return value, switch to per-value `[1]` inside the function before
returning the tuple.

## Source

`MTF_Second_Flip_Continuation_v1_2.pine`, function `f_structureBias()` (~line
390) and its `request.security()` call (~lines 505-506).

## Applied in this repo

`delta_break_retest/Stage4_MTFBiasStack.pine` — `f_get4hContext()` was rewritten
to this pattern in two rounds:
- **Round 1** (commit `cb53155`): replaced the previous hand-rolled
  `var lastPivotHigh` / `prevPivotHigh` tracking block (and its now-meaningless
  `pivotHighUpdateCount` diagnostic) with `ta.valuewhen()` inside the function,
  but applied the `[1]` offset to the whole `f_get4hContext()` call — invalid,
  since the function returns 7 values (CE10123, caught in the TradingView
  mobile Pine Editor on next compile).
- **Round 2** (same day): moved the `[1]` offset to each of the 7 return values
  individually, on the function's own last line; `request.security()` now
  receives the bare `f_get4hContext()` call with no outer `[1]`. Same fix
  applied to `f_get1hContext()` (4 return values), which had the identical
  bug for the same reason.

**Still not independently re-confirmed by the user on a live chart** — round 2
has been written and locally validated (bracket balance, no unguarded loops,
single `indicator()` declaration) but not yet pushed/compiled on-device as of
this note. Next time this file is touched, check whether "4H Pivots Ready"
reads YES and update this note.

## When to use this pattern

Any time a higher-timeframe value is pulled through `request.security()` where
the source function has its OWN internal confirmation delay (pivots being the
classic case — a pivot at bar N isn't known until `rightBars` bars later, but
other "confirmed on a delay" constructs qualify too). Plain hand-rolled
`var`-state change-tracking against a `lookahead_off` pull is not a reliable
substitute for `ta.valuewhen()` computed natively inside the pulled function.
