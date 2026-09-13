---
name: pine-proven-patterns
description: Persistent knowledge base of Pine Script v6 code patterns, idioms, and compiler-behavior gotchas already proven to work (or proven to fail) in this repo's own .pine files — MTF pivot pulls, cooldown/bar-index arithmetic, broker-verified exit detection via strategy.closedtrades, user-defined-type construction rules, for-loop direction inference, and other hard-won fixes. Load this BEFORE writing, revising, or debugging any Pine Script strategy or indicator in this repo — check it for an existing working pattern or a known failure mode before building new logic from scratch, especially anything touching multi-timeframe data (request.security), cooldown/state machines, pivots, or trade-exit detection.
---

# Pine Proven Patterns

A living reference library of Pine Script v6 patterns that have been directly
observed working (or directly observed failing, with the fix) in this repo's own
`.pine` files. Unlike `quant-research-notes` (trading theory from academic papers),
this skill is about **mechanical Pine Script correctness and idiom** — the kind of
thing that only surfaces by actually compiling and backtesting code in this repo.

Per the user's explicit standing instruction: *"use the pine scripts in my repo as
proven concepts, they are your skills from this point forward."* The existing
strategies and indicators in this repo are the source of truth for "this is how you
do X correctly in Pine v6 in this codebase" — consult them before inventing a new
approach, especially for anything that has already caused a bug once.

**This file is meant to be extended, not replaced.** When a new pattern is proven
(or a new failure mode is diagnosed and fixed) in this repo:
1. Add a new `references/<slug>.md` file using the same structure as the existing
   ones (Problem → Proven solution → Source (file/lines) → Code pattern → When to
   use it → Pitfalls it avoids / gotchas).
2. Add a row to the Index table below.
3. Add an entry to the Changelog at the bottom with the date and a one-line summary.
4. If a new finding **contradicts** something already recorded here (e.g. a pattern
   that worked in one script but fails in another context), do not silently
   overwrite the old entry — add a "Contradicts / qualifies" note under the relevant
   reference file pointing both ways, and surface it explicitly to the user rather
   than picking a winner unasked.
5. If a pattern here gets applied to fix or build a new script, note the file name
   and what was actually built under "Applied in this repo" in the relevant
   reference file, so this skill also tracks where each pattern is already in use.

## Index

| # | Concept | Reference file | Proven in |
|---|---|---|---|
| 1 | MTF confirmed-pivot pull via `ta.valuewhen()` + `lookahead_on` + `[1]` offset (hand-rolled var-state pivot tracking through `request.security` does NOT work) | `references/mtf-confirmed-pivot-pull.md` | `MTF_Second_Flip_Continuation_v1_2.pine` (`f_structureBias()`); applied to fix `delta_break_retest/Stage4_MTFBiasStack.pine` |
| 2 | Bar-index-arithmetic cooldown (reset on ENTRY not exit, no countdown var, `na` sentinel via large fallback) | `references/bar-index-cooldown-arithmetic.md` | `Trend_Following_Strategy_v6_Signal_Cooldown_FIX.pine`; applied in `delta_break_retest/Stage3_CooldownModule.pine` |
| 3 | Broker-verified exit detection via `strategy.closedtrades.entry_id()` / `.exit_bar_index()` / `.profit()` instead of inferring exits from `strategy.position_size` transitions | `references/broker-verified-exit-detection.md` | `Ranger_V2_*_POC_State_*.pine` family, `P0_Rebuild_Stage0_SanityCheck.pine`; applied in `Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine` |
| 4 | Pine v6 compiler-behavior gotchas (for-loop direction inference on empty arrays, UDT field default-value restriction, `var bool` cannot default to plain `na`, nested tuples from multi-return built-ins, `[]` operator can't index a multi-return tuple, `==`/`!=` against `na` is unreliable — always use `na()`/`not na()`) | `references/pine-v6-compiler-gotchas.md` | Discovered/fixed live in `delta_break_retest/Stage2_POIExtraction.pine`, `Stage3_CooldownModule.pine`, `Stage4_MTFBiasStack.pine`, `Stage6_RetestTrigger.pine` |

## Update discipline notes

- A pattern only belongs in the Index once it has been **observed working** (or
  observed failing with a confirmed fix) against real chart data or a real compile
  — not just written and assumed correct. Code that "looks right" but hasn't been
  run is not yet a proven pattern.
- When debugging a NEW script and a symptom looks familiar, search this skill's
  Index first, then grep the repo's `.pine` files directly for the concept — many
  patterns proven once are reused silently across multiple strategies in this repo
  without ever being written down here yet. Finding one during a debugging session
  is itself a trigger to add it here per the rules above.

## Changelog

- **2026-09-13 (hard-won lesson)**: `Stage6_RetestTrigger.pine`'s retest/
  trigger signal stayed dead (Active Zone / Hours Since Break both `--`)
  through FIVE separate, individually well-reasoned, individually
  falsified rounds of fixes to its `request.security()`/MTF pull layer
  (confirmation timing, a Broken-flag dependency, internal `ta.valuewhen`
  aggregation, the `na`-vs-`0.0` sentinel, and finally a two-layer
  function-split matching `Supply_and_Demand_Zones_XL.pine`'s proven
  structure — genuinely the right structural pattern, confirmed against
  real working repo code per explicit user instruction to stop guessing
  and check proven scripts, but still not the actual bug). Round 6 finally
  found it by re-auditing the CONSUMER of the pulled value instead of the
  pull itself: `bool newBreakEvent = breakDirection != 0 and breakEventTime
  != activeEventTime`, comparing against a `var int activeEventTime = na`
  sentinel with `!=` instead of `na()`. Logged as gotcha #6 in
  `references/pine-v6-compiler-gotchas.md`. The meta-lesson, worth
  repeating: when a signal is dead, don't assume the bug is in the most
  recently touched or most exotic-looking code just because it's the
  newest part of the script — audit the plain consumer logic too, and
  audit `!=`/`==` comparisons against any `na`-initialized `var`
  specifically, since Pine won't raise a compile or runtime error for this
  one, it just silently never fires.
- **2026-09-13 (correction)**: `references/mtf-confirmed-pivot-pull.md`'s
  original code sample was itself wrong in one detail — it applied the `[1]`
  offset to the whole pulled function call (`f_context()[1]`), which is only
  valid for a single-return function. Porting the pattern to
  `Stage4_MTFBiasStack.pine`'s multi-value context functions
  (`f_get4hContext()`, `f_get1hContext()`) hit CE10123 ("operator SQBR" can't
  take a tuple) on the very next compile. Fixed in both the code and the
  reference doc: for multi-return functions, `[1]` goes on each return value
  individually, inside the function, not on the outer call. Logged as its own
  gotcha (#5) in `references/pine-v6-compiler-gotchas.md` per this skill's own
  "don't silently overwrite, surface the correction" rule.
- **2026-09-13**: Skill created. Seeded with the four patterns above, all
  directly surfaced during the `delta_break_retest/` staged rebuild session:
  the MTF pivot fix (found by searching the repo per explicit user instruction
  after `request.security`-based hand-rolled pivot tracking was empirically
  confirmed to never update across months of loaded history), the cooldown
  bar-index-arithmetic pattern (the "glue" the user pointed to from the v6.1
  Trend Following strategy, now also the architecture Stage 3's `CooldownModule`
  was built around), the `strategy.closedtrades`-based exit detection the user
  supplied directly to fix `Dynamic_P0_Delta_Profile_Strategy_v1_0_4.pine`, and
  four distinct Pine v6 compiler-behavior gotchas hit and fixed while writing
  Stages 2-4 of the rebuild.
