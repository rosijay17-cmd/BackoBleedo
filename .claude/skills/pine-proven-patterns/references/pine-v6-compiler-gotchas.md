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

## When to check this file

Before writing a new `for i = 0 to array.size(x) - 1` loop, a new `type`
declaration with a non-trivial default, a `var bool` that needs an "unset"
sentinel, or a `request.security` wrapper function that touches any multi-return
`ta.*` built-in. All four of these are easy to get wrong in ways that either fail
to compile (2, 3, 4) or compile fine and fail silently/at runtime later (1) — (1)
in particular will not surface until the array in question is actually empty,
which may not happen until well into a real backtest.
