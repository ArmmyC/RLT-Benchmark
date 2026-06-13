# RTL-OPT Qwen2.5-Coder-32B-Instruct Public Baselines

## Lint Run

- Output: `outputs/rtlopt/qwen25-coder-32b/20260613T031037Z`
- Evaluation mode: Verilator lint-only
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 37 / 40 = 0.9250
- Failure categories: `{"passed": 37, "compile_failure": 3}`

## Generic Synthesis Run

- Output: `outputs/rtlopt/qwen25-coder-32b/20260613T031340Z`
- Evaluation mode: Yosys generic synthesis
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096
- Result: 36 / 40 = 0.9000
- Failure categories: `{"passed": 36, "synthesis_failure": 4}`
- Average generated generic cell ratio vs baseline: 1.2959
- Median generated generic cell ratio vs baseline: 0.9741

## Equivalence Run

- Benchmark: RTL-OPT public repository
- Model preset: `qwen25-coder-32b`
- Served model ID: `qwen25-coder-32b`
- Endpoint: `http://lanta-g-017:8000/v1`
- Output: `outputs/rtlopt/qwen25-coder-32b/20260613T031649Z`
- Evaluation mode: Yosys generic synthesis plus equivalence against original suboptimal RTL
- Tasks: 40
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Equivalence Results

- Syntax/synthesis pass rate before equivalence: 0.9000
- Equivalence pass rate: 19 / 40 = 0.4750
- Failure categories: `{"passed": 19, "equiv_failure": 17, "synthesis_failure": 4}`

## Valid Optimization Signal

Among the 19 equivalence-passing tasks:

- Fewer generic cells than the original baseline: 8 / 19
- Equal generic cells to the original baseline: 10 / 19
- More generic cells than the original baseline: 1 / 19
- Average generic cell ratio vs baseline: 0.8709
- Median generic cell ratio vs baseline: 1.0000

Equivalence-passing tasks that also reduced generic cells:

```text
alu_8bit
comparator_2bit
comparator_4bit
comparator_8bit
mul_const
mux_4to1_16bit
mux_4to1_64bit
sub_16bit
```

Failed tasks:

```text
equiv_failure: adder, adder_carry, comparator_16bit, divider_32bit, fsm, fsm_encode, mac, mul, mul_subexpression, mult_if, mux_dead, mux_large, saturating_add, selector, sub_32bit, sub_4bit, sub_8bit
synthesis_failure: divider_16bit, divider_4bit, mux_encode, register
```

## Interpretation

This is the trustworthy RTL-OPT condition because it checks behavior preservation. `qwen25-coder-32b` ties `qwen36-35b-a3b` and `qwen3-coder-30b-a3b-instruct` on equivalence pass rate, trails `qwen36-27b`, and has the best average generic cell ratio among equivalence-passing tasks in this four-model set.
