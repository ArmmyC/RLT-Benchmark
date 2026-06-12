# RTL-OPT Qwen36-27B Yosys Generic Baseline

## Run

- Benchmark: RTL-OPT public repository
- Model: `qwen36-27b`
- Endpoint: `http://lanta-g-165:8000/v1`
- Run directory: `outputs/rtlopt_yosys_pass1/20260612T052731Z__rtlopt__qwen36-27b`
- Evaluation mode: Yosys generic synthesis stats
- Tasks: 40
- Samples per task: 1

## Results

- Synthesis pass rate: 36 / 40 = 0.9000
- Failure categories: `{"passed": 36, "synthesis_failure": 4}`
- Average generated generic cell ratio vs suboptimal baseline: 1.3389
- Median generated generic cell ratio vs suboptimal baseline: 1.0000
- Average generic cell improvement vs suboptimal baseline: -33.8949%
- Tasks with fewer generic cells than the suboptimal baseline: 13 / 36
- Average generated generic cell ratio vs reference: 1.2004

## Failed Tasks

- `divider_32bit`: non-constant generate condition plus module-scope procedural-style final correction.
- `mux_4to1_64bit`: malformed ternary/indexing expression.
- `mux_encode`: Yosys rejected unpacked array port syntax in both generated RTL and official source/reference files.
- `register`: malformed generated module declaration beginning with `module for`.

Detailed failure analysis:

```text
outputs/rtlopt_yosys_pass1/20260612T052731Z__rtlopt__qwen36-27b/logs/synthesis_failure_analysis.md
```

## Notes

This run uses a reproducible generic Yosys synthesis mode because the conda Yosys/ABC path stalled during Nangate Liberty technology mapping, even on small designs. The harness still parses official RTL-OPT Yosys area reports when available, and stores them beside generated generic metrics in `results.jsonl`.

This is still not a full RTL-OPT functional equivalence score. It is a stronger baseline than lint because generated RTL must synthesize and gets structural cell-count comparisons, but equivalence checking remains the next missing layer.
