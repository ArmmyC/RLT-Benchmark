# RTL-OPT Qwen36-27B Public Lint Baseline

## Run

- Benchmark: RTL-OPT public repository
- Model: `qwen36-27b`
- Endpoint: `http://lanta-g-165:8000/v1`
- Run directory: `outputs/rtlopt_lint_pass1/20260612T045332Z__rtlopt__qwen36-27b`
- Evaluation mode: Verilator lint-only
- Tasks: 40
- Samples per task: 1

## Results

- Lint pass rate: 37 / 40 = 0.9250
- Failure categories: `{"passed": 37, "compile_failure": 3}`

## Failed Tasks

- `divider_32bit`: procedural assignment/conditional logic emitted at module scope.
- `register`: malformed module declaration; generated top module began as `module for`.
- `saturating_add`: declared `wire` inside procedural block in a way Verilator rejected.

Detailed failure analysis:

```text
outputs/rtlopt_lint_pass1/20260612T045332Z__rtlopt__qwen36-27b/logs/compile_failure_analysis.md
```

## Interpretation

This is a syntax/lint baseline, not the final RTL-OPT score. RTL-OPT is fundamentally about preserving behavior while improving PPA, so the next step is to add a Yosys-based synthesis/PPA evaluator and, if feasible with public tooling, an equivalence check against the reference RTL.
