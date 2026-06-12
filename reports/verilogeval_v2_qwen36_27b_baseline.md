# VerilogEval v2 Baseline: qwen36-27b

## Summary

This report records the baseline VerilogEval v2 result for `qwen36-27b` served through the Lanta vLLM OpenAI-compatible API.

- Date: 2026-06-11
- Host: Lanta
- Model endpoint: `http://lanta-g-013:8000/v1`
- Served model ID: `qwen36-27b`
- Benchmark: NVlabs VerilogEval v2, `dataset_spec-to-rtl`
- Tasks: 156
- Evaluator: Icarus Verilog 12.0
- Prompt condition: neutral RTL benchmark prompt
- Generation setting for pass@1: temperature `0.2`, top_p `0.95`, max_tokens `2048`
- Generation setting for pass@5: temperature `0.6`, top_p `0.95`, max_tokens `2048`

The benchmark client disables Qwen hidden thinking through vLLM chat-template kwargs:

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

This is treated as an API/runtime compatibility setting, not a tuned task prompt. Without it, the model sometimes consumed all completion tokens in hidden reasoning and returned empty final content.

## Results

### Full Pass@1

- Output: `outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b`
- Samples: 156
- Passed: 96
- Syntax pass rate: 0.8397
- Functional pass rate / pass@1: 0.6154

Failure categories:

| Category | Count |
|---|---:|
| passed | 96 |
| simulation_failure | 35 |
| compile_failure | 17 |
| code_extraction_failure | 8 |

### Full Pass@5

- Output: `outputs/verilogeval_v2_pass5/20260611T091009Z__verilogeval__qwen36-27b`
- Samples: 780
- Passed samples: 477
- Syntax pass rate: 0.7962
- Functional sample pass rate: 0.6115

Pass@k:

| Metric | Score |
|---|---:|
| pass@1 | 0.6115 |
| pass@2 | 0.6910 |
| pass@3 | 0.7327 |
| pass@4 | 0.7577 |
| pass@5 | 0.7756 |

Failure categories:

| Category | Count |
|---|---:|
| passed | 477 |
| simulation_failure | 144 |
| compile_failure | 104 |
| code_extraction_failure | 55 |

## Failure Analysis

Detailed logs:

- `outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b/logs/code_extraction_failure_analysis.md`
- `outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b/logs/compile_failure_analysis.md`
- `outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b/logs/simulation_failure_analysis.md`

### Code Extraction Failures

All 8 pass@1 extraction failures are truncated generations:

- The response starts a `module TopModule`.
- The model writes long reasoning or derivations inside Verilog comments.
- The response consumes the full `2048 / 2048` completion token budget.
- The response never reaches `endmodule`.

This is counted as baseline model behavior. A stricter no-derivation prompt may improve it, but that should be reported as a separate benchmark condition.

### Compile Failures

The 17 pass@1 compile failures break down as:

| Diagnosis | Count |
|---|---:|
| procedural_assignment_to_wire_output | 12 |
| procedural_code_outside_always | 2 |
| undefined_submodule_or_wrong_top | 2 |
| benchmark_artifact_port_mismatch | 1 |

Interpretation:

- 16/17 compile failures are model-generated invalid RTL.
- 1/17 is a benchmark data inconsistency: `Prob099_m2014_q6c` prompt/reference use `Y1/Y3`, while the testbench instantiates `Y2/Y4`.
- The baseline score is left unchanged, but `Prob099_m2014_q6c` should be flagged when interpreting results.

### Simulation Failures

The 35 pass@1 simulation failures break down as:

| Diagnosis | Count |
|---|---:|
| sequential_timing_or_state_error | 10 |
| fsm_or_protocol_logic_error | 9 |
| combinational_logic_error | 6 |
| functional_logic_error | 4 |
| initial_reset_or_one_cycle_timing_error | 3 |
| timeout_or_nonterminating_behavior | 2 |
| reset_behavior_error | 1 |

Interpretation:

- These failures compiled successfully, so they are mostly functional RTL errors.
- Sequential, FSM, and protocol tasks are the dominant weakness.
- Some near-miss failures have only one mismatch and may be reset/initial timing issues.
- Severe failures include long-running timeout behavior in `Prob141_count_clock` and `Prob156_review2015_fancytimer`.

## Known Caveats

- This is a baseline under one neutral prompt and one model-serving configuration.
- Prompt engineering should be reported as a separate condition, not merged into this baseline.
- `Prob099_m2014_q6c` appears inconsistent in the official dataset files.
- The simulation-failure taxonomy is heuristic and based on task names, simulator hints, and mismatch behavior.

## Conclusion

`qwen36-27b` reaches a VerilogEval v2 baseline pass@1 of `0.6154` and pass@5 of `0.7756`.

The model is strong on early/simple combinational and basic sequential RTL, but loses accuracy on harder sequential, FSM, protocol, and long-context waveform-derived tasks. The largest non-functional issue is invalid procedural assignment to wire outputs, while the largest functional issue is incorrect sequential/FSM behavior.

Next recommended step: add the RTLLM 2.0 adapter and run the same model under the same benchmark discipline.
