# Cycle Analysis (Kaufman, *Trading Systems and Methods*, Ch. 11)

**Citation:** Kaufman, P. J. (2019). "Cycle Analysis" (Chapter 11). *Trading Systems and
Methods*, 6th ed. John Wiley & Sons.

**Format note:** this is a textbook survey chapter, not an empirical study with a
tested hypothesis — different in kind from papers #1-7 already in this skill. It's a
practitioner's field guide to detecting and using cycles, several of them openly
speculative, with Kaufman's own skepticism noted inline in several places. Treated
here accordingly: as a source of technique and terminology, not validated findings.

**Coverage note:** the uploaded excerpt is 21 pages and stops mid-example (an Excel
Solver setup fitting `y = a·cos(wt) + b·sin(wt)` to detrended corn prices), before
showing the fitted result or reaching the chapter's own stated destination — Fourier
(spectral) analysis and John Ehlers' Maximum Entropy Spectral Analysis (MESA), both
named in the opening paragraph as the two main rigorous methods but never actually
covered in what was provided. If a future session gets the rest of the chapter, treat
this file as needing a follow-up pass — the trigonometric section here is the *weaker*
of the two methods the chapter itself sets out to explain.

## Core Methodology

**Decomposition model.** Price movement = trend + seasonality + cycle + noise (the last
being "everything not accounted for in the first three"). To isolate the cycle, remove
trend and seasonality first (first differences for trend; a centered 12-period average
lagged 6 months for seasonality), then whatever periodic structure remains in the
residual is the cycle.

**Hurst's Five Principles (1970)** — the conceptual vocabulary for the rest of the
chapter:
- *Summation*: a large cycle can be composed of smaller cycles (harmonics — a smaller
  cycle's length is typically 1/2, 1/3, 1/4... of the larger one).
- *Commonality*: macro/economic events move many markets' cycles together.
- *Variation*: cycle length is not fixed — peaks/valleys drift, they don't recur on a
  metronome.
- *Nominality*: shorter common cycles often trace to calendar events (earnings, etc.).
- *Proportionality*: longer cycles have proportionally larger retracements — same shape
  as this repo's own trend-following intuition, just applied to cycle amplitude instead
  of trend strength.

**Manual cycle identification** (the "cattle cycle" worked example): plot the series,
circle the visually obvious peaks/valleys, measure days between consecutive peaks and
between consecutive valleys, average the two counts. Requires roughly 8+ cycle
repetitions before trusting the result. Kaufman explicitly grounds this example in real
fundamentals: it takes 4-6 months to wean a calf and 6-10 months to fatten it for
market, so a ~10-month cattle cycle (10.2 months measured) has an actual causal
mechanism, not just curve-fit pattern-matching.

**Detrending for cycle isolation**: subtract a moving average (lagged by half its
period) from price, or take `p_t - p_{t-N}` (first differences over the guessed cycle
length N). Enhancement: use **triangular weighting** instead of equal weighting — a
symmetric weight kernel that peaks at the center of the window and tapers linearly to
1.0 at both ends (formula and worked 9-period example given in the source). Take two
triangular moving averages, one at half the period of the other, and difference them —
this is a **"triangular MACD"**, the chapter's practical, implementable cycle
oscillator (worked examples: 63-day/quarter-earnings cycle on IBM at 20-10 periods;
252-day/annual cycle on corn at 252-126 periods). Explicitly a momentum-indicator
relative — peaks/valleys won't be evenly spaced or equal amplitude, but it's smooth
enough to anticipate major turns.

**Trigonometric curve fitting**: represent price as `y = a·sin(ωφ + b)`, or a sum of
several such sine terms for a compound wave (`y = a₁sin(ω₁φ+b₁) + a₂sin(ω₂φ+b₂) + ...`).
Terminology: amplitude `a`, period `T`, frequency `ω = 1/T`, phase `b` (horizontal
shift), phase angle (position within cycle, clock-face convention), left/right
translation (peak skew relative to cycle center). Fit via least squares — practically,
via Excel Solver: detrend the series, then vary `a`, `b`, `ω` in `y = a·cos(wt) + b·sin(wt)`
to minimize the standard deviation of the residual. First/second derivatives of the
fitted wave locate its maxima/minima (`y'=0` for extrema; `y''>0`→minimum, `y''<0`→maximum).

## Key Findings (and where Kaufman himself is skeptical)

- **The cattle cycle (worked example) has a real fundamental basis and holds up**:
  ~10.2 months, consistent across two disjoint historical periods (1978-1984 and
  2012-2017) with matching averages, and matches known feeder/finisher timelines.
- **The Swiss franc "cycle" is presented as a negative/cautionary result, not a finding.**
  Peak spacing ranged from 26 to 52 months over the sample with no consistent period
  found and no clear fundamental mechanism proposed beyond a speculative link to
  year-end profit repatriation. Kaufman's own conclusion: "there did not appear to be a
  26-month cycle. What fundamentals would cause such a cycle?" — i.e., presented
  specifically to teach *recognizing when a cycle claim doesn't hold up*, the same
  spirit as this skill's recurring "no free edge" finding from other papers.
- **Macro/political cycles (8.6-year business cycle, 25-year "Wheeler Index of War",
  54-year Kondratieff wave) are treated with real skepticism inside the source itself.**
  Two different cited sources give incompatible period claims for what's nominally the
  same war/political cycle (25.049 years per Wheeler vs. 18 years plus 54-year
  socio-political plus 4.5/9-year subcycles per a second source), never reconciled.
  On Kondratieff specifically, Kaufman writes: "with only three full cycles completed,
  it is difficult to tell if the overall trend is moving upward, or whether the entire
  pattern is just a coincidence" — a direct admission that the sample size is too small
  to distinguish a real 54-year cycle from noise. These sit closer to numerology than to
  the cattle-cycle example; **not a source of tradeable signal**, included here only so
  a future session recognizes the citations rather than re-deriving this same caution
  from scratch.
- **The Presidential Election Cycle is the most quantitatively grounded section**, with
  real return data across ten election cycles (1936-1992, Table 11.3) and detailed
  annual breakdowns 1948-2016 (Figures 11.9-11.12). Consistent findings: the 3rd year of
  a presidential term has both the highest average return *and* the lowest volatility of
  the four-year cycle (Figure 11.10 — "only the 3rd year of the cycle has low
  volatility"); the election year itself is the most erratic (a 39% average-return swing
  range). A plausible mechanism is proposed (incumbent-party fiscal policy timed to
  produce good pre-election economic news). Still a macro/calendar-timing signal on a
  multi-month-to-year horizon — not applicable to this repo's intraday MNQ work, but
  the most defensible cycle claim in the whole chapter.

## Pitfalls (explicit in the source, or evident from it)

- **Detecting a cycle post-hoc, without a fundamental mechanism, is close to
  data-mining a periodicity out of noise.** The chapter itself draws this line (cattle =
  yes, Swiss franc = no) but several of its own later examples (war/political cycles)
  arguably fall on the wrong side of that same line the author draws for the Swiss
  franc case, without saying so as explicitly.
- **Cycle length is not stable ("Variation Principle").** A "10-month" or "8.6-year"
  cycle is a historical average, not a metronome — trading on the assumption a peak
  will land exactly N days after the last trough is a much stronger claim than what any
  of these methods actually establish.
- **Cycles get overwhelmed by strong trends**, the same failure mode noted for
  seasonality in the prior chapter — classic cycle identification requires removing the
  trend and seasonal components first, which is itself a source of error if the
  detrending method (moving average, first differences) leaks trend back into the
  "cycle" residual or vice versa.
- **The triangular MACD is fundamentally a momentum indicator wearing cycle
  terminology** — it will not produce evenly spaced, equal-amplitude turns even when a
  genuine cycle exists, because real price series rarely obey a pure sinusoid. Useful
  as a smoothed turn-anticipation tool, not as a literal cycle clock.

## Portability

**Triangular-weighted moving average / triangular MACD**: fully portable to Pine — it's
just a custom weighted-average kernel (`array.new<float>` of triangular weights, applied
via a rolling dot product) differenced at two periods, no different in kind from any
other weighted MA already computable in Pine. The one design decision that matters is
picking the candidate period(s) from an actual fundamental or empirically-observed
periodicity for the instrument/timeframe in question — see Mapping below for why this
matters more than the math itself.

**Manual peak/valley cycle measurement** (the cattle-cycle method): portable as an
offline `quantor`/Python analysis step (find local extrema, measure spacing, average) to
*discover* whether a candidate instrument/timeframe shows a genuine periodic component
before ever encoding a period into a Pine script. Not something to run live in Pine bar
by bar.

**Trigonometric least-squares curve fitting (the corn/Solver example)**: possible in
Pine only in a limited, fixed-parameter form — Pine has `math.sin`/`math.cos` but no
iterative nonlinear least-squares solver equivalent to Excel's Solver or `scipy.optimize`.
A single-frequency fit (`y = a·cos(wt) + b·sin(wt)` for a *known, fixed* `w`) reduces to
ordinary least squares on two linear terms, which Pine *could* compute directly (closed-form
OLS via summed products over a rolling window), but searching over `w` itself (the actual
"find the cycle period" step) is a nonlinear/iterative problem exactly like the
Markov-switching MLE fits and DBSCAN clustering already flagged elsewhere in this skill
as Python-pipeline-only. **Recommended split**: find the candidate period(s) offline
(`quantor`, or even literally Excel Solver as the source describes), then hardcode/input
the resulting fixed period into a Pine `triangular MACD`-style oscillator. Never try to
discover the period live, bar by bar, inside Pine itself.

**Fourier/spectral analysis and MESA**: not covered in the uploaded excerpt (see
Coverage note above) and not assessable from what's available. Both are referenced as
the chapter's actual recommended rigorous methods, ahead of the trigonometric approach
detailed here. Flagged as a gap — if the rest of the chapter (or a dedicated Ehlers
MESA/Hilbert-transform source) is ever supplied, it likely supersedes the trigonometric
section here as the better-grounded technique, and Ehlers' adaptive-cycle indicators
(MESA, Hilbert-transform-based `ta`-style oscillators) have known, previously-published
Pine ports in the broader community worth checking against instead of rebuilding from
first principles.

## Mapping to This Repo

- **This repo's TCO engine currently uses a different decomposition than this chapter's
  trend+seasonal+cycle+noise model.** `Regime_Engine_TCO_Gatekeeper.pine`'s REGIME row
  (TREND / EXPANSION / CHOP / SQZ) is a discrete-state classification, structurally
  closer to the Markov-switching paradigm already in this skill (papers #2, #6) than to
  a continuous periodic-cycle model. Not a contradiction — different generative
  assumptions about the same non-stationary price series — but worth naming explicitly:
  a cycle oscillator would be a genuinely new signal *type* for this repo, not a
  variant of anything already built.
- **The chapter's own dividing line (cattle cycle = yes, Swiss franc/political cycles =
  no) is the operative lesson for this repo, more than any specific formula.** Before
  ever adding a cycle-based oscillator to an intraday MNQ script, the right first step
  (per this chapter's own method) is the offline peak/valley measurement exercise on
  the actual instrument/timeframe in question, checking for both (a) a stable period
  across many repetitions and (b) a plausible fundamental mechanism at that timeframe
  (session structure, futures roll, economic data release cadence). Absent both, a
  "cycle" indicator on 5m/1H MNQ bars would be exactly the kind of unfounded
  pattern-matching the Swiss franc example warns against — nothing about intraday
  index futures obviously produces a stable multi-bar periodicity the way calf-weaning
  timelines produce the cattle cycle.
- **If a genuine short-period cycle is ever confirmed for the trading instrument/timeframe
  this repo actually uses**, the triangular MACD is the practical, portable technique to
  reach for — a smoothed, differenced weighted-MA pair, the same computational shape as
  indicators already used throughout this repo's scripts (RAP/EMA RAP, VWAP), just with
  a triangular instead of exponential/simple kernel and a fixed candidate period found
  offline first.

## Applied in This Repo

*(none — no confirmed periodic component has been established for this repo's
instruments/timeframes yet; see Mapping above for the offline verification step that
should precede any implementation.)*
