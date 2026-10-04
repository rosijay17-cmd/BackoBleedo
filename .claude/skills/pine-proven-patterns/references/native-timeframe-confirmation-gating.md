# Native-timeframe signal detectors need explicit `barstate.isconfirmed` gating before driving orders

## Problem

A signal detector that computes everything directly on the chart's own
execution timeframe — no `request.security()` pull, no higher-timeframe
context — looks "safer" than an MTF signal in one respect (no `[1]`-offset
confirmation dance needed, since there's no cross-timeframe lag to account
for). But if the detector was originally written as a pure `indicator()` and
is then reused inside a `strategy()` to drive real `strategy.entry()` calls,
it can carry a latent bug that never mattered in its original form: its own
internal state (accumulators, regime flags, level trackers) updates on
**every tick**, including intrabar ticks on a still-forming, not-yet-closed
bar.

For a plot, that's cosmetically fine — the line/marker just repaints until
the bar closes, same as any real-time indicator. For a strategy, it's a real
correctness problem: if the detector's own "event fired" condition can
resolve to true on a still-forming bar, and firing that event also **resets**
some of the detector's internal state (a common design, since most
change-point/breakout detectors zero their own accumulators once they
declare a change), then a single volatile intrabar tick sequence could:

1. Trip the event condition on an incomplete bar.
2. Reset the accumulators the same tick.
3. Have price tick back the other way before the bar actually closes.
4. Trip the (reset) accumulators into declaring **another** event before the
   bar even finishes forming.

None of this is visible in a plain visual indicator's history (which only
draws confirmed values by the time you look at it), but it is exactly the
kind of repeated, spurious "event" a strategy's entry logic would act on in
real time, well before Pine's history ever reflects it as a problem.

## Proven fix

Gate the detector's own state **mutation** — not just the final trading
decision — behind `barstate.isconfirmed`, so the accumulators, flags, and
levels only ever update once per fully-closed bar:

```pine
var float sPos = 0.0
var float sNeg = 0.0
var int trend = 0

bool changeUp = false
bool changeDn = false

if barstate.isconfirmed
    if not na(zScore)
        sPos := math.max(0, sPos + zScore - slackInput)
        sNeg := math.min(0, sNeg + zScore + slackInput)

    changeUp := sPos > thresholdInput
    changeDn := sNeg < -thresholdInput

bool isChange = changeUp or changeDn

var float regimePrice = na
var int regimeStartBar = bar_index

if barstate.isconfirmed and (isChange or bar_index == lengthInput)
    trend := changeUp ? 1 : (changeDn ? -1 : trend)
    regimePrice := src
    regimeStartBar := bar_index
    sPos := 0.0
    sNeg := 0.0
```

`changeUp`/`changeDn` are declared fresh (not `var`) each bar and default to
`false`, so on every intrabar tick before the bar closes they simply stay
`false` — the detector's state is frozen at its last confirmed value until
the bar actually confirms, at which point it updates exactly once. This adds
zero new inputs and changes nothing about the detector's actual math; it
only changes *when* that math is allowed to run.

## When to use it

Any time a detector originally built as a plain `indicator()` (accumulator-
based change-point detectors, breakout/level trackers, regime classifiers —
anything with `var` state that resets itself on its own trigger condition)
is reused, ported, or adapted into a `strategy()` context. The tell is
simple: does the detector mutate any `var` state as a direct function of
`close`/`high`/`low` on the current bar, with no `request.security` pull
involved? If yes, and that state feeds an entry decision, it needs this
gate — MTF-pulled signals (see `mtf-confirmed-pivot-pull.md`) get their
confirmation for free from `lookahead_on` + the two-layer `[1]`-offset
pattern; a native-timeframe detector gets no such protection automatically
and needs it added explicitly.

## Pitfalls it avoids

- Multiple spurious `isChange`/break/breakout events firing and resetting
  the detector's own accumulators within a single still-forming bar,
  something that would never show up by inspecting historical bars (which
  only ever show the settled, confirmed outcome) but is a real live-trading
  risk.
- The `calc_on_every_tick = true` setting most of this repo's strategies use
  for responsive dashboards (see `futures-strategy-margin-simulation.md`'s
  sibling lesson on why that setting matters) makes this specific risk
  *more* likely to matter in practice, not less — more intrabar re-evaluations
  means more chances for a still-forming bar's noise to trip a native
  detector's own event condition before it settles.

## Applied in this repo

`delta_break_retest/Stage9_ChangePointVolumePressure.pine` — ported a
user-supplied CUSUM log-return change-point detector (originally a plain
`indicator()`-style script with no confirmation gating at all) into a
`strategy()` alongside Stage 8's entry-logic scaffold. The gating shown
above is the only functional change made to the user's own CUSUM math;
everything else (the log-return/z-score/CUSUM formulas themselves) was kept
exactly as supplied.
