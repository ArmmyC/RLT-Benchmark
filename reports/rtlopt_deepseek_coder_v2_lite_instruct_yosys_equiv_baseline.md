# RTL-OPT DeepSeek-Coder-V2-Lite-Instruct Public Baselines

## Lint Run

- Benchmark: RTL-OPT public repository
- Model preset: `deepseek-coder-v2-lite-instruct`
- Served model ID: `deepseek-coder-v2-lite`
- Model repo: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- Output: `outputs/rtlopt/deepseek-coder-v2-lite/20260613T150136Z`
- Evaluation mode: Verilator lint-only
- Date: 2026-06-13
- Tasks: 40
- Samples: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 37 / 40 = 0.9250
- Failure categories: `{"passed": 37, "compile_failure": 2, "code_extraction_failure": 1}`

## Generic Synthesis Run

- Output: `outputs/rtlopt/deepseek-coder-v2-lite/20260613T170218Z`
- Evaluation mode: Yosys generic synthesis
- Tasks: 40
- Samples: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 36 / 40 = 0.9000
- Failure categories: `{"passed": 36, "synthesis_failure": 3, "code_extraction_failure": 1}`
- Average generated generic cell ratio vs baseline: 1.3264
- Median generated generic cell ratio vs baseline: 1.0000

## Equivalence Run

- Output: `outputs/rtlopt/deepseek-coder-v2-lite/20260613T190310Z`
- Evaluation mode: Yosys generic synthesis plus equivalence against original suboptimal RTL
- Tasks: 40
- Samples: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Equivalence Results

- Syntax/synthesis pass rate before equivalence: 0.9000
- Equivalence pass rate: 29 / 40 = 0.7250
- Failure categories: `{"passed": 29, "equiv_failure": 5, "synthesis_failure": 3, "timeout": 2, "code_extraction_failure": 1}`

## Valid Optimization Signal

Among the 29 equivalence-passing tasks:

- Fewer generic cells than the original baseline: 3 / 29
- Equal generic cells to the original baseline: 26 / 29
- More generic cells than the original baseline: 0 / 29
- Average generic cell ratio vs baseline: 0.9739
- Median generic cell ratio vs baseline: 1.0000

Equivalence-passing tasks that also reduced generic cells:

```text
comparator_4bit
comparator_8bit
mul_const
```

Failed tasks:

```text
code_extraction_failure: register
equiv_failure: adder_carry, comparator_2bit, mul, mult_if, sub_16bit
synthesis_failure: gray, mux_dead, mux_encode
timeout: divider_16bit, divider_32bit
```

## Output Artifacts

The lint, generic synthesis, and equivalence run folders contain:

```text
config_snapshot.yaml
run_metadata.json
report.md
results.jsonl
summary.json
summary.csv
raw_responses/
extracted_rtl/
logs/
error_logs/
```

## Interpretation

This is the trustworthy RTL-OPT condition because it checks behavior preservation. `deepseek-coder-v2-lite-instruct` has the strongest RTL-OPT equivalence pass rate in the current public comparison, but it does not have the strongest optimization magnitude: only 3 of its 29 equivalence-passing tasks reduce generic cell count.
