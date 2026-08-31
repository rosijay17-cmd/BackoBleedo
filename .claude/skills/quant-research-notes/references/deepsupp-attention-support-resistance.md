# DeepSupp: Attention-Driven Correlation Pattern Support/Resistance Detection

**Citation:** Kriuk, B., Ng, L., & Al Hossain, Z. (2025). "DeepSupp: Attention-Driven
Correlation Pattern Analysis for Dynamic Time Series Support and Resistance Levels
Identification." arXiv:2507.01971v1 [q-fin.ST].

**Data:** S&P 500 tickers, 2-year historical price/volume history. Compared against six
baselines: Hidden Markov Models (HMM), Local Minima detection, Fractal analysis,
Fibonacci retracement, Moving Average analysis, Quantile Regression.

## Core Methodology (4 stages)

**Stage 1 — Feature engineering.** From raw OHLCV, build a 5-feature vector per bar:
`[Close, VWAP, Volume, PriceChangeVolume, VolumeRatio]`, MinMax-scaled.
- `VWAP_t = Σ(P_i·V_i) / ΣV_i`
- `PriceChangeVolume_t = ((P_t - P_{t-1}) / P_{t-1}) · V_t` — volume-weighted price
  change, meant to capture "conviction" behind a move.
- `VolumeRatio_t = V_t / (20-bar average volume)` — the same construct this repo already
  calls RVOL.

**Stage 2 — Dynamic correlation analysis.** Rolling Spearman rank correlation
(`ρ = 1 - 6Σd²/(n(n²-1))`, window `n=32`) across the 5 features, producing a sequence of
32×32 correlation-matrix snapshots (padded/trimmed to constant size) that feed the
attention stage. Deliberately non-static — correlations are allowed to evolve bar to
bar rather than being estimated once over the whole sample.

**Stage 3 — Multi-head attention autoencoder.** A 4-head attention mechanism processes
each 32×32 correlation matrix (permutation-invariant by construction — exploits that a
correlation matrix's meaning doesn't depend on feature ordering), with scaled
dot-product attention, residual connections, and layer norm. An encoder (two linear+ReLU
layers) compresses 32→16 dims; a mirrored decoder reconstructs the original matrix
(standard autoencoder training objective).

**Stage 4 — Clustering-based level extraction.** DBSCAN (`ε=0.1`, min_samples = 10% of
dataset size) clusters the 16-dim embeddings from the trained encoder's bottleneck. Each
cluster's price levels are mapped back to the original series; the **median** price
within each cluster (chosen over the mean for outlier robustness) becomes one support
level. DBSCAN's density-based design means the number of levels is discovered
automatically, not pre-specified.

## Reported Results (Table 1, this paper's own numbers)

| Method | Overall (weighted) | Support Accuracy (25%) | Price Proximity (20%) | Volume Confirmation (20%) | Market Regime (15%) | Support Duration (15%) | Breakout Recovery (5%) |
|---|---|---|---|---|---|---|---|
| DeepSupp | **0.554 ± 0.039** | 0.483 | 0.759 | 0.349 | 0.299 | 0.846 | 0.800 |
| HMM | 0.550 ± 0.044 | 0.408 | **0.826** | 0.348 | 0.299 | **0.859** | 0.800 |
| Local Minima | 0.507 ± 0.048 | **0.603** | 0.362 | **0.351** | 0.299 | 0.857 | 0.800 |
| Fractal | 0.478 ± 0.049 | 0.583 | 0.262 | 0.350 | 0.299 | 0.831 | 0.800 |
| Fibonacci | 0.449 ± 0.044 | 0.570 | 0.137 | 0.349 | 0.299 | 0.832 | 0.800 |
| Moving Average | 0.385 ± 0.081 | 0.311 | 0.168 | 0.349 | 0.297 | 0.796 | 0.800 |
| Quantile Regression | 0.336 ± 0.147 | 0.197 | 0.182 | 0.301 | 0.297 | 0.744 | 0.684 |

DeepSupp's stated advantage is winning the **weighted composite** with the **lowest
variance**, not winning any individual category — the paper is explicit about this
("While not achieving the top score in every individual category, DeepSupp
demonstrates exceptional consistency...").

## Independent Critique (not flagged by the authors)

Reading Table 1 directly, rather than taking the composite-score framing at face value,
raises three concerns the paper does not address:

- **Three of six metrics barely discriminate between ANY of the seven methods tested.**
  Volume Confirmation: six of seven methods (including trivial ones — Fibonacci, Moving
  Average) score within **0.349-0.351**, a spread of 0.002. Market Regime Sensitivity:
  **all seven** methods score within **0.297-0.299**, a spread of 0.002. Breakout
  Recovery: **six of seven** methods score an identical **0.800** to three decimal
  places — a genuinely implausible coincidence across structurally very different
  methods (a trained neural clustering pipeline scoring *exactly* the same as a plain
  moving average) unless the metric is measuring something close to constant across
  methods, or saturating. These three metrics carry **40% of the total weight**
  (20% + 15% + 5%), meaning nearly half of DeepSupp's composite "win" rests on
  dimensions where the evaluation framework doesn't appear to be discriminating
  between approaches at all.
- **DeepSupp loses the single highest-weighted metric (Support Accuracy, 25%) by a
  wide margin** — 0.483 vs. Local Minima's 0.603 — to the simplest possible baseline in
  the comparison set. On the metrics that *do* show real spread (Support Accuracy,
  Price Proximity, Support Duration — 60% of the weight combined), DeepSupp is
  consistently 2nd-4th place, never 1st.
- **The composite margin over HMM is 0.004** (0.554 vs 0.550), smaller than DeepSupp's
  own reported standard deviation (±0.039) and much smaller than HMM's (±0.044) — on
  the numbers given, this is not distinguishable from noise. HMM is also vastly cheaper
  to run than a trained 4-head attention autoencoder + rolling correlation pipeline.
- Net effect: the strongest honest reading of Table 1 is "DeepSupp is never the worst
  performer and has the most stable score across tickers," which is a real but modest
  claim, not "DeepSupp finds better support/resistance levels than existing methods" —
  and per this skill's own recurring finding, this is another paper whose *headline*
  claim is more modest on close reading than the framing suggests.

## Portability

**Not portable to Pine Script — a hard barrier, not just extra effort.** Every stage of
the pipeline requires infrastructure Pine does not have:
- Training a multi-head attention autoencoder via backpropagation (no ML training of
  any kind is possible in Pine).
- Rolling 32×32 Spearman correlation matrices as a batched tensor operation (Pine can
  compute a single pairwise `ta.correlation` but not a matrix pipeline like this).
- DBSCAN density-based clustering (no clustering primitives in Pine at all).

If this were ever pursued, the entire pipeline belongs in the Python `quantor` stack
(e.g. PyTorch/TensorFlow for the attention autoencoder, `scipy`/`scikit-learn` for
Spearman correlation and DBSCAN), trained offline, with levels exported and fed into a
Pine script as static data (e.g. re-entered periodically, or bridged via an external
data feed) — a real operational undertaking, disproportionate to the modest, noisy edge
the paper's own results actually support (see Critique above).

## Mapping to This Repo

- **Conceptual goal already achieved more simply.** DeepSupp's stated selling point over
  naive baselines (Figure 4: Moving Average produces "closely spaced, redundant"
  support levels with little differentiation, vs. DeepSupp's "varied gaps... major and
  minor support areas") describes exactly the failure mode a **Volume Profile**
  (POC/Value Area High/Low) already avoids, using simple, transparent, causally
  grounded math — levels form where real trading volume concentrated, not where a
  correlation-attention model's embedding space happened to cluster. This repo already
  has a working Volume Profile module in `Supply_and_Demand_Zones_XL.pine`
  (`vpShowPOC`/`vpShowVA`, built this session) directly usable as the practical
  alternative.
- **`Regime_Engine_TCO_Gatekeeper.pine`'s current structural levels are the closest
  candidate for this kind of upgrade** — its `swingLen`-based single-pivot "must break"
  lines are exactly the simple, mechanical level-detection DeepSupp positions itself
  against. Given the portability barrier and the weak evidence above, the recommended
  path is porting the Volume Profile POC/VAH/VAL concept from `Supply_and_Demand_
  Zones_XL.pine` into the TCO engine, not attempting any part of DeepSupp's own
  pipeline.
- **RVOL and PriceChangeVolume overlap with existing/newly-built features.** DeepSupp's
  `VolumeRatio` feature is identical in construction to this repo's RVOL (`Regime_
  Engine_TCO_Gatekeeper.pine`'s `rvol = volume / volAvg`). Its `PriceChangeVolume`
  (volume-weighted price change, a "conviction" proxy) is conceptually adjacent to —
  though not identical to — the CVD/Volume Trend modules already built in
  `Regime_Engine_TCO_Gatekeeper.pine` this session; worth remembering as a candidate
  feature (a single-bar, not cumulative, volume-weighted momentum term) if a future
  session wants a third, still-distinct volume-based signal, but not something to add
  speculatively — this repo's running lesson from CVD/Volume Trend is to add a new
  volume signal only when it measures something the existing RVOL/CVD/Volume Trend trio
  genuinely doesn't.

## Applied in This Repo

**2026-08-31** — Ported the Volume Profile (POC/VAH/VAL) concept into
`Regime_Engine_TCO_Gatekeeper.pine`, as recommended above, rather than any part of
DeepSupp's own pipeline. Lean port of the visual Volume Profile already built in
`Supply_and_Demand_Zones_XL.pine`: bins a lookback window into price rows, sums each
row's volume, takes the highest-volume row as POC, expands outward until the Value Area
% is covered — three lines (POC, VAH, VAL) instead of the source script's full box
histogram, recomputed on the last bar only. Added as a new "VOL PROFILE" dashboard row
and folded into `atGoodEntryZone` (informational, alongside the existing Fibonacci and
RAP pullback zones — not a hard gate). Confirms the Mapping section's prediction: the
transparent, volume-grounded alternative was straightforward to build and integrate,
with none of the infrastructure barriers DeepSupp's own pipeline would have required.
