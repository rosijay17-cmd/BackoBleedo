# Candlestick Patterns & Pivot-Point Confluence (Person, *A Complete Guide to Technical Trading Tactics*, Ch. 4 & 6)

**Citation:** Person, J. L. (2004). "Candle Charts: Lighting the Path" (Chapter 4) and
"Pivot Point Analysis: A Powerful Weapon" (Chapter 6). *A Complete Guide to Technical
Trading Tactics: How to Profit Using Pivot Points, Candlesticks, and Other Indicators*.
John Wiley & Sons.

## Evidentiary basis

Same category as paper #10 (Scheier) — a practitioner's book illustrated with
individually-selected worked chart examples (sugar, live cattle, S&P 500, silver, the
U.S. Dollar Index, crude oil, cotton), not a systematic study. There are more
worked examples here than in paper #10's single 39-gap sample, but they're still the
author's own chosen illustrations of a method he's advocating, not an out-of-sample or
random test — expect selection bias toward cases where the method worked. Logged for
the same reason as paper #10: several of the techniques are precise and mechanically
testable regardless of the author's own evidentiary standard, and one part of this
source (the Floor Trader's Pivot Point formula and its all-session-vs-day-only
pitfall) independently overlaps with paper #10 almost word for word, from a source
predating it by a decade — see Overlap note below.

## Overlap with paper #10 — read this first

This source and Scheier (2014, paper #10) both describe the **same Floor Trader's
Pivot Point formula** and the **same all-session-vs-day-only session-range pitfall**
(pivot inputs should come from the full/all-session H/L/C even when the resulting
levels are applied to a day-only chart). Rather than re-deriving that content here,
see `references/pivot-exhaustion-grid-scheier.md`'s "Floor Trader's Pivot Points"
section for the full formula and pitfall writeup. This file only adds what's new on
top of that: the specific derivative-support/resistance formulas (below, since they
weren't fully spelled out in paper #10), and several techniques paper #10 does not
cover at all (candlestick patterns, multi-timeframe pivot confluence, the "first test
only" fade rule, and the three-gap-formation signal).

**Floor Trader's Pivot Point formulas** (the one piece worth stating precisely, since
paper #10 named the concept without giving every derived level):
```
P  = (H + L + C) / 3
R1 = (P × 2) − L
R2 = (P + H) − L
S1 = (P × 2) − H
S2 = (P − H) + L
```
`H`, `L`, `C` are the prior period's high, low, close (day/week/month, per the
calculation horizon chosen). The author explicitly rejects a variant some traders use
that adds the *open* and divides by four, on the grounds that it's an unnecessary
extra input and the point of the formula is the close's weight relative to the
high/low range specifically.

## New Techniques (beyond paper #10)

**Multi-timeframe pivot confluence.** When the pivot levels computed on two different
horizons (e.g., the weekly S1 and the monthly S1) land close to each other, that
convergence itself is treated as a stronger signal warranting closer attention — not
because either level alone is more reliable, but because two independently-derived
support/resistance estimates agreeing is read as extra confirmation. Worked example:
July cotton, weekly S1 = 32.35¢ and monthly S1 = 32.61¢ (26¢ apart) — the actual low
that followed (33.05¢) landed between the two, and the author explicitly frames the
proximity of the two numbers as *why* he flagged the trade in advance in a published
newsletter recommendation, not after the fact. A precise, easily portable technique:
compute pivot S1/R1 (or S2/R2) on two different calculation horizons and flag when
they fall within some tolerance of each other.

**"First test only" pivot-fade rule.** An explicit risk-management/entry-frequency
rule for trading off a specific pivot level: **only take a trade on the *first* test**
of a given S1 or R1 number within its period, not the second, third, or fourth time
price returns to it. The author's stated reasoning is an "well runs dry" analogy — by
the time a level has been tested and held multiple times, other traders have adapted
to the pattern, and the level is more likely to finally break rather than hold again.
This is a falsifiable, mechanically simple filter: track how many times a level has
already been tested this period and gate entries on `testCount == 1`.

**Three-gap-formation exhaustion signal.** A sequence-based read on daily gaps: a
**breakaway gap** (the initial gap that starts a strong directional move), followed
later by a **midpoint gap** (roughly mid-trend), followed by an **exhaustion gap**
(the trend's last gasp, often into the terminal move) is read as high-confidence
evidence the move is nearly over — combined, in the author's sugar futures example,
with a monthly pivot S1 target that the market reached almost exactly (target 6.09,
actual low 6.11, two ticks off) two days after the exhaustion gap. Distinct from — but
in the same conceptual family as — paper #10's Break-Away Lap/Gap-Close material;
cross-reference both files if building any gap-based feature.

**"Eight to ten new records" exhaustion counter.** Counting consecutive new highs (in
an uptrend) or new lows (in a downtrend) as a session-independent exhaustion clock:
when the 8th–10th consecutive new extreme occurs together with a reversal-type candle
(hammer, doji) within a bar or two, that combination is read as a probable turning
point. Worked weekly-U.S.-Dollar-Index example: nine consecutive weekly higher highs,
the ninth made by a doji, followed by a ~950-point decline over the following months.
Mechanically simple to implement as a running streak counter (`ta.highest`/`ta.lowest`
comparison chain) combined with a candle-pattern check at the streak's 8th-10th bar.

**"Pillar of strength / weakness"** — a refinement of a standard bullish/bearish
engulfing pattern: the more prior candles a single engulfing candle's real body
consumes, the stronger the reversal signal (worked example: one candle engulfing
three prior candles and closing at the midpoint of a fourth). Two tiered
support/resistance targets follow from the "pillar" candle itself once it forms: its
**midpoint** is the first target/support level, and its **opening price** is the
second, more significant "last line of defense" level. A precise, portable
refinement of the standard engulfing-pattern boolean — instead of a single
prior-candle comparison, count how many consecutive prior candles' full range the
current candle's body consumes.

**Sklarew's "Rule of Multiple Techniques" (cited by the author as the philosophical
basis for combining pivot points + candle patterns + a momentum oscillator into what
he calls a "P3T signal")**: *"the chart technician [should] not rely solely on one
single technical signal or indicator but look for confirmation from other technical
indicators. The more indicators that confirm each other, the better the chance of an
accurate forecast."* This is the explicit, named justification (from Sklarew, 1980,
via Person) for exactly the confluence-gate architecture already used throughout this
repo's own scripts — worth having as a citable source for that design philosophy
rather than treating it as this repo's own invention. The author's own **P3T
signal** — Person's Pivot Point Trade signal — is literally this pattern applied
concretely: a pivot-level target reached, *plus* a recognizable candle pattern at that
level, *plus* a confirming Western indicator (stochastics or MACD divergence/
crossover) — a three-part AND-gate, structurally identical in shape to this repo's own
regime + bias + order-flow gating.

## Candlestick Pattern Catalog

Standard Japanese candlestick vocabulary, as defined in this chapter (colors: a filled
"black"/dark body means close below open; a hollow/white body means close above open —
the color, per the author, is *not* what matters in most of these patterns, only the
body/shadow geometry):

**Single-candle patterns**
- **Hammer** (bottom reversal): body at the upper end of the day's range; lower shadow
  ≥2× the body length; little/no upper shadow. Same geometry at a top is a
  **hanging man** instead (context — prior trend direction — determines which name
  and which implication applies, not the candle shape itself).
- **Star / shooting star** (top reversal): body at the *lower* end of the range with a
  long *upper* shadow, little/no lower shadow — a failed rally that closed back near
  the day's low. The same shape at a bottom is an **inverted hammer** — explicitly
  flagged by the author as "not a tremendously reliable" standalone bottom signal;
  needs a confirming white candle opening above its body on the next bar.
- **Spinning top**: small real body with small upper *and* lower shadows on both
  sides — indicates a tug-of-war, not a directional signal by itself.
- **Doji**: open ≈ close (negligible real body). Signals indecision; more powerful as
  a reversal warning after a long prior trend candle than as a standalone signal.
  Named sub-variants by shadow shape: **gravestone** (long upper shadow, no/tiny lower
  shadow — bearish-context), **dragonfly** (long lower shadow, no/tiny upper shadow —
  bullish-context), **rickshaw** (long shadows on both sides, body dead-center).

**Two-candle patterns**
- **Bullish/bearish engulfing**: second candle's real body completely covers the
  first candle's real body (open beyond the first's close-or-open and close beyond
  the first's open-or-close, in the trend-reversing direction). See "Pillar of
  strength/weakness" above for the multi-candle-consuming refinement.
- **Dark cloud cover** (bearish, after an uptrend): a black candle opens *above* the
  prior white candle's high, then closes *below* the midpoint of that white candle's
  real body.
- **Piercing pattern** (bullish, after a downtrend) — the mirror image: a white candle
  gaps open *below* the prior black candle's close, then closes *above* the midpoint
  of that black candle's real body.
- **Harami**: a small second real body entirely contained within the first candle's
  real body (opposite of engulfing). More reliable, per the author, when the two
  bodies are opposite colors. A **harami cross** is the harami variant where the
  second candle is a doji instead of a small spinning-top-like body — described as
  rarer and a more powerful reversal signal than a standard harami.
- **Shooting star** is itself sometimes described as a 2-candle setup when the prior
  candle is a tall white/hollow body the star gaps above — see "Reading Candle
  Charts" worked examples.

**Three-candle patterns**
- **Evening star** (major top, bearish): tall white/hollow candle → small real body
  (white or black; a doji here is read as even more bearish) that gaps *higher* →
  black candle that closes well into the first candle's real body.
- **Morning star** (major bottom, bullish) — the mirror image: long black candle →
  small real body gapping *lower* → white candle closing well above the first
  candle's midpoint.
- **Abandon baby**: an extremely rare, very potent variant of the evening/morning
  star where the middle candle is a doji that gaps away from *both* neighboring
  candles (an island reversal made of candles) — described as one of the strongest,
  though rarest, of all the patterns in this catalog.

**Continuation patterns** (trend *resumes*, not reverses)
- **Three crows**: three consecutive longer-than-normal candles each closing at or
  near their own lows — a potential top signal after an extended uptrend (a bearish
  continuation/exhaustion-of-the-rally pattern, despite superficially looking like
  three separate down bars).
- **Three white soldiers / advancing three**: the bullish mirror — three consecutive
  candles advancing from a bottom, a sign of strengthening upside continuation.
- **Bearish falling three (methods)**: one long black candle → three small candles
  drifting higher but staying within the first candle's range → a final long black
  candle closing below the first black candle's close. Reads like a bear flag on a
  bar chart; signals the downtrend continuing.
- **Bullish rising three (methods)** — the mirror image, reading like a bull flag;
  signals the uptrend continuing. Worked weekly bond example: a rising-three pattern
  that projected (like a flag's measured move) to 108, and price reached 108-plus in
  the following months.

## Pitfalls

- **The author's own worked examples are close-but-not-exact in nearly every case**
  (target 6.09 vs. actual 6.11; target 75.94 vs. actual 76.05; target $4.7737 vs.
  actual $4.775; target 120.98 vs. actual 120.88; target $27.54 vs. actual $27.69) —
  the author frames each as impressively close, but the recurring pattern of
  "close but not exact, margin of a few ticks to a few points" across every single
  example is itself worth noting: read these pivot-target hits as approximate zones
  to watch, never as precise price predictions, consistent with the author's own
  explicit caveat ("not an exact science... allow for a margin of error").
- **Candle patterns are explicitly stated by the author to need external confirmation**
  — "candle chart analysis is not an exact science. It is always necessary to
  validate signals and chart patterns manually... incorporating other techniques."
  None of the candlestick patterns above are presented as standalone, sufficient
  trading signals even by their own author.
- **The book predates modern Pine-style backtesting entirely (2004)** — every example
  is a single annotated historical chart chosen to illustrate the concept, with no
  aggregate hit-rate, sample size, or out-of-sample claim anywhere in either chapter.

## Portability

| Technique | Portable to Pine? | Notes |
|---|---|---|
| Full candlestick pattern catalog (hammer/star/doji variants/engulfing/harami/dark cloud/piercing/three-candle patterns/three crows/soldiers/rising-falling three) | ✅ Direct | Every pattern is defined purely in terms of `open`/`high`/`low`/`close` and their history (`[1]`, `[2]`) — no exotic infrastructure needed at all. The most cleanly portable content in this skill so far. |
| Floor Trader's Pivot Point formula (P/R1/R2/S1/S2) | ✅ Direct | Already covered in paper #10; same formula |
| Multi-timeframe pivot confluence (weekly vs. monthly levels agreeing) | ✅ Direct | Compute both, compare with a tolerance band — trivial once the base pivot formula exists |
| "First test only" pivot-fade rule | ✅ Direct | A per-period test-count tracker on a given level |
| "Eight to ten new records" exhaustion counter | ✅ Direct | A consecutive-new-extreme streak counter plus a candle-pattern check |
| "Pillar of strength/weakness" (multi-candle-consuming engulfing) | ✅ Direct | Count how many consecutive prior candles' full range the current body consumes, instead of just comparing to one prior candle |
| Three-gap-formation exhaustion read | ✅ Direct (the mechanic) / ⚠️ Unvalidated (the edge) | Detecting and sequencing gaps is trivial; whether the specific breakaway→midpoint→exhaustion sequence has real predictive value needs a proper backtest |
| P3T signal (pivot + candle + oscillator confluence) | ✅ Direct as an architecture pattern | Not a single formula — it's a design pattern (AND-gate across three signal types) already used throughout this repo |

## Mapping to This Repo

- **The candlestick pattern catalog is a genuinely new, high-value, and unusually
  cleanly-portable addition** — as far as this ingestion pass can tell, none of this
  repo's scripts implement formal candlestick-pattern recognition (hammer, engulfing,
  harami, doji variants, morning/evening star, three-method continuation patterns) as
  boolean conditions, despite several scripts (`Regime_Engine_TCO_Gatekeeper.pine`,
  the various ORB and liquidity-sweep scripts) already tracking regime/bias/order-flow
  confirmation that a candle-pattern module could sit alongside as one more
  independent confirmation axis, in the same architectural slot as CVD or Volume
  Trend. A strong candidate for a genuinely new module if the user wants one.
- **Sklarew's Rule of Multiple Techniques, cited here from 1980, is the earliest,
  most explicit statement of the confluence philosophy this repo's entire TCO
  Gatekeeper architecture already embodies** (regime + bias + acceptance score + CVD
  confirms + volume trend confirms, all AND'd together before an entry is called
  tradeable) — worth having as a named, citable precedent for that design choice
  rather than treating it as an ad hoc decision made this session.
- **Multi-timeframe pivot confluence and the "first test only" fade rule are
  concrete, well-specified techniques with no current analogue in this repo** — if
  the user ever wants a pivot-point module (none currently exists in the scripts
  reviewed this session), both should be built in from the start rather than added
  later, since they're cheap, mechanical, and directly address two of pivot trading's
  most commonly cited failure modes (trading a stale, already-tested level; trusting
  a single-timeframe number that happens to be noise).
- **The three-gap-formation signal adds a specific, sequenced variant to the gap
  concepts already logged in paper #10** (Break-Away Lap, Gap-Close) — if a gap-based
  module is ever built, check both files together rather than just one.

## Applied in This Repo

*(none yet — the candlestick pattern catalog and the two pivot-confluence rules
(multi-timeframe agreement, first-test-only) are the standout candidates; note here if
either is prototyped.)*
