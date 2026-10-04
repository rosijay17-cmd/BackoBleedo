# Breakout Price Action (Brooks, *Trading Price Action Trading Ranges*, Part I)

**Citation:** Brooks, A. (2012). "Breakouts: Transitioning into a New Trend" (Part I,
Chapters 1-6: "Example of How to Trade a Breakout," "Signs of Strength in a Breakout,"
"Initial Breakout," "Breakout Entries in Existing Strong Trends," "Failed Breakouts,
Breakout Pullbacks, and Breakout Tests," "Gaps"). *Trading Price Action Trading Ranges:
Technical Analysis of Price Charts Bar by Bar for the Serious Trader*. John Wiley & Sons.

## Evidentiary basis — read this before the rest of the file

This is the weakest-evidence, most purely discretionary source in this skill by a wide
margin — weaker than papers #10 (Scheier) and #11 (Person), both of which at least had
scattered numerical examples across multiple markets. Across 63 pages there is no
backtest, no sample size, no cited study — just extremely detailed, bar-by-bar
narrative walkthroughs of individual historical charts, describing what the author
believes institutional traders were thinking on each bar. The handful of numerical
claims that do appear (a ~60-70% follow-through probability for strong breakouts, a
~30% failure rate even for the strongest ones) are stated as the author's own trading
experience, not measured. Treat every specific percentage in this file as "one
experienced trader's stated heuristic," not a validated statistic — the same caution
already applied to Scheier and Person. What earns this source a place in the skill is
that one section (Chapter 2's signs-of-strength/weakness checklist) is unusually
precise and mechanizable despite the surrounding narrative style — most of the rest of
the book is not.

## Core Content

**The central thesis, repeated throughout**: most breakout attempts fail — the market
has strong inertia and resists transitioning between trading-range and trending
states. Every trend bar is itself functionally a breakout, a spike, and a gap
simultaneously (a trend bar's body has no overlap with the prior bar's range, the same
geometric signature as a session-open gap) — so breakout analysis isn't limited to
classic "price crosses a swing high/low" events; a single unusually strong trend bar
carries the same follow-through statistics as a textbook breakout and is worth scoring
in its own right.

**Signs of strength in a breakout (Chapter 2) — the standout, mechanizable content.**
A long, itemized checklist of characteristics, each one independently increasing or
decreasing the odds a breakout will have real follow-through. Compressed here to the
items that are actually computable from OHLCV, dropping the purely subjective ones
("there is a sense of urgency"):

*Increases confidence (bull breakout; mirror-image for bear):*
- Breakout bar has a large body relative to its range, with small or no tails.
- Volume is 10-20x the recent average.
- The bar's low stays near its high as it forms (pullback during formation stays under
  ~25% of the bar's height).
- The next 2-3 bars also have above-average-size same-direction bodies.
- The spike runs 5-10 bars without any pullback exceeding about one bar's worth.
- A micro-gap forms between consecutive trend bars in the spike (the low of one bar at
  or above the high of the bar two back) — the same geometric signature this skill
  already logged as a Break-Away Lap (paper #10) and independently arrived at here.
- The first pullback after the breakout doesn't arrive for at least 3 bars, then lasts
  only 1-2 bars, doesn't reach the breakout point, and doesn't hit a breakeven stop.
- The breakout bar's close reverses many prior bars' closes and highs/lows (the more
  bars reversed, the stronger — directly comparable to this repo's already-planned
  "eight to ten new records" exhaustion counter from paper #11, just measuring
  reversal strength instead of extension length).

*Decreases confidence (mirror image applies to both directions):*
- Small/average body with a large tail on the breakout bar.
- The very next bar has an opposite-direction body closing near its own extreme.
- The pullback arrives within 1-2 bars of the breakout, extends for several bars,
  retraces more than two-thirds of the breakout bar's height (possibly more than once
  as the bar forms), falls below the breakout point or the first bar of the spike, or
  hits the breakeven stop.
- The spike barely clears a resistance/support level (by a tick or so) before
  reversing, rather than clearing it and continuing.

**The "trader's equation" / probability heuristic.** Brooks' repeated claim: a strong
breakout spike has "at least a 60%" (sometimes stated as up to 80%) chance of reaching
a measured move roughly equal to the spike's own height, before retracing back to the
spike's low. Since the stop (below the spike low) and the target (spike height) are
roughly the same size, a 60%+ win-rate with a ~1:1 reward:risk is framed as a strongly
favorable bet — the "math is on their side" even when the entry feels emotionally
terrifying (buying at the top of a fast, tall spike). Explicitly not derived from a
study — an experienced trader's stated rule of thumb, given here as exactly that.

**Dynamic position sizing within a single developing spike.** As a spike extends and
the logical stop (below its low) gets further away, experienced traders don't skip the
trade — they reduce position size to keep dollar risk constant, then re-add as the
market moves in their favor and the effective risk shrinks. This is the same principle
as this repo's already-used ATR-scaled sizing (`Kaufman_Trend_System_Swing.pine`,
`Herberger_Intraday_Reversal_Feasibility.pine`), but applied continuously as a single
trade's stop distance changes mid-formation, rather than computed once at entry — a
genuinely new refinement, not yet implemented anywhere in this repo.

**Measured-move target calculation (multiple variants, all arithmetic).**
- Basic: project the height of the breakout spike (or the leg leading into it) from
  the breakout point.
- Gap-based: for a breakout that leaves a gap between the breakout bar and the bar
  before/after it, measure from the start of the leg to the *middle* of the gap, then
  project that same distance again beyond the gap's middle.
- Micro-gap variant: the same calculation using the small gap between a single strong
  trend bar and its neighbors, for finer-grained intraday targets.
- "Negative gap" variant: when the breakout test undershoots and actually closes the
  gap (or overshoots the breakout point on the test), the measured-move arithmetic
  still runs (using a negative distance), producing a less reliable but still usable
  projection — explicitly flagged by the source as "worth watching," not as reliable
  as a clean positive gap.
- Multiple simultaneous candidate breakout points (several nearby swing highs, say)
  each generate their own separate measured-move projection; a cluster of several
  projections landing near the same price is read as a stronger confluence target.

**Breakout tests and the "first failure isn't necessarily failure" distinction.** A
pullback that arrives within 1-2 bars of a breakout technically means the breakout has
already failed in the strict sense — but if the reversal itself only lasts 1-2 bars
before the original trend resumes, the "failure" converts into a legitimate breakout
pullback (a valid re-entry setup, sometimes called a cup-and-handle). A breakout test
that falls just short of the exact breakout price (by a tick or so) reads as strength;
a test that blows through the breakout point by more than a tick or two reads as
weakness — a precise, directly computable distinction (`breakoutLevel - testExtreme`,
signed).

**Gap taxonomy (Chapter 6).** Traditional classification — breakaway/breakout gaps
(form at a trend's start), measuring gaps (form mid-trend, their midpoint plus the
leg's starting distance gives a measured-move target), and exhaustion gaps (form late
in a trend and get closed, often preceding a reversal or at minimum a correction). A
gap's classification is explicitly not fixed — the same gap gets reclassified in
hindsight as more bars form (a "measuring gap" candidate that never gets exceeded and
then closes becomes, retroactively, an exhaustion gap instead).

## Pitfalls (evident from the source itself)

- **Almost none of this is backtested or sourced** — every claim is Brooks' own stated
  trading experience across thousands of hours of chart-watching, not a study. The
  60-70% follow-through figure, the 30% failure-even-for-strong-breakouts figure, and
  every "usually" and "often" in the signs-of-strength checklist are anecdotal.
- **The checklist items are independently plausible but never weighted or combined
  systematically** in the source — there's no stated rule for how many "signs of
  strength" outweigh how many "signs of weakness," or whether they should be summed,
  averaged, or gated. Any Pine implementation needs to make that combination choice
  itself, since the book doesn't.
- **Extremely bar-count-dependent claims** (e.g., "a large number of bars reversed by
  the close is a stronger sign than a similar number reversed by the high") are highly
  specific to the author's own discretionary reading and harder to validate than they
  are to state.

## Portability

| Technique | Portable to Pine? | Notes |
|---|---|---|
| Signs-of-strength/weakness checklist (body/tail ratio, volume multiple, pullback depth/timing/duration, micro-gap presence, close-reversal count) | ✅ Direct, as a scored checklist | Every item above is computable from `open`/`high`/`low`/`close`/`volume`; the combination/weighting is a design choice this repo would have to make, not one the source specifies |
| Measured-move target calculation (spike height, gap-midpoint variants, negative-gap variant) | ✅ Direct | Pure arithmetic on price levels already being tracked |
| Breakout test precision (`breakoutLevel - testExtreme`, signed) as a strength/weakness read | ✅ Direct | A single subtraction |
| Dynamic mid-trade position-size scaling as the logical stop distance changes | ✅ Direct | An extension of the ATR-scaled sizing formula already used in this repo, recomputed as the stop moves rather than fixed at entry |
| "Trader's equation" 60-70% follow-through heuristic | ⚠️ Codeable as a display/decision rule | The percentage itself is unvalidated — usable as a documented assumption, not a measured probability, unless re-derived from this repo's own backtests |
| The qualitative narrative reasoning generally (institutional psychology, "sense of urgency," discretionary trend-strength reads) | ❌ Not systematizable | The same limitation already noted for Scheier's and Person's discretionary content — pattern-recognition judgment, not a specified rule |

## Mapping to This Repo

- **The signs-of-strength/weakness checklist is a strong, concrete candidate for a new
  "breakout quality score" module** — conceptually the same architecture as the
  strength-scoring system already built in `Supply_and_Demand_Zones_XL.pine`
  (formation volume, departure velocity, purity, endurance, decay, touch penalties →
  a 1-10 score), just re-targeted at scoring a live breakout bar/spike instead of a
  historical zone. Given how many of this repo's scripts already gate on a breakout
  (ORB scripts, `Regime_Engine_TCO_Gatekeeper.pine`'s EXPANSION regime, the various
  liquidity-sweep scripts), this could plug in as an additional confirmation score
  rather than a replacement for any of their existing logic.
- **The measured-move gap-based target calculation is a concrete, portable alternative
  target method** for any script currently using a flat R-multiple or ATR-multiple
  exit — alongside the Inverse 78.6% Projection Rule already logged from paper #10 and
  the CP2 projected-crossover concept from `Kaufman_Trend_System_Swing.pine`, this
  repo now has three independently-sourced, non-Fibonacci target-calculation methods
  worth comparing empirically in `quantor` rather than defaulting to any one of them.
- **Dynamic mid-trade position sizing (scale down as the stop distance grows, scale
  back up as it shrinks) is a genuinely new refinement** to the ATR-scaled sizing
  formula already used in `Kaufman_Trend_System_Swing.pine` and
  `Herberger_Intraday_Reversal_Feasibility.pine` — both currently size once at entry
  and hold that size for the life of the trade.
- **A third independent source now touches "repeated tests of the same level get less
  reliable"** (alongside paper #11's explicit "first test only" pivot-fade rule and
  paper #10's Y-High/Y-Low exhaustion framing) — not stated as cleanly here as in
  Person's version, but the breakout-test-precision discussion (a test that falls
  short reads as strength, repeated failed tests erode confidence in the losing side)
  is the same underlying idea from a third, independent, unrelated author.
- **The "every trend bar is itself a micro-breakout" framing is a useful design
  reminder, not a new feature to build**: it argues for scoring individual strong
  trend bars (not just formal level-crossings) using the same signs-of-strength
  checklist, which several of this repo's scripts (candle-pattern-adjacent logic, if
  paper #11's candlestick catalog is ever implemented) would naturally support without
  new infrastructure.

## Applied in This Repo

*(none yet — the signs-of-strength/weakness breakout quality score and the gap-based
measured-move target calculation are the two standout, ready-to-build candidates.)*
