# RTL-OPT Qwen36-27B Yosys Equivalence Baseline

## Run

- Benchmark: RTL-OPT public repository
- Model: `qwen36-27b`
- Endpoint: `http://lanta-g-165:8000/v1`
- Run directory: `outputs/rtlopt_equiv_pass1/20260612T060533Z__rtlopt__qwen36-27b`
- Evaluation mode: Yosys generic synthesis plus equivalence against original suboptimal RTL
- Tasks: 40
- Samples per task: 1

## Results

- Equivalence pass rate: 25 / 40 = 0.6250
- Syntax/synthesis pass rate before equivalence: 36 / 40 = 0.9000
- Failure categories: `{"passed": 25, "equiv_failure": 9, "synthesis_failure": 4, "timeout": 2}`

## Valid Optimization Signal

Among the 25 equivalence-passing tasks:

- Fewer generic cells than the original baseline: 9 / 25
- Equal generic cells to the original baseline: 12 / 25
- More generic cells than the original baseline: 4 / 25
- Average generic cell ratio vs baseline: 0.9124
- Median generic cell ratio vs baseline: 1.0000

Equivalence-passing tasks that also reduced generic cells:

```text
adder
comparator_2bit
comparator_4bit
comparator_8bit
mul_const
mul_subexpression
mux_4to1_16bit
mux_4to1_64bit
sub_16bit
```

## Failed Tasks

Equivalence failures:

```text
adder_carry
addr_calcu
fsm
fsm_encode
gray
mac
mux_dead
saturating_add
ticket_machine
```

Synthesis failures:

```text
calculation
mux_encode
mux_large
register
```

Timeouts:

```text
divider_16bit
divider_32bit
```

Detailed failure analyses:

```text
outputs/rtlopt_equiv_pass1/20260612T060533Z__rtlopt__qwen36-27b/logs/equiv_failure_analysis.md
outputs/rtlopt_equiv_pass1/20260612T060533Z__rtlopt__qwen36-27b/logs/synthesis_failure_analysis.md
outputs/rtlopt_equiv_pass1/20260612T060533Z__rtlopt__qwen36-27b/logs/timeout_analysis.md
```

## Interpretation

This is the first RTL-OPT score that checks behavior preservation. The model often emits synthesizable RTL, but only 25 tasks were proven equivalent to the original RTL with this Yosys flow. Of those behavior-preserving outputs, 9 also improved generic cell count, which is the most honest current "valid optimization" subset.

This is still not full official PPA scoring because Nangate Liberty technology mapping through conda Yosys/ABC stalled on small examples. The current result is reproducible, open-source, and stricter than lint/synthesis-only.
