# Pivot/Exhaustion Grid (Scheier, *Pivots, Patterns, and Intraday Swing Trades*, Ch. 3)

**Citation:** Scheier, M. W. (2014). "Pivot/Exhaustion Grid" (Chapter 3). *Pivots,
Patterns, and Intraday Swing Trades: Derivatives Analysis with the E-mini and Russell
Futures Contracts*. John Wiley & Sons.

## Evidentiary basis — read this before the rest of the file

This is the weakest evidentiary source in this skill so far, and should be weighted
accordingly. It's a single practitioner's discretionary trading philosophy, illustrated
with individual annotated charts, not a study. Across the whole chapter there is exactly
**one** quantified sample (39 gaps, one contract — Russell TF futures — over a 90-day
window in 2013), and even the author's own framing leans on intuition and "a little
practice" for most of the techniques (trend lines: "just eyeball the connecting lows and
highs"; break-away pivots: "the concept is easier to understand visually than in
words"). Several techniques here are genuinely well-specified and mechanically
testable (the gap-close behavior, the EMA-translation formula, the pivot-point
formula, the Inverse 78.6% projection rule) even though the author never tests them
systematically — those are logged as precise, portable *techniques*, not validated
findings. Others (trend lines, Break-Away Pivots, Measured Move chart-pattern targets)
are fundamentally pattern-recognition judgment calls that would need real, separate
detection algorithms before they could be systematized at all, and this chapter
doesn't attempt that. Treat everything below as "worth knowing and worth testing,"
never as "already shown to work."

## Core Concepts

**ORB as an all-day level, not just a breakout trigger ("ORB Kilroy").** The Opening
Range Bar's high/low persists as support/resistance for the *entire* session, not only
during the initial breakout — and gets *more* significant the longer price stays away
from it, within the same day. The specific pattern: late in the day, especially during
a fast midday correction, price often pokes just through the **far side** of the ORB
(the side away from the current trend) before snapping back — a shallow, brief
exhaustion spike the author nicknames "the Kilroy," used as a place to re-enter the
original trend or exit a countertrend correction. Distinct from the *near* side of the
ORB, which behaves as ordinary support/resistance when price is still close to it
earlier in the day.

**Break-Away Pivot / Pivot Ledge.** A support/resistance level that does *not* form at
a swing high or low. It forms at the "shoulder" of a pattern — the base level price sat
at immediately before a sudden, steep acceleration away from it. The level left behind
(the "Ledge") acts as strong future support/resistance, and — per the author — is often
where a trend's momentum finally dies when price eventually returns to retest it. This
is a genuinely different detection target than a pivot high/low: it's about consolidation
immediately preceding a momentum expansion, not a local price extreme.

**Break-Away Lap.** A small, precisely-defined gap between two *consecutive intrabar
bars* — the close of one bar and the open of the next don't touch, leaving a sliver of
untouched price ("no air" — distinct from a session Gap, which is a *range* gap between
one bar's high/low and the next's, and is more consequential). Marked once, terminates
(stops projecting forward) the first time price touches it again. Conceptually adjacent
to what much of the current retail-trading vocabulary calls a Fair Value Gap (FVG) —
worth naming directly, since the user explicitly chose to drop FVGs from
`Regime_Engine_TCO_Gatekeeper.pine`'s planned feature set earlier this session. This is
the same family of idea under a different, older name; that earlier decision is
relevant context, not a reason to avoid logging the technique here.

**Previous highs/lows (Y-High/Y-Low) as *exhaustion* levels, not continuation
confirmation.** Direct pushback on the common assumption that a new lower low
confirms a downtrend. The author's claim: the *initial* break of a Y-Low or Y-High,
especially with little immediate follow-through, is more often the point where the
trend reverses (stops resting exactly there get run, then price snaps back) than a
confirmation to keep pressing the trade. This is the same underlying idea as a
liquidity-sweep/stop-run setup already implemented in this repo (see Mapping below).

**Previous close / Gap-Close, with the chapter's one real data point.** A "Gap-Close"
is the previous session's closing price, tracked forward as a support/resistance level
on the day-only chart. The author's own small study, TF futures, ~90 days, June 2013,
39 gaps of ≥2 points:
- Only 6 of 39 closed within the *first* trend of the origination day (i.e., an
  immediate gap-fill trade would have worked only ~15% of the time).
- 21 of 39 eventually reversed *off* the gap (bounced within about a point of it,
  whenever it was finally revisited — sometimes days later), which the author reports
  as a materially better hit rate for **fading the gap on its eventual retest**, rather
  than trading the fill itself.
- Only 8 of 39 never reacted to the gap at all.
- **The chapter's own stated conclusion**: trade the gap's eventual *closure* as a
  reversal-back-toward-the-open-gap-direction signal, using other confirming filters —
  not a same-day gap-fill entry, and not a same-day gap-and-go continuation entry either.

**Dynamic exhaustion EMAs.** 200- and 89-period EMAs on 1-minute bars, used as
*exhaustion levels* (where a short-term spike is likely to stall), explicitly **not**
as a crossover signal pair. For higher timeframes, the same role is served by a
19-26-period EMA on 60-minute bars — and the chapter gives a fully mechanical
translation to reuse a higher-timeframe EMA's *look and feel* directly on a 1-minute
chart: multiply the period by the ratio of timeframes (roughly ×60 here), landing on
1140/1300/1560-period EMAs on 1-minute bars as the tested equivalents across
ES/YM/NQ/TF's differing volatility. A genuinely mechanical, precisely-specified,
directly portable idea — the "translate an HTF lookback into an LTF-equivalent
period" technique, independent of any chart-pattern judgment.

**Floor Trader's Pivot Points**, with an implementation pitfall worth remembering more
than the formula itself. Traditional formula: `DP = (Y-High + Y-Low + Y-Close) / 3`,
with the standard S1/S2/S3/R1/R2/R3 derived from it (not reproduced here — this is the
generic floor-pivot formula). The pitfall: **the H/L/C inputs must come from the
all-session (24-hour) daily range, not the day-only (RTH) range, even though the
resulting levels are then applied to a day-only chart.** Using day-only H/L/C for the
pivot inputs is the single biggest reported cause of two traders/vendors quoting
different pivot numbers for the "same" instrument and day — a data-plumbing detail,
not a conceptual one, but one that silently produces wrong numbers if missed.

**Fibonacci — explicit skepticism for entries, one specific rule kept for exits.** The
author's stated conclusion after extensive testing: "most Fibonacci numbers do not
produce market turns. In fact, most don't even produce reactions" — and no longer uses
Fibonacci retracement/extension levels as an entry trigger at all. The one Fibonacci-
adjacent technique kept: the **Inverse 78.6% Projection Rule**, an exit/target rule —
if a Break-Away Pivot's Ledge formed 21.4% of the way from a swing extreme (i.e., the
acceleration happened early in the move, close to the reversal point), project a
target 78.6% further beyond the Ledge, measured as the same-scale extension of that
21.4%-vs-78.6% split. A fully specified, mechanical rule, despite the author's
broader skepticism of Fibonacci as a category.

**Measured-move chart-pattern targets** (symmetrical triangle: project the open jaw's
height from the apex; head-and-shoulders: project the head-to-neckline distance from
the neckline break; channel: use the centerline as an equidistant projection anchor;
rising/declining wedge: project the base-to-apex distance). All require the underlying
chart pattern (triangle, H&S, channel, wedge) to already be detected — the target rule
itself is simple, but only as good as the pattern-recognition step feeding it, which
this chapter doesn't specify an algorithm for.

**Market Profile — mixed verdict, with a specific carve-out that matters here.** The
author is skeptical of Market Profile as a complete trade-setup tool ("soft,
approximate, only vaguely effective" beyond one specific number), but explicitly
endorses **the Point of Control (POC) alone** as a legitimate, worthwhile
support/resistance level to track — and separately states that **Volume-at-Price
(Volume Profile) is "a good approximation" substitute** when true Market Profile
(time-based TPO count) isn't available in a given charting package, since the
highest-volume price is usually close to the highest-TPO-count price anyway.

**Trend lines from a higher timeframe, carried down.** Draw trend lines/channels on a
higher timeframe (60-minute, in the chapter's examples) using **all-session data
specifically** (not the day-only/RTH range used elsewhere in the same grid for gap
tracking), then project those same lines down onto the lower intraday timeframe the
trader actually executes on. The chapter's own before/after comparison (Figures 3.11
vs. 3.15) shows the all-session 60-minute trend channel catching roughly three dozen
contact points across a 3-month window that the day-only version of the same chart
did not show as cleanly — anecdotal, single-instrument, but a clean illustration of
the specific claim (all-session data matters for trend lines, day-only data is fine
for tracking gaps).

## Pitfalls

- **Nearly the entire chapter relies on visual/discretionary pattern recognition**
  ("just eyeball," "a little practice") for the concepts that would matter most for a
  systematic Pine implementation (Break-Away Pivots, trend lines, chart-pattern
  targets). Only a handful of the techniques here (Break-Away Lap, the EMA-translation
  ratio, the DP formula, the Inverse 78.6% rule, and the gap-close statistic) are
  precise enough to code without first building a separate pattern-detection layer.
- **The one quantified claim (the 39-gap study) is a single contract, single 90-day
  window, no out-of-sample check, and no statistical test of significance** — a
  suggestive anecdote pointing at a testable hypothesis (fade a stale gap on its
  eventual retest, don't trade the fill), not evidence the hypothesis holds.
- **The Floor Trader's Pivot vendor-discrepancy warning is really about data
  correctness, not trading edge** — worth remembering as an implementation checklist
  item (verify session range assumptions match the intended convention) any time this
  repo computes daily pivots via `request.security("D", ...)`, independent of whether
  the pivot technique itself has any edge.

## Portability

| Technique | Portable to Pine? | Notes |
|---|---|---|
| ORB Kilroy (far-side ORB exhaustion poke) | ✅ Direct | Just a price-vs-ORB-level comparison plus a "distance from ORB / time of day" condition — this repo already has the ORB level infrastructure in several scripts (see Mapping) |
| Break-Away Lap (intrabar gap, terminate-on-touch) | ✅ Direct | A gap test between `high`/`low` of adjacent bars plus a persisted "untouched" flag — mechanically identical in shape to this repo's existing zone/level "wipe on touch" patterns |
| Y-High/Y-Low exhaustion read | ✅ Direct | Simple level tracking plus a "shallow penetration, quick reclaim" condition |
| Gap-close-as-reversal-signal | ✅ Direct (the mechanic) / ⚠️ Unvalidated (the edge) | Tracking the prior close and detecting its retest is trivial in Pine; whether fading it actually works needs a proper `quantor` backtest, not just this chapter's one small sample |
| EMA-period HTF-to-LTF translation (×60-style ratio) | ✅ Direct | Pure arithmetic on the length input; this repo already has an analogous pattern in its structure-timeframe handling (`Supply_and_Demand_Zones_XL.pine`) |
| Floor Trader's Pivot Points (DP/S/R formula) | ✅ Direct | Standard formula; the all-session-vs-day-only session range choice is the part to get deliberately right, not a portability barrier |
| Inverse 78.6% Projection Rule | ✅ Direct, once a Ledge is identified | The projection arithmetic itself is trivial; depends on first detecting a Break-Away Pivot, which is the harder, judgment-based part |
| Break-Away Pivot / Pivot Ledge detection | ⚠️ Needs a real detection algorithm | "Shoulder before a sudden acceleration" isn't specified mechanically in this chapter — would need its own rule (e.g., an ATR-expansion bar following N bars of tight consolidation) before it could run unattended |
| Trend lines (manual, "eyeball the connecting lows and highs") | ⚠️ Needs a real detection algorithm | Not specified as an algorithm at all; would need a proper swing/regression trendline detector, or manual anchor inputs, to systematize |
| Measured-move chart-pattern targets (triangle/H&S/channel/wedge) | ⚠️ Needs pattern detection | The target math is trivial; the bottleneck is detecting the pattern itself, which this chapter doesn't specify — this repo's `Auto_Pattern_Detector_Targets_MarkitTick_Session_Strategy.pine` may already be relevant prior art to check against |
| Market Profile (true TPO-based Value Area/POC) | ❌ Not native to Pine | Pine has no time-price-opportunity primitive; Volume Profile (already built in this repo) is the author's own named substitute, not a workaround invented here |

## Mapping to This Repo

This chapter connects to an unusually large number of existing files, mostly because
it's describing the same retail/discretionary vocabulary (ORB, liquidity sweeps,
gaps, pivots) this repo's strategies already implement under various names:

- **ORB Kilroy is a specific, nameable behavior this repo's many ORB scripts don't yet
  encode** — `15_Minute_ORB_Box_Break_Return_Cross_Strategy.pine`,
  `ORB_Break_and_Retest_v3.pine`, `Institutional_ORB_v6_Boxes_Regime_Fakeout.pine`,
  `STRONG_NQ_ORB_BREAKOUTS.pine`, `MNQ_OneAndDone_Confirmed_Expansion_v1.pine`,
  `ES_ORB_15min_RTH.pine`, `15M_Confirmed_Breakout_Strategy_v2.pine` all track the ORB
  level, but (as far as this file's ingestion pass can tell from names/prior sessions)
  none specifically model "late-day poke through the *far* side of the ORB, then snap
  back" as its own distinct exhaustion signal, separate from the initial-breakout use
  of the same level. A concrete, well-defined candidate feature for any of these.
- **Y-High/Y-Low-as-exhaustion is the same underlying idea already implemented as a
  liquidity-sweep/fakeout concept** in `MNQ_Liquidity_Sweep_Trend_Following_v1_3_
  Territory_Blocker.pine` and `Institutional_ORB_v6_Boxes_Regime_Fakeout.pine` (the
  "Fakeout" in that name is exactly this chapter's Y-Low/Y-High exhaustion-not-
  confirmation claim). Convergent validation from an independent, much less
  quantitative source — worth noting, not re-implementing.
- **Break-Away Lap is conceptually the same family as a Fair Value Gap**, which the
  user explicitly chose to drop from `Regime_Engine_TCO_Gatekeeper.pine`'s planned
  feature set earlier this session ("Let's get rid off FVGs"). That decision stands —
  this is flagged here for completeness of the record, not as a reason to revisit it.
- **Market Profile's POC endorsement, and its explicit "Volume-at-Price is a good
  approximation" carve-out, is independent, converging validation for the Volume
  Profile (POC/VAH/VAL) module already built this session** in
  `Supply_and_Demand_Zones_XL.pine` and ported into
  `Regime_Engine_TCO_Gatekeeper.pine` — two unrelated sources (this chapter, and the
  earlier DeepSupp-paper critique) now separately point at the same conclusion:
  volume-at-price is the practical, implementable stand-in for a "true" profile-based
  level, worth trusting more than either source alone would justify.
- **The Floor Trader's Pivot session-range pitfall is a direct checklist item** for any
  script in this repo computing daily pivots via `request.security("D", ...)` — verify
  whether the intended convention is all-session or day-only H/L/C, and apply it
  consistently, independent of whatever edge (if any) the pivot levels themselves add.
- **The Inverse 78.6% Projection Rule is a genuinely new, well-specified exit-target
  idea** for any script currently using a flat R-multiple or ATR-multiple target (e.g.
  `Supply_and_Demand_Zones_XL_Strategy.pine`'s reward-risk exit) — worth prototyping as
  an alternative target calculation if the user wants a target that scales with how
  aggressively a Break-Away-style level formed, rather than a fixed multiple.
- **`Auto_Pattern_Detector_Targets_MarkitTick_Session_Strategy.pine` may already be
  relevant prior art** for the Measured-Move chart-pattern target family (triangle/
  H&S/channel/wedge) — worth checking what it already detects before treating that as
  new work.

## Applied in This Repo

*(none yet — this file catalogs technique and cross-references; see Mapping above for
the concrete, well-specified candidates — ORB far-side exhaustion, the Inverse 78.6%
target rule, and the session-range pivot checklist — that don't require building a new
pattern-detection layer first.)*
