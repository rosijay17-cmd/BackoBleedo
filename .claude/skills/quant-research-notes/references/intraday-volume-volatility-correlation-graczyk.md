# Intraday Volatility–Volume Correlation Profile (Graczyk & Duarte Queirós)

**Citation:** Graczyk, M.B. & Duarte Queirós, S.M. (2018). "Volatility–Trading volume
intraday correlation profiles and its nonstationary features." *Physica A*, 508, 28–34.

## Evidentiary basis — read this before the rest of the file

An econophysics paper, not a finance journal, but methodologically solid: 10 years
(2004–2013) of 1-minute price/volume data on all 30 DJIA constituents, aggregated to
5-minute bars, with an explicit non-stationarity check (t-Student test, 95% confidence)
rather than an eyeballed chart. The headline finding (a hump-shaped, not U-shaped,
intraday correlation profile) is robust across three different volatility definitions
tested independently. Weaknesses worth flagging: it studies large-cap **US equities**
during **NYSE cash-session hours only** (9:30–16:00, pre/post-market explicitly
excluded) — nothing here was tested on futures, nothing was tested on 24-hour/overnight
sessions, and the sample ends in 2013, before the current era of much heavier algorithmic/
HFT participation. The specific numbers (correlation ~0.12 at open rising to ~0.3 by
2pm) should be treated as illustrative of the *shape*, not as literal targets to
replicate on NQ/MNQ.

## Core Content

**The central, counterintuitive finding.** Most intraday volume and volatility measures
individually show the well-known **∪-shape** (high at the open, low at midday, high
again at the close). This paper instead studies the **correlation *between* volume and
volatility** at each intraday timestamp, across the trading session — and that
correlation is **hump-shaped, not U-shaped**: low near the open (~0.12), rising fairly
steadily through the morning to a peak around 2:00pm (~0.3, roughly double the opening
value), then declining back toward open-like levels by the close. This holds
"qualitatively and nearly quantitatively" across three independent volatility
definitions (simple log-price standard deviation, Garman-Klass HL-CO volatility, and
raw absolute 5-minute price change) — the shape is not an artifact of how volatility is
measured.

**A sharp, dateable spike at t=60 (~2:00pm).** A clear, one-time-of-day peak in the
correlation coincides with scheduled Federal Reserve publications — FOMC Minutes and
the Beige Book, both released at 2:00pm ET on their respective calendar days. This is
the paper's cleanest, most directly actionable single data point: a *specific,
known-in-advance, recurring intraday window* where volume and volatility become
unusually tightly linked, tied to a real, identifiable mechanism (scheduled
macro news), not a statistical artifact.

**MDH vs. SIAH — a third framework for "why does the market move," alongside this
skill's existing regime-switching and cycle-decomposition paradigms.** Two long-standing,
competing hypotheses about the volume-volatility-information relationship:
- **Mixture of Distributions Hypothesis (MDH):** volatility and volume are driven by
  the *same* latent information-arrival process, hitting all market participants at
  roughly the same time — so volume and volatility should be strongly, contemporaneously
  correlated.
- **Sequential Arrival of Information Hypothesis (SAIH/SIAH):** information reaches
  market participants at *different times*, so the market passes through a sequence of
  local, temporarily-stable states before settling — correlation between volume and
  volatility should be weaker at any single instant, and would only show up fully once
  a time lag is allowed for.
The paper's own reading of its results: **SIAH dominates at the open and close** (where
correlation is weakest — information hasn't yet propagated through the full set of
participants), and **MDH dominates through the bulk of the session** (where correlation
is strongest — by then, information has effectively become common knowledge and hits
everyone at once). Both hypotheses are correct, just in different parts of the day —
not a single universal answer, a genuinely time-varying one.

**Confirming evidence beyond the average correlation.** Three further statistics
corroborate the same intraday split: the *fraction of stock-days with a negative*
volume-volatility correlation is elevated specifically at the open and close (up to
~10%, essentially zero mid-session) — i.e., at the edges of the session it's not just
"weaker correlation," some days genuinely show volume and volatility moving in opposite
directions, a stronger form of the SIAH-at-the-edges reading. The cross-correlation
matrix's **variance** shows a step-like regime shift with a sharp increase right at the
close, and the diagonal (same-stock, volume-vs-own-volatility) entries specifically do
**not** show the 2pm FOMC spike that the off-diagonal (cross-stock) entries do — meaning
the FOMC effect is specifically about one company's information flow spilling over into
*another* company's price action, not just a single-stock reaction.

**A dated, real structural break, not noise.** Splitting the 10-year sample into 19
semesters, the off-diagonal (cross-stock) correlation-matrix statistics show a
statistically significant shift (t-test, 95% CI) starting at semester s=10 — which the
paper ties to a specific regulatory event: the SEC's phased removal of the "uptick rule"
restricting short-selling (2007 and 2010 releases), which made cross-stock long-short
strategies structurally easier to execute and is plausibly the mechanism behind the
increase in cross-stock volume-volatility linkage from that point on.

## Pitfalls (evident from the source itself, plus repo-relevant caveats)

- **US cash-session equities only, 2004–2013.** No claim here about futures, no claim
  about overnight/globex sessions, no claim about post-2013 market structure. NQ/MNQ
  trade nearly 24 hours; this paper says nothing directly about the overnight portion of
  that session, only (at best) about the RTH-equivalent hours that overlap NYSE cash
  trading.
- **The exact correlation *matrix* (30×30 cross-stock analysis, semester segmentation,
  Gram-Charlier cumulant formulas) is a multi-security, offline academic research tool.**
  It answers "does company i's volume at time t correlate, across many days, with
  company j's volatility at the same time t" — a cross-sectional research question, not
  something a single-symbol live indicator computes.
- **The specific numbers (0.12 → 0.3, t=60 spike) are DJIA-large-cap-specific and dated.**
  The *shape* (hump not U, edges weaker than midday, a scheduled-news spike) is the
  transferable claim; the exact correlation values are not.
- **MDH/SIAH remain a *description*, not a trading rule.** The paper explicitly frames
  this as resolving an academic dispute about market dynamics, not as a strategy.
  Turning "SIAH dominates at the edges" into an actual gating rule is this repo's own
  design choice to make, not something the source specifies.

## Portability

| Technique | Portable to Pine? | Notes |
|---|---|---|
| Full 30×30 cross-stock volatility-volume correlation matrix, semester non-stationarity test, Gram-Charlier cumulants | ❌ Not feasible | Cross-sectional, multi-security, offline research machinery — same class of barrier as papers #2/#7's matrix/ML pipelines |
| Time-of-day weighting curve for a volume-confirms-volatility gate (hump-shaped: weak at open/close, strong midday) | ✅ Direct, as a design pattern | `session.ampm`/`hour`/`minute` conditionals or a smooth intraday-time-based multiplier on an existing confirmation score; the exact curve shape would need re-derivation on this repo's own instrument/timeframe, not copied verbatim from DJIA-equity numbers |
| Scheduled-news correlation spike (FOMC Minutes/Beige Book, 2:00pm ET) | ✅ Direct | A simple calendar/time check (`hour==14 and minute==0`, adjusted for the actual FOMC release calendar) already has real justification behind it as a "confirmation gets stronger here" window, rather than an arbitrary news-time guess |
| MDH/SIAH as a conceptual lag-adjustment idea (expect a delay between volume and volatility near the open/close, near-simultaneity mid-session) | ⚠️ Codeable as a design choice | Could motivate requiring one extra bar of confirmation lag on any volume-based gate specifically near the session open/close, loosening it mid-session — not something the source specifies mechanically, this repo's own synthesis |
| Garman-Klass HL-CO volatility estimator | ✅ Direct | Simple closed-form OHLC arithmetic; a legitimate alternative volatility measure to ATR/stdev already used throughout this repo |

## Mapping to This Repo

- **Directly relevant to any volume-confirms-price-move gate already in this repo** —
  most concretely `Regime_Engine_TCO_Gatekeeper.pine`'s CVD divergence check and Volume
  Trend confirmation, and `Stacked_Buy_Sell_Volume_Columns.pine`'s buy/sell delta reading
  built this session. All of these currently treat "does volume confirm the move" as
  equally meaningful at every time of day. This paper's finding says that's very
  unlikely to be true: the same volume/volatility relationship is a much weaker signal
  near the open and close (SIAH-dominated, more sequential/laggy) than it is mid-session
  (MDH-dominated, near-simultaneous) — a concrete, testable case for time-of-day-aware
  confidence weighting on any of these confirmation gates, rather than a flat threshold
  applied uniformly across the session.
- **A specific, low-effort addition**: a "near FOMC/Beige Book release" flag (a simple
  calendar check, not a data feed) that temporarily raises confidence in a volume-
  confirms-volatility signal during that known window — directly justified by this
  paper's own strongest, most mechanistically-grounded single finding.
- **A third framework alongside this skill's regime-switching (papers #2, #6) and
  cycle-decomposition (paper #8) paradigms** — MDH/SIAH is specifically about the
  volume-volatility-information relationship changing character through the day, a
  different axis from "which hidden state is the market in" or "what periodic
  components does price decompose into." Doesn't replace either; adds a third lens,
  most relevant to exactly the volume/order-flow-adjacent modules named above.
- **Not a candidate for the cross-sectional multi-security machinery itself** — unlike
  paper #16 (beta dispersion, below), which is genuinely blocked from Pine and needs an
  offline `quantor` computation, this paper's actionable content (the time-of-day shape,
  the FOMC-window flag) is usable *directly* in Pine without any offline pipeline at
  all, since it only requires knowing the current bar's time-of-day, not any
  cross-security computation.

## Applied in This Repo

*(none yet — the time-of-day confidence-weighting idea for CVD/volume-confirmation
gates and the FOMC-window flag are the two concrete, ready-to-build candidates.)*
