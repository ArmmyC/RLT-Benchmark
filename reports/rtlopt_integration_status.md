# RTL-OPT Integration Status

## What We Added

- Added `rtlopt` as a reusable benchmark adapter.
- Registered it in the shared adapter registry.
- Added `configs/rtlopt_lint.yaml` for a first pass@1 lint baseline against the Lanta OpenAI-compatible endpoint.
- Added focused adapter tests.

## What The Adapter Loads

- Source: `benchmarks/rtl-opt/benchmark/<design>/<design>.v` or `.sv`
- Reference: `benchmarks/rtl-opt/benchmark/<design>_ref/<design>_ref.v` or `.sv`
- Task count on Lanta: 40
- Tasks with reference RTL on Lanta: 40

## Current Evaluation Mode

The first usable mode is `verilator_lint`.

This checks whether the model returns syntactically valid/synthesizable-looking RTL with the same top module target, but it is not yet a full RTL-OPT score. RTL-OPT's real value is PPA optimization under functional equivalence, so the next evaluator should add open-source synthesis metrics with Yosys and, if feasible, an equivalence check.

## Verification

Remote test suite on Lanta:

```text
16 passed
```

RTL-OPT adapter dry-load on Lanta:

```text
tasks 40
with_refs 40
evaluator verilator_lint
extract_all_modules True
```

## Blocker For A Model Run

The previous Lanta vLLM endpoint was not running:

```text
http://lanta-g-069:8000/v1/models -> connection refused
```

There were no active `ub127` Slurm jobs at the time of this integration check, so the next benchmark run requires restarting the model server or updating `configs/rtlopt_lint.yaml` to a new active endpoint.
