# RTLLM 2.0 Baseline: qwen36-27b

## Summary

This report records the baseline RTLLM 2.0 result for `qwen36-27b` served through the Lanta vLLM OpenAI-compatible API.

- Date: 2026-06-11
- Host: Lanta
- Model endpoint: `http://lanta-g-069:8000/v1`
- Served model ID: `qwen36-27b`
- Benchmark: RTLLM 2.0 / OpenLLM-RTL
- Source repository: `https://github.com/hkust-zhiyao/RTLLM.git`
- Tasks: 50
- Evaluator: Icarus Verilog 12.0
- Prompt condition: neutral RTL benchmark prompt built from each `design_description.txt`
- Generation setting: temperature `0.2`, top_p `0.95`, max_tokens `4096`

The benchmark client disables Qwen hidden thinking through vLLM chat-template kwargs:

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

RTLLM answers may validly include helper modules. The RTLLM adapter therefore extracts all complete Verilog modules from a response when the required top module is present. This is a harness compatibility fix, not task-specific prompt tuning.

## Results

- Output: `outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b`
- Samples: 50
- Passed: 30
- Syntax pass rate: 0.7000
- Functional pass rate / pass@1: 0.6000

Failure categories:

| Category | Count |
|---|---:|
| passed | 30 |
| compile_failure | 14 |
| simulation_failure | 4 |
| code_extraction_failure | 1 |
| timeout | 1 |

## Failure Analysis

Detailed logs:

- `outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b/logs/code_extraction_failure_analysis.md`
- `outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b/logs/compile_failure_analysis.md`
- `outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b/logs/simulation_failure_analysis.md`
- `outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b/logs/timeout_analysis.md`

### Code Extraction Failure

There was 1 extraction failure:

- `Miscellaneous__Frequency divider__freq_divbyfrac`

Diagnosis: truncated reasoning comments.

The model started a module, wrote long reasoning in Verilog comments, consumed the full `4096 / 4096` completion token budget, and did not reach `endmodule`. This is counted as baseline model behavior.

### Compile Failures

The 14 compile failures break down as:

| Diagnosis | Count |
|---|---:|
| compile_error_other | 5 |
| procedural_assignment_to_wire_output | 3 |
| procedural_code_outside_always | 3 |
| syntax_error | 2 |
| undefined_submodule_or_wrong_top | 1 |

Interpretation:

- The largest group is miscellaneous compile errors, often interface or parameter mismatches with RTLLM testbenches.
- Procedural-assignment and module-scope procedural-code errors are the same model weakness seen in VerilogEval.
- RTLLM arithmetic tasks with helper modules are sensitive to complete, syntactically valid multi-module generation.

### Simulation Failures

The 4 simulation failures break down as:

| Diagnosis | Count |
|---|---:|
| sequential_timing_or_state_error | 3 |
| functional_logic_error | 1 |

These samples compile but fail RTLLM's self-checking testbenches, so they are treated as functional RTL errors.

### Timeout

There was 1 timeout:

- `Miscellaneous__Others__serial2parallel`

The generated RTL compiled but simulation did not complete within the evaluation timeout. It is counted separately from simulation mismatch failures.

## Sanity Runs

The first 10-task sanity run scored 3/10 because the extractor kept only the first module from multi-module responses. After enabling all-module extraction for RTLLM, the same staged sanity condition improved to 6/10. The full baseline above uses the corrected all-module extraction behavior.

## Known Caveats

- This is a pass@1 baseline only; no RTLLM pass@5 run has been executed yet.
- Failure classifications are heuristic and based on compiler logs, testbench output, and response structure.
- Prompt engineering should be reported as a separate condition, not merged into this baseline.
- RTLLM testbenches are self-checking and do not always emit VerilogEval-style mismatch counts, so simulation-failure reports rely more on pass/fail strings and task metadata.

## Conclusion

`qwen36-27b` reaches an RTLLM 2.0 baseline pass@1 of `0.6000`.

The score is close to its VerilogEval v2 pass@1 baseline (`0.6154`), but the failure mix differs. RTLLM exposes more compile/interface issues in larger self-contained modules, while VerilogEval exposed more functional failures in sequential and FSM-heavy tasks.

Next recommended step: either run RTLLM pass@5 for a comparable pass@k curve, or add the next benchmark adapter, ProtocolLLM.
