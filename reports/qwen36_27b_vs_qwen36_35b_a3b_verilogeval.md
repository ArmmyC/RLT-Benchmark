# Qwen36-27B vs Qwen36-35B-A3B VerilogEval v2 Comparison

## Scope

This comparison uses only VerilogEval v2 functional simulation results under matched benchmark settings.

Do not compare these numbers against lint-only ProtocolLLM or synthesis/equivalence RTL-OPT results as if they measure the same thing.

## Matched Settings

| Setting | pass@1 | pass@5 |
|---|---|---|
| Benchmark | VerilogEval v2 `dataset_spec-to-rtl` | VerilogEval v2 `dataset_spec-to-rtl` |
| Tasks | 156 | 156 |
| Samples per task | 1 | 5 |
| Temperature | 0.2 | 0.6 |
| Top-p | 0.95 | 0.95 |
| Max tokens | 2048 | 2048 |
| Evaluator | Icarus functional simulation | Icarus functional simulation |
| Repair retries | none | none |

## Results

| Model | Run | Samples | Syntax Pass | Functional/sample Pass | pass@5 |
|---|---|---:|---:|---:|---:|
| `qwen36-27b` | `outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b` | 156 | 0.8397 | 0.6154 | - |
| `qwen36-35b-a3b` | `outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z` | 156 | 0.7564 | 0.5705 | - |
| `qwen36-27b` | `outputs/verilogeval_v2_pass5/20260611T091009Z__verilogeval__qwen36-27b` | 780 | 0.7962 | 0.6115 | 0.7756 |
| `qwen36-35b-a3b` | `outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z` | 780 | 0.7449 | 0.5615 | 0.7308 |

## Deltas

| Metric | qwen36-27b | qwen36-35b-a3b | Delta |
|---|---:|---:|---:|
| pass@1 syntax | 0.8397 | 0.7564 | -0.0833 |
| pass@1 functional | 0.6154 | 0.5705 | -0.0449 |
| pass@5 syntax | 0.7962 | 0.7449 | -0.0513 |
| pass@5 sample functional | 0.6115 | 0.5615 | -0.0500 |
| pass@5 task recovery | 0.7756 | 0.7308 | -0.0449 |

## Failure Breakdown

### pass@1

| Model | Passed | Simulation Failure | Compile Failure | Extraction Failure |
|---|---:|---:|---:|---:|
| `qwen36-27b` | 96 | 35 | 17 | 8 |
| `qwen36-35b-a3b` | 89 | 29 | 26 | 12 |

### pass@5 Samples

| Model | Passed | Simulation Failure | Compile Failure | Extraction Failure |
|---|---:|---:|---:|---:|
| `qwen36-27b` | 477 | 144 | 104 | 55 |
| `qwen36-35b-a3b` | 438 | 143 | 121 | 78 |

## Conclusion

On VerilogEval v2, `qwen36-27b` is stronger than `qwen36-35b-a3b` under the matched baseline settings we have tested so far.

The difference is not huge, but it is consistent:

- `qwen36-27b` has better pass@1 functional correctness.
- `qwen36-27b` has better pass@5 recovery.
- `qwen36-35b-a3b` shows more extraction and compile failures, which lowers syntax pass rate.

Recommended next comparison step: run RTLLM 2.0 pass@1 for `qwen36-35b-a3b` with the same settings as the existing `qwen36-27b` RTLLM run. That will show whether the VerilogEval gap generalizes to a second functional RTL benchmark.
