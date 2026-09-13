# Pine v6 compiler-behavior gotchas

Four distinct Pine v6 compile/runtime-error patterns, each hit and fixed live
while writing the `delta_break_retest/` staged rebuild this session. These are
mechanical language-behavior facts, not strategy design choices — worth checking
against before writing new loop/type/tuple code in this repo.

## 1. `for` loop direction auto-inference on empty arrays (RE10045)

**Symptom:** `array.get() Index 0 out of bounds, array size is 0` at runtime, in
a loop that looks like it should never execute when the array is empty:

```pine
for i = 0 to array.size(registry) - 1
    // ...array.get(registry, i)...
```

**Root cause:** Pine's `for i = start to end` with no explicit `by` auto-infers
the step DIRECTION from whether `start <= end` at that point. When `registry` is
empty, `array.size(registry) - 1` evaluates to `-1`, so `start (0) > end (-1)`,
and Pine infers a DESCENDING loop — which, unlike a typical C-style `for`, still
executes **at least once**, with `i` starting at `0`, before immediately going
out of bounds. This is NOT "skip the loop when the range is empty/inverted" —
that assumption is wrong for Pine.

**Fix:** Always guard with an explicit size check before the loop:

```pine
if array.size(registry) > 0
    for i = 0 to array.size(registry) - 1
        // ...
```

**Found in:** `delta_break_retest/Stage2_POIExtraction.pine`, `f_tryAddPoi()`'s
"too close to existing POI" check. Audited every other `for i = 0 to
array.size(x) - 1` loop written this session — this was the only unguarded
instance; every other one already had the guard from established habit.

## 2. User-defined type field defaults must be literal constants (CE10133)

**Symptom:** `default value cannot be a function, variable or calculation` on a
`type` declaration like:

```pine
type CooldownState
    array<string> usedPoiIds = array.new_string()   // INVALID
```

**Root cause:** Pine v6 UDT field defaults must be literal constants (`na`, `0`,
`false`, `""`, etc.) — a function call is not allowed as a default, even one with
no arguments.

**Fix:** Omit the default in the type declaration; pass the actual value
explicitly as a named argument at construction time:

```pine
type CooldownState
    array<string> usedPoiIds

// ...

CooldownState.new(usedPoiIds = array.new_string())
```

**Found in:** `delta_break_retest/Stage3_CooldownModule.pine`, `CooldownState`
type. Audited all other `type` declarations written this session — only
instance.

## 3. `var bool` cannot be initialized to plain `na` (CE10173)

**Symptom:** `Cannot assign a value of the 'simple na' type... const bool type`
on:

```pine
var bool lastLoggedTrendOK = na   // INVALID
```

**Root cause:** unlike `float`/`int`, which happily accept `na` as an initial
`var` value, Pine v6 does not accept plain `na` for an explicitly-typed `var
bool`.

**Fix:** initialize to `false` instead (or `true`, whichever is the correct
"nothing has happened yet" sentinel for that flag) — there's no boolean `na`
equivalent to fall back on, so pick the value that reads as "unset."

```pine
var bool lastLoggedTrendOK = false
```

**Found in:** `delta_break_retest/Stage4_MTFBiasStack.pine`. Audited all other
files — only instance.

## 4. Multi-return built-ins can't be nested inside another tuple literal

**Symptom:** compile error when a function that itself returns a tuple (e.g.
`ta.dmi()`, which returns `[plusDI, minusDI, adx]`) is embedded directly as one
slot of a larger tuple literal, e.g. passed straight into `request.security`:

```pine
// INVALID shape — ta.dmi(...) is itself a 3-tuple, can't sit inside this outer tuple
request.security(syminfo.tickerid, tf, [ta.dmi(len, len), emaFast, emaSlow], ...)
```

**Fix:** destructure the nested tuple **locally, inside a wrapper function**, and
only pass the specific scalar(s) actually needed onward in the wrapper's own
return tuple:

```pine
f_get1hContext() =>
    [plusDI, minusDI, adx] = ta.dmi(dmiLen, dmiLen)   // destructure locally
    float emaFast = ta.ema(close, fastLen)
    float emaSlow = ta.ema(close, slowLen)
    [adx, emaFast, emaSlow, /* ...er... */]            // only scalars go onward

[adx1h, emaFast1h, emaSlow1h, er1h] = request.security(syminfo.tickerid, tf, f_get1hContext()[1], ...)
```

**Found in:** `delta_break_retest/Stage4_MTFBiasStack.pine`, `f_get1hContext()`.
Caught proactively while writing the file, before it ever reached compile — worth
checking for this shape any time a built-in that returns multiple values
(`ta.dmi`, `ta.macd`, `ta.bb`, `ta.kc`, etc.) is used inside a function destined
for `request.security`.

## 5. The `[]` history-reference operator can't be applied to a multi-return tuple (CE10123)

**Symptom:** `Cannot call "operator SQBR" with argument "expr0"=...` naming a
function call whose type is a list like `[series float, series float, series
float, series float]`, followed by `An argument of [...] type was used but a
"series na" is expected.`

```pine
f_context() =>
    // ...
    [valA, valB, valC, valD]

// INVALID -- f_context() returns 4 values, not 1
[a, b, c, d] = request.security(syminfo.tickerid, tf, f_context()[1], ...)
```

**Root cause:** `expr[N]` (the historical-reference operator) only accepts a
single series expression. A function that returns multiple values returns a
tuple, and a tuple is not a valid operand for `[]` — even though `[]` on a
*single-return* function call (e.g. `f_structureBias()[1]` where
`f_structureBias()` returns one `int`) is perfectly valid and is exactly the
recommended way to apply a one-bar-back offset before a `lookahead_on`
`request.security()` pull (see `references/mtf-confirmed-pivot-pull.md`).

**Fix:** for a multi-return function, apply `[1]` to each return value
INDIVIDUALLY on the function's own last line — still inside the function, so
it's still evaluated in the pulled context — then pass the bare (un-indexed)
function call to `request.security()`:

```pine
f_context() =>
    // ...
    [valA[1], valB[1], valC[1], valD[1]]   // offset baked in here

[a, b, c, d] = request.security(syminfo.tickerid, tf, f_context(), ...)   // no outer [1]
```

**Found in:** `delta_break_retest/Stage4_MTFBiasStack.pine`, both
`f_get4hContext()` (7 return values) and `f_get1hContext()` (4 return values) —
this is the same file as the MTF pivot pattern (#`mtf-confirmed-pivot-pull.md`);
the first attempt to apply that pattern to a multi-value context function hit
this exact error, caught live in the TradingView mobile Pine Editor.

## 6. Comparing a value against `na` with `==`/`!=` is unreliable — always use `na()`/`not na()`

**Symptom:** logic that's supposed to fire "the first time X happens" never
fires — not once, not ever — even though every upstream signal feeding it is
confirmed correct and firing constantly. No compile error, no runtime error;
the condition just silently never becomes true.

```pine
var int activeEventTime = na

bool newBreakEvent = breakDirection != 0 and breakEventTime != activeEventTime  // INVALID pattern
```

**Root cause:** Pine's `==`/`!=` comparison operators don't reliably behave
like a normal equality check when one operand is `na` — comparing a real value
against `na` this way does not consistently evaluate to `true`/`false` the way
it intuitively should. The only safe way to test for "is this na" (or its
inverse) is the dedicated `na(x)` function, never a naive `x == na` or
`x != na`. This applies to `var`-initialized sentinels especially: a variable
declared `var int x = na` and later compared with `!=` against a real value
will not reliably detect "this hasn't been set yet."

**Fix:** explicitly handle the not-yet-set case with `na()` before falling
back to the normal comparison, once both sides are guaranteed non-na:

```pine
bool newBreakEvent = breakDirection != 0 and (na(activeEventTime) or breakEventTime != activeEventTime)
```

**Found in:** `delta_break_retest/Stage6_RetestTrigger.pine` — this was the
actual root cause of a bug that survived FIVE rounds of unrelated fixes to a
completely different part of the script (a `request.security()`/MTF pull) before
being found. Every one of those five rounds correctly diagnosed and fixed real,
legitimate issues in the pull layer (see `mtf-confirmed-pivot-pull.md`'s own
history for two of them), and none of them mattered, because the actual bug was
downstream in the *consumer* logic the whole time: `activeEventTime` started as
`var int ... = na`, and `breakEventTime != activeEventTime` on the very first
real event most likely evaluated to `na` (falsy) instead of `true` — so the
first adoption never happened, the sentinel stayed `na` forever, and every
subsequent event (600+) hit the identical broken comparison, permanently.
**Lesson for next time a signal seems dead: audit the CONSUMER of a pulled
value, not just the pull itself, especially any `!=`/`==` comparison touching
a `var` initialized to `na`** — don't assume the bug is in the most recently
touched or most exotic-looking code (the MTF pull here) just because it's the
newest or most unusual part of the script.

## When to check this file

Before writing a new `for i = 0 to array.size(x) - 1` loop, a new `type`
declaration with a non-trivial default, a `var bool` that needs an "unset"
sentinel, a `request.security` wrapper function that touches any multi-return
`ta.*` built-in, or ANY `==`/`!=` comparison where one side could be `na`
(especially a `var` sentinel initialized to `na`). These are easy to get wrong
in ways that either fail to compile (2, 3, 4) or compile fine and fail
silently/at runtime later (1, 6) — (1) won't surface until the array in
question is actually empty, and (6) won't surface as an error at all, just as
logic that mysteriously never fires despite everything upstream working.
