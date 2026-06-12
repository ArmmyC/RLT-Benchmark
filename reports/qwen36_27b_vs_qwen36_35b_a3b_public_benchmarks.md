# Qwen36-27B vs Qwen36-35B-A3B vs Qwen3-Coder Public RTL Benchmark Comparison

## Scope

This report compares `qwen36-27b`, `qwen36-35b-a3b`, and `qwen3-coder-30b-a3b-instruct` on public RTL benchmarks currently available in the harness.

Comparison rule:

- Functional simulation results are compared with functional simulation results.
- ProtocolLLM public lint is reported separately as lint-only.
- RTL-OPT equivalence is reported separately as behavior-preserving optimization evidence.

## Explicit Comparison Checklist

| Check | Status |
|---|---|
| qwen36-27b result | Included in every result table under the `qwen36-27b` column. |
| qwen36-35b-a3b result | Included in every result table under the `qwen36-35b-a3b` column. |
| qwen3-coder-30b-a3b-instruct result | Included in every result table under the `qwen3-coder-30b-a3b-instruct` column. |
| Same benchmark? | Yes. Each row below compares only the same benchmark and evaluation mode. |
| Same samples_per_task? | Yes. Listed per benchmark/mode in the matched settings audit. |
| Same temperature? | Yes. Listed per benchmark/mode in the matched settings audit. |
| Same max_tokens? | Yes. Listed per benchmark/mode in the matched settings audit. |

## Matched Settings Audit

| Benchmark / Mode | Same benchmark? | samples_per_task | Temperature | Top-p | Max tokens | Notes |
|---|---|---:|---:|---:|---:|---|
| VerilogEval v2 pass@1 | yes, VerilogEval v2 `dataset_spec-to-rtl` | 1 | 0.2 | 0.95 | 2048 | qwen36-27b run predates `run_metadata.json`; settings are from the committed baseline report and run command record; qwen36-35b and qwen3-coder verified from metadata |
| VerilogEval v2 pass@5 | yes, VerilogEval v2 `dataset_spec-to-rtl` | 5 | 0.6 | 0.95 | 2048 | qwen36-27b run predates `run_metadata.json`; settings are from the committed baseline report and run command record; qwen36-35b and qwen3-coder verified from metadata |
| RTLLM 2.0 pass@1 | yes, RTLLM 2.0 public benchmark | 1 | 0.2 | 0.95 | 4096 | verified from run metadata and committed baseline reports |
| ProtocolLLM public lint | yes, ProtocolLLM public prompts | 1 | 0.2 | 0.95 | 4096 | verified from run metadata and committed baseline reports; lint-only |
| RTL-OPT lint | yes, RTL-OPT public benchmark | 1 | 0.2 | 0.95 | 4096 | lint-only |
| RTL-OPT generic synthesis | yes, RTL-OPT public benchmark | 1 | 0.2 | 0.95 | 4096 | synthesis-only |
| RTL-OPT equivalence | yes, RTL-OPT public benchmark | 1 | 0.2 | 0.95 | 4096 | verified from run metadata and committed baseline reports; behavior-preserving optimization condition |

The comparison below reports the three model results side by side only within the same benchmark and evaluation mode.

## Output Artifact Tracking

Raw output folders are preserved on Lanta and are not committed to Git because `outputs/` is intentionally gitignored by repo policy. The committed output artifacts are the manifests, `reports/qwen36_35b_a3b_output_manifest.md` and `reports/qwen3_coder_30b_a3b_instruct_output_manifest.md`, which list every authoritative Lanta output folder. The committed artifacts are the benchmark configs, summary reports, output manifests, and this comparison report.

## Functional RTL Generation

| Benchmark | Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct |
|---|---|---:|---:|---:|
| VerilogEval v2 | pass@1 functional | 0.6154 | 0.5705 | 0.4808 |
| VerilogEval v2 | pass@5 task recovery | 0.7756 | 0.7308 | 0.5705 |
| RTLLM 2.0 | pass@1 functional | 0.6000 | 0.6000 | 0.5000 |

## Syntax / Compile Reliability

| Benchmark | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct |
|---|---:|---:|---:|
| VerilogEval v2 pass@1 syntax | 0.8397 | 0.7564 | 0.8654 |
| VerilogEval v2 pass@5 syntax | 0.7962 | 0.7449 | 0.8628 |
| RTLLM 2.0 syntax | 0.7000 | 0.7800 | 0.6600 |

## Lint-Only Protocol Result

| Benchmark | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct |
|---|---:|---:|---:|
| ProtocolLLM public lint | 0.7778 | 0.2222 | 0.7778 |

This is lint-only. It does not measure protocol functional correctness.

## RTL-OPT Behavior-Preserving Optimization

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct |
|---|---:|---:|---:|
| RTL-OPT lint pass | 0.9250 | 0.8500 | 0.8250 |
| RTL-OPT generic synthesis pass | 0.9000 | 0.8750 | 0.9250 |
| RTL-OPT equivalence pass | 0.6250 | 0.4750 | 0.4750 |
| Equiv-passing tasks with fewer generic cells | 9 / 25 | 6 / 19 | 4 / 19 |
| Average generic cell ratio among equiv-passing tasks | 0.9124 | 0.9003 | 0.9472 |

The 35B-A3B model has the best average cell ratio among the tasks that pass equivalence, but fewer tasks reach equivalence than qwen36-27b. Qwen3-Coder ties qwen36-35B-A3B on equivalence pass rate but has fewer cell-reducing equivalence-passing tasks.

## Conclusion

`qwen36-27b` remains the strongest public RTL benchmark baseline overall.

- It is better on VerilogEval v2 pass@1 and pass@5.
- It ties `qwen36-35b-a3b` and beats `qwen3-coder-30b-a3b-instruct` on RTLLM 2.0 functional pass@1.
- It ties `qwen3-coder-30b-a3b-instruct` on ProtocolLLM public lint.
- It is better on RTL-OPT equivalence pass rate and valid-improved task count.

The clearest advantages for `qwen3-coder-30b-a3b-instruct` are VerilogEval syntax pass rate and RTL-OPT generic synthesis pass rate. Those do not translate into stronger VerilogEval functional correctness, RTLLM functional correctness, or RTL-OPT equivalence.

Recommended next step: analyze why Qwen3-Coder has high syntax reliability but lower functional simulation pass rates, especially the VerilogEval and RTLLM simulation/compile failure mix.
