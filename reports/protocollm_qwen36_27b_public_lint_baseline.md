# ProtocolLLM Public Lint Baseline: qwen36-27b

## Summary

This report records a public-repository ProtocolLLM baseline for `qwen36-27b` served through the Lanta vLLM OpenAI-compatible API.

- Date: 2026-06-11
- Host: Lanta
- Model endpoint: `http://lanta-g-069:8000/v1`
- Served model ID: `qwen36-27b`
- Benchmark source: `https://github.com/amsheth/ProtocolLLM`
- Paper: `https://arxiv.org/abs/2506.07945`
- Public prompt tasks loaded: 9
- Protocols: SPI, I2C, AXI, UART
- Evaluator used here: Verilator lint only
- Generation setting: temperature `0.2`, top_p `0.95`, max_tokens `4096`

Important limitation: the public repository includes prompts, existing generated outputs, lint/synthesis scripts, and metric tables, but it does not include the waveform/UVM functional testbenches described in the paper. Therefore this report measures **SystemVerilog lint correctness**, not full ProtocolLLM functional protocol correctness.

## Results

- Output: `outputs/protocollm_lint_pass1/20260611T162344Z__protocollm__qwen36-27b`
- Samples: 9
- Verilator lint passed: 7
- Lint pass rate: 0.7778

The generic runner fields map as follows for this public ProtocolLLM condition:

- `syntax_pass_rate`: Verilator lint pass rate
- `functional_pass_rate`: also Verilator lint pass rate, because no public functional testbench is available
- `pass@1`: lint pass@1, not waveform-functional pass@1

Failure categories:

| Category | Count |
|---|---:|
| passed | 7 |
| compile_failure | 2 |

## Task Coverage

Loaded tasks from `src/configs/base.yaml`:

| Protocol | Tasks |
|---|---:|
| SPI | 4 |
| I2C | 2 |
| AXI | 1 |
| UART | 2 |

## Failure Analysis

Detailed log:

- `outputs/protocollm_lint_pass1/20260611T162344Z__protocollm__qwen36-27b/logs/compile_failure_analysis.md`

The two lint failures were:

| Task | Diagnosis |
|---|---|
| `uart__easy1` | procedural_code_outside_always |
| `uart__hard1` | undeclared next-state/helper variables |

Interpretation:

- SPI, I2C, and AXI prompts all produced lint-clean SystemVerilog in this run.
- UART was the weak protocol in this public lint condition.
- This does not imply UART functional failure only; it did not pass syntax/lint strongly enough to reach any functional stage.

## Harness Notes

ProtocolLLM support required a separate evaluator path:

- Adapter: `ProtocolLLMAdapter`
- Config: `configs/protocollm.yaml`
- Evaluator: `VerilatorLintEvaluator`

The adapter loads prompts from `src/configs/base.yaml`. It extracts all modules from model output, because protocol implementations may validly include helpers.

## Caveats

- This is not comparable to VerilogEval/RTLLM functional pass rates.
- The ProtocolLLM paper describes lint, synthesis, and waveform simulation, but the public repo currently lacks functional testbenches.
- Yosys/OpenSTA synthesis could be added later if the required standard-cell environment is installed and validated.
- Full ProtocolLLM functional benchmarking requires obtaining or reconstructing the missing protocol testbenches.

## Conclusion

Under the public-repository lint-only condition, `qwen36-27b` passes 7/9 ProtocolLLM prompts.

This is a useful syntax/synthesizability-adjacent checkpoint, but it should be reported separately from the functional VerilogEval and RTLLM baselines.
