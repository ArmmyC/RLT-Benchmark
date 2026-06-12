# RTL-OPT Qwen3-Coder-30B-A3B-Instruct Public Baselines

## Lint Run

- Output: `outputs/rtlopt/qwen3-coder-30b-a3b/20260612T183843Z`
- Evaluation mode: Verilator lint-only
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 33 / 40 = 0.8250
- Failure categories: `{"passed": 33, "compile_failure": 4, "code_extraction_failure": 3}`

## Generic Synthesis Run

- Output: `outputs/rtlopt/qwen3-coder-30b-a3b/20260612T184111Z`
- Evaluation mode: Yosys generic synthesis
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 37 / 40 = 0.9250
- Failure categories: `{"passed": 37, "synthesis_failure": 2, "code_extraction_failure": 1}`
- Average generated generic cell ratio vs baseline: 1.3438
- Median generated generic cell ratio vs baseline: 1.0000

## Equivalence Run

- Benchmark: RTL-OPT public repository
- Model preset: `qwen3-coder-30b-a3b-instruct`
- Served model ID: `qwen3-coder-30b-a3b`
- Endpoint: `http://lanta-g-028:8000/v1`
- Output: `outputs/rtlopt/qwen3-coder-30b-a3b/20260612T184318Z`
- Evaluation mode: Yosys generic synthesis plus equivalence against original suboptimal RTL
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Equivalence Results

- Syntax/synthesis pass rate before equivalence: 0.9250
- Equivalence pass rate: 19 / 40 = 0.4750
- Failure categories: `{"passed": 19, "equiv_failure": 16, "code_extraction_failure": 2, "timeout": 2, "synthesis_failure": 1}`

## Valid Optimization Signal

Among the 19 equivalence-passing tasks:

- Fewer generic cells than the original baseline: 4 / 19
- Equal generic cells to the original baseline: 14 / 19
- More generic cells than the original baseline: 1 / 19
- Average generic cell ratio vs baseline: 0.9472
- Median generic cell ratio vs baseline: 1.0000

Equivalence-passing tasks that also reduced generic cells:

```text
alu_64bit
comparator
mux_4to1_16bit
mux_4to1_64bit
```

Failed tasks:

```text
code_extraction_failure: calculation, register
equiv_failure: adder, adder_carry, addr_calcu, comparator_16bit, comparator_8bit, divider_4bit, divider_8bit, fsm, mul_const, mul_subexpression, mux_dead, mux_large, saturating_add, sub_16bit, sub_32bit, sub_8bit
synthesis_failure: mux_encode
timeout: divider_16bit, divider_32bit
```

## Interpretation

This is the trustworthy RTL-OPT condition because it checks behavior preservation. `qwen3-coder-30b-a3b-instruct` ties `qwen36-35b-a3b` on equivalence pass rate, trails `qwen36-27b`, and has fewer equivalence-passing cell reductions than both qwen36 baselines.
