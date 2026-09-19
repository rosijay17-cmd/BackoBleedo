# Trend Systems (Kaufman, *Trading Systems and Methods*, Ch. 8)

**Citation:** Kaufman, P. J. (2019). "Trend Systems" (Chapter 8). *Trading Systems and
Methods*, 6th ed. John Wiley & Sons.

**Format note:** same as paper #8 (Ch. 11, Cycle Analysis) — a textbook survey, not an
empirical study, but by far the most directly applicable source in this skill so far.
Where the cycle chapter was mostly speculative macro pattern-matching, this chapter is
the practitioner core of trend-following: the actual toolkit this repo's Pine scripts
already partially reimplement, with real backtest tables (futures 1991-2018, stocks
1998-2018) instead of single anecdotal charts. Treated with the same discipline as
every other source here — technique and documented empirical pattern, not a validated
edge to copy blindly.

## Core Methodology

### Why trend systems work, and what "working" looks like

Three stated reasons: (1) long-term trends track slow-moving fundamentals (interest
rate policy above all); (2) prices have a **fat tail** — far more long directional runs
than a random walk would produce (worked coin-flip comparison: expected ~1-2 runs of 6
in 100 trials, real markets show runs of 12+); (3) money flow is self-reinforcing —
funds moving into a strengthening trend extend it further. **Capturing the fat tail is
the entire point of pure trend-following** — you don't need every day to go your way,
only for interim reversals to stay small enough not to end the trade.

**The generalized trend-following performance profile** (from six-system, multi-market
backtests, futures 1991-2018 and stocks 1998-2018):
- Win rate is low, **around 35%**, consistently, across almost every system and market
  tested.
- For that win rate to be profitable, **the average winner must be at least ~2.85x the
  average loser** (a 10:3.5 win:loss ratio, stated explicitly in the source).
- Winning trades are held **much longer** than losing trades (worked NASDAQ example:
  avg. 47 days in winners vs. 10 days in losers) — this is "cut your losses and let your
  profits run" made quantitative, and Kaufman names it **conservation of capital**.
- Consequently: **a high percentage of profitable trades is associated with fewer
  trades and higher risk** (breakout systems trade this way — 50-70% win rate but much
  larger max drawdown), while low-win-rate systems (simple MA) have smaller, more
  frequent losses and a better overall ratio in several of the tested markets.
- **Adding profit-taking or stop-losses to a pure trend system directly reduces the
  ability to capture the fat tail** — every "improvement" of this kind is a real
  trade-off, not a free lunch, and must be proven to help, not assumed.

### Signal construction: three ways to read the same trendline

1. **Price-cross** (buy when price crosses above the trendline) — most signals, most
   whipsaws.
2. **Close-cross** (buy when price *closes* above) — fewer signals than intrabar
   price-cross.
3. **Trendline-direction** (buy when the trendline itself turns up, regardless of where
   price is relative to it) — fewest signals, **highest profit factor in the AMZN
   10-year comparison table** (Table 8.2: e.g. 20-day trendline-direction: PF 1.45 on
   196 trades vs. price-cross PF 0.98 on 252 trades), at the cost of more lag. **Best
   for longer-term trading; price-cross is better for short-term/day trading** where the
   lag would eat the whole edge (Chapter 16 cross-reference in the source).

### Anticipating the signal (precomputing the flip price)

For an n-day MA, today's average rises iff today's price exceeds the price dropping off
n days ago (`close[n]`) — the other n-1 terms are unchanged. So the exact price that
would flip the average is knowable *before* the close, letting you place a stop order
ahead of time instead of reacting after signal confirmation. Source's own tested caveat:
in practice, delaying entry to the next open after a close-confirmed signal improved
execution price about 75% of the time, but **fast breakouts that never retrace get
missed entirely**, and those missed trades were disproportionately the profitable ones
— net effect roughly a wash. Timing-order rules given as options: wait for next open,
delay 1-3 days, wait for a 50%-of-range retracement, or a hybrid (`buy after a 0.50×ATR
reversal, or on the next close` — whichever comes first).

### Bands and channels

- **High/low band**: apply the MA separately to daily highs and lows (not just close);
  long entries cross the high-average, shorts cross the low-average. Comparison table
  (Eurodollar vs. S&P, 2001-2011): **helps the noisier market (S&P — turned a loss into
  a profit at the 40-day period) and hurts the already-trending market (Eurodollar)** —
  bands are a noise filter, valuable in proportion to how noisy the instrument actually
  is, not universally beneficial.
- **Keltner channel**: `AP = (H+L+C)/3`; 10-day MA of `AP`; bands = `MA ± AP` (source
  itself notes true range would be a better volatility proxy than this original
  formulation).
- **Percentage band**: `B = (1±c) × MA_t` (or, more reactive, using `p_{t-1}` instead of
  `MA_t`). Warns explicitly: never use a **fixed-dollar** band — it's oversensitive at
  high prices, undersensitive at low prices; percentage or volatility-scaled bands don't
  have this problem.
- **Volatility-scaled bands** (general form): `B = MA ± s×ATR` or `± s×stdev`, with `s`
  a scaling factor (s=1 ⇒ full band = 2×ATR or 2×stdev). This is the general form that
  Bollinger, Keltner (fixed), and the 10-Day Rule are all specific cases of.
- **Bollinger bands**: 20-day MA ± 2×20-day stdev of price differences (not returns).
  2 stdev ≈ 87% confidence interval for non-normal price data (would be 95.4% if
  normal). **Known flaw**: bands expand fast after a volatility spike but narrow slowly
  afterward (persistent "bulge"). **Modified Bollinger fix** (McNicholl, cited),
  fully specified: a double-exponentially-smoothed center line
  `D_t = ((2-α)M_t - U_t)/(1-α)` where `M_t = αC_t+(1-α)M_{t-1}`,
  `U_t = αM_t+(1-α)U_{t-1}`, α≈0.15 for a ~20-day equivalent — and the same
  double-smoothing construction applied to `|C_t - D_t|` for the deviation term, with
  band multiplier `f=2.5` (vs. Bollinger's 2.0). Result: bands that track volatility
  changes with much less lag than the standard construction — directly implementable
  in Pine as two chained EMA-like recursions, no different in kind from RAP/EMA RAP
  already in this repo's scripts.
- **Bollinger squeeze**: wait for the band width to compress to some fraction (e.g. 50%)
  of its own average, then trade the breakout through either band — compression has a
  documented history as a useful pre-filter (cited source, not independently re-derived
  here). **This repo's own `isSqueeze`/`WAIT BREAKOUT` state in
  `Regime_Engine_TCO_Gatekeeper.pine` is conceptually identical to this exact
  technique**, just built on ATR-ratio/range-efficiency rather than Bollinger width —
  worth naming as independent convergence on the same idea, not a coincidence.
- **Adaptive Price Zone (APZ)**, Leibfarth (cited): double-smoothed-EMA-of-(high-low)
  band, specifically framed for **mean-reversion** entries (touching the band signals a
  reversal opportunity) rather than breakout continuation — the opposite trading
  philosophy from a squeeze breakout using the same band-touch event, worth remembering
  as a reminder that "price touched the band" is not inherently a buy or sell signal —
  it depends entirely on which regime you believe you're in (this is exactly the
  distinction this repo's `atGoodEntryZone`/pullback-zone logic already makes: the same
  "price stretched away from fair value" observation is used as a *reversion target*
  gate, never as a breakout continuation trigger).

### Classic single-trend systems (fully specified formulas)

- **MPTDI (step-weighted MA)**, Taylor (1972): calculation period, weighting scheme, and
  entry-penetration/stop-loss distance **all step-change together based on which
  discrete volatility "step" the instrument is currently in** (worked gold example:
  5 discrete steps from 2-5 days/TYPE A at low volatility to 5 days/TYPE E at high
  volatility). Kaufman's own critique: the step boundaries are individually crude and
  behavior can jump abruptly at a step edge, but it's genuinely adaptive rather than
  fixed — **directly analogous to this repo's own regime-conditional behavior**
  (`riskMode` changing by `regime` in `Regime_Engine_TCO_Gatekeeper.pine`) — this repo
  already independently arrived at the same "let regime state change trading
  parameters" idea MPTDI pioneered in 1972, just via a continuous ADX/efficiency
  classifier instead of discrete volatility-range steps.
- **Volatility System** (Bookstaber, cited): `Sell if close drops > k×ATR_{t-1} from
  previous close; buy if close rises > k×ATR_{t-1}`, `k≈2.0`. Few trades, high
  reliability — the trend is defined only by a large move, and the thesis is that
  post-shock movement continues in the shock's direction.
- **10-Day Moving Average Rule** (Keltner, 1960): 10-day MA of `(H+L+C)/3`, banded by
  the 10-day MA of the high-low range (an early ATR-band hybrid) — noted as
  historically effective when price movement was smoother (pre-1980s); shorter
  calculation periods generally aren't successful on current, noisier price action.
- **TRIX** (triple exponential smoothing), fully specified: `E1_t = E1_{t-1} +
  s×(ln p_t - E1_{t-1})`, `E2_t = E2_{t-1} + s×(E1_t - E2_{t-1})`,
  `E3_t = E3_{t-1} + s×(E2_t - E3_{t-1})`, `TRIX = (E3_t - E3_{t-1})×10000` (or a
  percent-change variant without the log, `s = 2/(n+1)`, n recommended ≈6 days).
  Triple smoothing removes most of the lag a single/double smoothing would add — worked
  example shows TRIX peaks landing almost exactly at price peaks despite three
  smoothing passes. A 3-day MA of TRIX forms a signal line (same construction as MACD's
  signal line). Directly portable — three chained `ta.ema`-style recursions plus a
  rate-of-change, all primitives Pine already has.

### Comparative testing across six trend types (the chapter's own empirical core)

Six systems compared head-to-head on identical data (futures 1991-2018: Eurodollar,
e-mini S&P, Euro currency, crude oil; stocks 1998-2018: AAPL, BA, GE, V, AMZN, F):
**M** (n-day momentum), **MA** (simple moving average), **EXP** (exponential
smoothing), **BO** (n-day breakout), **SWG** (swing breakout), **LRS** (linear
regression slope sign). All six always-in-market, no stops/profit-taking, so each shows
its own natural risk profile uncontaminated by add-on rules.

- **Exponential smoothing (EXP) was consistently the weakest performer** across nearly
  every market and both asset classes — the one system the source recommends against by
  default.
- **Momentum (M) and simple MA are nearly interchangeable in results, but MA is the
  better choice** (marginally superior and no meaningful downside to preferring it).
- **No single system dominates across markets — the best performer varies by
  instrument.** Regression (LRS) was best on average for 3 of 4 futures markets tested
  and had the best per-stock average; MA best for the 4th futures market (Euro); it
  "comes down to" MA, BO, and LRS as the three worth choosing among in practice.
- **Calculation-period sensitivity is instrument-specific, not universal.** Eurodollar
  and S&P (the strongest and most macro-policy-driven trends tested) improve steadily as
  the calculation period lengthens; a highly individual stock like Ford showed the
  *opposite* — better with short periods because it lacks a persistent long-term trend.
  **The practical lesson: calculation-period selection needs per-instrument
  verification, not a single "long is always better" or "short is always better"
  heuristic** — directly reinforces this skill's existing overfitting-guard synthesis
  note (papers #3/#4) but from calculation-period selection rather than
  indicator-weight optimization.
- **Application guidance by system type** (source's own conclusion, not independently
  derived here): breakout systems suit intraday trading better; moving averages suit
  long-term trend; regression suits arbitrage/ranking applications. The regression
  system sits between MA and breakout on both risk and win-rate.

### Two- and three-trend combination systems

- **Crossover** (fast MA crosses slow MA) — always in market, reverses on every cross.
- **Price-vs-both-trendlines** — enter when price clears *both* averages, exit on
  either — creates a **neutral/flat zone** between signals, at the cost of some total
  profit for materially lower per-trade risk.
- **Both-trendlines-agree** (enter when fast and slow trend are both pointed the same
  way, exit when they diverge) — the highest-quality-filter variant: exits (rather than
  reverses) into flat, which **halves order size on every transition and adds
  liquidity/reduces slippage** — worth noting given this repo's own scripts trade
  MNQ/futures where slippage/fill quality on reversal orders matters.
- **Empirical result (Table 8.12, Eurodollar & e-mini S&P, 1991-2017)**: a 2-trend
  crossover **substantially improved the already-strongly-trending Eurodollar** (much
  smaller short-side losses, higher profit factor, far fewer trades) but **did not
  improve the noisier e-mini S&P** (20-day fast trend had large short-side losses; the
  combined system only marginally beat the single slow trend). Source's own conclusion:
  **"a 2-trend system improves an already-trending market, but not a noisy one"** — a
  directly quotable, falsifiable claim worth remembering before assuming any
  multi-confirmation architecture (including this repo's own CVD+VolumeTrend+regime
  hard-gate stack in `Regime_Engine_TCO_Gatekeeper.pine`) automatically helps on every
  instrument — it should be expected to help most on the cleanest trenders and least
  (or not at all) on the noisiest.
- **Adding a 3rd, fast (~3-day) confirming trend**: small, consistent improvement, more
  pronounced on the long side (Table 8.13) — a real but modest effect, not a
  transformative one.
- **4-9-18 crossover** (a once-popular "beat the 5-10-20 crowd" combo from the late
  1970s): explicitly tested on modern data and found only marginally profitable —
  **"none of the results would have convinced you to trade this."** Included as a
  documented negative result: a classic, once-famous parameter combination that no
  longer clears its own historical reputation once actually re-tested — a caution
  against porting "well-known" classic parameter sets into new scripts on reputation
  alone, matching this skill's recurring theme that publish/folklore fame ≠ tested edge.
- **Donchian 5-/20-day system** (one of the longest continuously-documented trading
  histories, from 1961): entry requires price to clear the 20-day MA **by more than the
  largest prior 1-day penetration** (a volatility-adjusted breakout-of-the-band
  condition, not a plain crossover), modernized here with an explicit ATR band:
  `buy: close_t > MA5_{t-1}+1×ATR_{t-1} AND close_t > MA20_{t-1}+1×ATR_{t-1}`
  (mirror for shorts/exits). **Position sizing formula given explicitly**:
  `Position size = investment / (ATR × Big Point Value)` — i.e. size inversely to
  current volatility so each position carries roughly equal dollar risk. **This is
  directly relevant to the zero-qty/margin-rejection bugs root-caused earlier this
  session** in `Trend_Following_Strategy_v6_Cooldown.pine` and
  `..._Signal_Cooldown_FIX.pine` (MNQ notional exceeding `percent_of_equity` sizing,
  rounding to 0 contracts) — an ATR-scaled fixed-risk sizing formula like this one is
  the textbook-correct fix class for that entire bug family, not just the
  `strategy.fixed`/`margin_long` patches actually applied — worth considering as a
  proper sizing upgrade in a future pass on those scripts.
- **Donchian 20-/40-day breakout**: `buy: today's high > 40-day high`,
  `sell: today's low < 20-day low` (asymmetric entry/exit lookback) — explicitly named
  as **the direct basis for the Turtles' trading method**.
- **Golden Cross / Death Cross** (50-day crosses 200-day): long history of avoiding
  major bear-market drawdowns (2008 among them); source's own empirical note worth
  remembering — **the largest drawdown in the tested SPY history came in 2014, not
  during the 2008 financial crisis** — a reminder that a system's stated purpose (avoid
  the big crash) doesn't guarantee it avoids the *next* significant drawdown, which can
  come from an unexpected period.
- **ROC method** (Woodshedder, cited): `buy: 5-day ROC < 252-day ROC for 2 consecutive
  days`; `exit: 5-day ROC > 252-day ROC for 2 consecutive days`; cash position earns
  T-bill yield when flat. **The "2 consecutive day" confirmation requirement is the
  same debounce/second-flip pattern** this skill's Cross-Paper Synthesis already
  connects to paper #6's provably-optimal hysteresis result and this repo's own
  `MTF_Second_Flip` naming — a third independent source converging on the same
  single-confirmation-is-not-enough principle.
- **"Staying ahead of the crowd"** (using an atypical period, e.g. 8/18 instead of the
  popular 10/20, to front-run other traders' order flow) and **replication** (tracking
  a target portfolio's daily returns without knowing its actual holdings/rules): both
  presented as real techniques but with no backtest evidence in this excerpt — **flagged
  here as unverified/speculative**, same treatment as the political-cycle claims in
  paper #8's reference file. Not a source of confirmed edge, just documented technique.
- **Ichimoku Cloud**: five-line system (Tenkan-sen, Kijun-sen, Senkou A/B forward-
  projected 26 periods, Chikou lagging span) — fully specified formulas given. Used as a
  long-term trend filter (cloud color = regime) with a faster reentry signal (Tenkan
  crossing Kijun) inside it — **structurally the same two-tier "slow regime filter +
  faster entry timing" pattern already used throughout this repo** (e.g. TCO's
  regime/bias gate plus its faster acceptance/CVD/volume-trend confirmations), just
  built from shifted/projected moving averages instead of a scored regime classifier.

### Trend-family confirmation (an underused technique worth flagging)

**Moving average sequences / signal progression**: compute the *same* signal
(up/down) across a whole family of calculation periods (e.g. every 5 days from 5 to 50)
and look at whether the transition from short to long periods flips **smoothly/
monotonically** (all periods up to some length agree, all above disagree) versus
**erratically** (alternating up/down as period increases). Source's stated rule of
thumb: an orderly, monotonic progression is a trustworthy trend change; an erratic one
is not, and for the fastest trend ranges specifically, it's better to wait for *all*
faster trends to agree before trusting the signal. **This is a genuinely portable,
not-yet-used-in-this-repo technique**: a "trend confluence count" — how many of N
different-length MAs currently agree on direction — is straightforward in Pine (a
`for` loop over N periods, tallying sign agreement) and would give TCO-style scripts a
continuous, cheap confirmation strength independent of the ADX/efficiency/DI logic
already used, worth prototyping if a future session wants a genuinely new confirmation
axis rather than another variant of the existing regime classifier.

### Early exits and early identification (qualitative techniques, weaker portability)

- **"Techno-fundamental" early exit**: exit a slow trend when the underlying
  *fundamental driver* changes (e.g. a central bank policy shift), even before the
  trendline itself reverses — because a very slow trend (200-day-equivalent lag) can
  give back a large, avoidable share of open profit waiting for the lagging average to
  catch up. Source's own explicit caveat undercuts the technique's reliability: a 2010
  worked example where "it seemed" Fed policy was about to change, followed by 2011
  posting a *strong* continuation of the old trend anyway — i.e. **this discretionary
  override is itself frequently wrong and cannot be honestly backtested** (you can't
  simulate "I correctly read the policy shift in advance" as a rule). Log as a
  documented, named technique with an admitted failure case, not a rule to encode.
- **Projecting moving average crossovers (CP2 formula)**: given two MA periods `m` and
  `n`, the exact future price `CP2` at which they will cross is computable in closed
  form from the sums of the most recent `m-1` and `n-1` prices:
  `CP2 = m × (Σ(most recent m-1 prices)/m − Σ(most recent n-1 prices)/n)`.
  **Directly portable to Pine** — pure arithmetic on rolling sums, no different from any
  running-total calculation already in this repo's scripts, and lets a script place a
  crossover order *before* the cross actually happens rather than reacting a bar late.
  The **Market Directional Indicator (MDI)**, Lambert (cited), extends this into an
  oscillator: `MDI = 100 × (CP2_previous − CP2_today) / avg(last 2 days' prices)`,
  read as a zero-line-cross momentum signal on the *projected* crossover itself.
- **Ehlers' quotient transform** (early trend identification): formula given —
  `Output = (Input+K)/(K×Input+1)`, `-1<K<1`, applied to any oscillator rescaled to
  [-1,+1] first — but the companion **roofing filter** and **automatic gain control
  (AGC)** steps that make Ehlers' actual "Early Onset Trend" indicator work are
  referenced, not specified, in this excerpt. **Portability gap, same shape as paper
  #8's Fourier/MESA gap** — flagged rather than guessed at; if Ehlers' own published
  roofing-filter/AGC formulas are ever supplied (or a verified existing Pine port is
  found), this indicator becomes directly implementable, but not from what's here.

## Pitfalls (explicit in the source, or evident from it)

- **A high win rate is not automatically better** — it usually trades off against a
  materially worse risk/drawdown profile (breakout systems: 50-70% win rate but among
  the largest max drawdowns in every comparison table shown).
- **The best single-trend system genuinely differs by instrument**, confirmed with real
  multi-market data, not asserted — there is no universally-best trend method to
  default to; per-instrument testing is not optional.
- **A famous/classic parameter combination (4-9-18) failed a direct modern retest** —
  fame or historical popularity is not evidence.
- **Multi-trend confirmation stacking helps trending markets and doesn't reliably help
  noisy ones** — demonstrated with a real head-to-head result, not assumed.
- **"Ahead of the crowd" positioning and portfolio replication are asserted, not
  backtested**, in this excerpt — treat as technique, not confirmed edge.
- **A discretionary fundamental override (techno-fundamental exits) is explicitly shown
  failing** in its own worked example (the 2010→2011 Fed case) — a documented,
  named failure mode for any rule that requires "reading" a policy change in real time.

## Portability

Almost everything in this chapter is directly Pine-portable — a rarity in this skill,
where most sources have at least one hard ML/statistics barrier. The exceptions:

| Technique | Portable to Pine? | Notes |
|---|---|---|
| All band/channel constructions (Keltner, %, ATR/stdev-scaled, Bollinger, Modified Bollinger) | ✅ Direct | Pure arithmetic/recursive smoothing, same primitives already used throughout this repo |
| TRIX, MPTDI, Volatility System, 10-Day Rule | ✅ Direct | Fully specified, simple recursions/comparisons |
| All single/multi-trend crossover systems (M, MA, EXP, BO, SWG, LRS, Donchian variants, Golden/Death Cross, ROC) | ✅ Direct | `ta.sma`/`ta.ema`/`ta.highest`/`ta.lowest`/`ta.linreg` cover essentially all of it |
| ATR-scaled position sizing (`investment / (ATR × BigPointValue)`) | ✅ Direct | Straightforward `strategy.entry(qty=...)` computation — relevant fix class for this session's earlier zero-qty sizing bugs |
| Moving-average-family confluence count | ✅ Direct | A `for` loop over N periods; genuinely new technique for this repo, not yet used anywhere |
| CP2 projected-crossover price, MDI oscillator | ✅ Direct | Closed-form arithmetic on rolling price sums |
| Ichimoku Cloud | ✅ Direct | Forward-offset plots are a standard Pine pattern (`offset=` parameter) |
| "Ahead of the crowd" / replication | ⚠️ Codeable but unverified | No barrier to implementing, but the source gives no evidence it works — build only as a documented experiment, not a trusted technique |
| Techno-fundamental discretionary exit | ❌ Not systematizable | By definition requires real-time discretionary judgment about *why* a trend is happening, not just its price behavior — cannot be honestly backtested or encoded as a rule |
| Ehlers' full Early Onset Trend (quotient transform + roofing filter + AGC) | ⚠️ Partial | The quotient transform alone is portable; roofing filter/AGC formulas aren't in this excerpt |

## Mapping to This Repo

- **Several ideas here are things this repo already independently arrived at** —
  worth naming as convergent validation, not new information to add: the Bollinger
  squeeze ≈ `isSqueeze`/`WAIT BREAKOUT` in `Regime_Engine_TCO_Gatekeeper.pine`;
  MPTDI's regime-conditional parameters ≈ `riskMode` varying by `regime`; the
  ROC method's 2-consecutive-bar confirmation ≈ this repo's `MTF_Second_Flip` naming
  and paper #6's hysteresis result; Ichimoku's slow-filter-plus-fast-entry structure ≈
  TCO's regime/bias gate plus CVD/volume-trend confirmations.
- **The ATR-scaled position sizing formula is a concrete candidate fix** for the
  zero-qty/margin-rejection bug family root-caused earlier this session in
  `Trend_Following_Strategy_v6_Cooldown.pine` and
  `Trend_Following_Strategy_v6_Signal_Cooldown_FIX.pine` — those were patched with
  `margin_long`/`margin_short` and `strategy.fixed` respectively, which fix the
  immediate symptom (0 contracts) but don't give risk-proportional sizing the way
  `investment / (ATR × BigPointValue)` would. Worth a dedicated pass if the user wants
  proper volatility-adjusted position sizing rather than a fixed contract count.
- **Moving-average-family confluence (monotonic MA-fan agreement) is a genuinely new,
  not-yet-built confirmation axis** for `Regime_Engine_TCO_Gatekeeper.pine` — distinct
  from ADX/DI/efficiency (which measure trend *strength*) and from CVD/Volume Trend
  (which measure *participation*) — this measures whether the trend read is *consistent
  across timeframes/speeds* rather than just strong at one specific speed. A candidate
  for a future module if the user wants another independent gate rather than tuning
  existing ones further.
- **The Modified Bollinger center-line/deviation formulas are a ready-made, fully
  specified upgrade** if a future session wants volatility bands anywhere in this
  repo's scripts that don't suffer the standard Bollinger "slow to narrow" lag — the
  formulas are copy-portable as given.
- **The "2-trend system helps trending markets, not noisy ones" finding is a caution
  worth remembering specifically for the TCO engine's own multi-gate architecture**
  (CVD confirms + Volume Trend confirms + regime + bias, all AND'd together): expect
  the accumulating hard gates to help most on cleanly trending instruments and to mostly
  just suppress signal count (not necessarily improve win rate) on genuinely noisy
  ones — worth checking empirically per-instrument in `quantor` rather than assuming
  more gates is strictly better everywhere, the same overfitting-guard lesson this
  skill already carries from papers #3/#4, now confirmed from a completely different,
  much simpler empirical source.

## Applied in This Repo

**2026-08-31** — Built `Kaufman_Trend_System_Swing.pine`, a new standalone daily/swing
strategy implementing most of this chapter directly: selectable trend engine
(SMA/EMA/Linear Regression) with optional 2-trend confirmation (enter on agreement,
exit to flat on conflict); ATR/volatility or Modified Bollinger bands with an optional
band-clear entry requirement; three entry-timing styles (Immediate, Delay N Bars, ATR
Retracement-or-Timeout) as a pending-order state machine, with exits always immediate;
the ATR-scaled position-sizing formula (`investment / (ATR × Big Point Value)`) via
`syminfo.pointvalue`, applied as the properly-designed fix class for the zero-qty
sizing bugs root-caused earlier in the Trend Following Strategy v6 files; and
display-only readouts for the anticipated single-trend flip price, a self-derived
(not literally transcribed — see the CP2 note below) projected 2-trend crossover price
and MDI oscillator, and the MA-family confluence count. No profit target of any kind,
per this chapter's own explicit fat-tail-capture warning; only an optional, off-by-
default wide catastrophic stop.

**Known residual uncertainty**: the CP2 projected-crossover formula was re-derived
algebraically from the equal-average condition rather than transcribed literally from
the source excerpt, because the OCR/vision-extracted text of Kaufman's own printed
formula did not algebraically reduce to a consistent result on manual re-derivation —
flagged as a transcription-fidelity risk in the source, not a error in the arithmetic
used here. The implemented formula is independently verified correct for what it's
solving (the price at which two moving averages of period m and n will next be equal);
if exact agreement with Kaufman's own notation matters, check it against the physical
text.

**Not yet applied**: this build is not compiler-verified (no live Pine editor access
in this environment) — validated only via this session's established static-analysis
suite (bracket/paren balance, tabs, single strategy() declaration, ternary-nesting
depth, duplicate/unused variables, dashboard row-count match) and a manual review pass.
Flag any compile error back to this session the same way prior scripts' errors were
resolved this session.
