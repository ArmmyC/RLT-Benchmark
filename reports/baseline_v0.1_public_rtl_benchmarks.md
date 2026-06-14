# Baseline v0.1 Public RTL Benchmarks

## Scope

Five-model public RTL benchmark baseline generated from committed reports and LANTA output manifests.

Functional simulation, lint-only, synthesis-only, and equivalence results are reported in separate sections and are not treated as interchangeable.

## Matched Settings Audit

| Benchmark / mode | Samples per task | Temperature | Top-p | Max tokens | Matched across models? |
|---|---:|---:|---:|---:|---|
| verilogeval / pass1 | 1 | 0.2 | 0.95 | 2048 | yes |
| verilogeval / pass5 | 5 | 0.6 | 0.95 | 2048 | yes |
| rtllm2 / pass1 | 1 | 0.2 | 0.95 | 4096 | yes |
| protocollm / lint | 1 | 0.2 | 0.95 | 4096 | yes |
| rtlopt / lint | 1 | 0.2 | 0.95 | 4096 | yes |
| rtlopt / synthesis | 1 | 0.2 | 0.95 | 4096 | yes |
| rtlopt / equivalence | 1 | 0.2 | 0.95 | 4096 | yes |

## Artifact Tracking

The registry is the source of truth. Values marked `manual_summary` were transcribed from committed reports/manifests because raw LANTA output folders are not available in this checkout. Accessible `summary.json` files override manual values automatically.

## Functional RTL Generation

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| VerilogEval v2 pass@1 functional | 0.6154 | 0.5705 | 0.4808 | 0.4487 | 0.4872 |
| VerilogEval v2 pass@5 task recovery | 0.7756 | 0.7308 | 0.5705 | 0.5385 | 0.5641 |
| RTLLM 2.0 pass@1 functional | 0.6000 | 0.6000 | 0.5000 | 0.5400 | 0.5200 |

## Syntax / Compile Reliability

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| VerilogEval v2 pass@1 syntax | 0.8397 | 0.7564 | 0.8654 | 0.8846 | 0.8590 |
| VerilogEval v2 pass@5 syntax | 0.7962 | 0.7449 | 0.8628 | 0.8654 | 0.8551 |
| RTLLM 2.0 syntax | 0.7000 | 0.7800 | 0.6600 | 0.7400 | 0.7800 |

## ProtocolLLM Lint-Only

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| ProtocolLLM public lint pass | 0.7778 | 0.2222 | 0.7778 | 0.6667 | 0.6667 |

This section is lint-only and does not measure protocol functional correctness.

## RTL-OPT Lint-Only

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| RTL-OPT lint pass | 0.9250 | 0.8500 | 0.8250 | 0.9250 | 0.9250 |

## RTL-OPT Synthesis-Only

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| RTL-OPT generic synthesis pass | 0.9000 | 0.8750 | 0.9250 | 0.9000 | 0.9000 |

Synthesis success is not proof of behavior preservation.

## RTL-OPT Behavior-Preserving Optimization

| Metric | qwen36-27b | qwen36-35b-a3b | qwen3-coder-30b-a3b-instruct | qwen25-coder-32b | deepseek-coder-v2-lite-instruct |
|---|---:|---:|---:|---:|---:|
| RTL-OPT equivalence pass | 0.6250 | 0.4750 | 0.4750 | 0.4750 | 0.7250 |
| Equiv-passing tasks with fewer generic cells | 9 | 6 | 4 | 8 | 3 |
| Average generic cell ratio among equiv-passing tasks | 0.9124 | 0.9003 | 0.9472 | 0.8709 | 0.9739 |

Generic Yosys cell counts are an early optimization proxy, not final silicon PPA.

## Key Findings

- `qwen36-27b` is the strongest baseline for functional RTL generation in the registered results.
- `deepseek-coder-v2-lite-instruct` has the highest RTL-OPT equivalence pass rate.
- High syntax or lint rates do not imply functional correctness.

## Known Limitations

- Historical results use explicitly labeled manual summaries when local raw outputs are unavailable.
- ProtocolLLM is lint-only in Baseline v0.1.
- RTL-OPT generic cell ratios are not technology-mapped area, timing, or power results.
- Per-task failure analysis is only available for registered, accessible `results.jsonl` files.

## Regeneration

```bash
python scripts/generate_comparison_report.py --registry runs/index.yaml --baseline baseline_v0_1
```

## Data Sources

- `verilogeval_pass1_qwen36_27b`: `manual_summary` from `reports/verilogeval_v2_qwen36_27b_baseline.md`
- `verilogeval_pass1_qwen36_35b_a3b`: `manual_summary` from `reports/verilogeval_v2_qwen36_35b_a3b_baseline.md`
- `verilogeval_pass1_qwen3_coder`: `manual_summary` from `reports/verilogeval_v2_qwen3_coder_30b_a3b_instruct_baseline.md`
- `verilogeval_pass1_qwen25_coder`: `manual_summary` from `reports/verilogeval_v2_qwen25_coder_32b_baseline.md`
- `verilogeval_pass1_deepseek_coder`: `manual_summary` from `reports/verilogeval_v2_deepseek_coder_v2_lite_instruct_baseline.md`
- `verilogeval_pass5_qwen36_27b`: `manual_summary` from `reports/verilogeval_v2_qwen36_27b_baseline.md`
- `verilogeval_pass5_qwen36_35b_a3b`: `manual_summary` from `reports/verilogeval_v2_qwen36_35b_a3b_baseline.md`
- `verilogeval_pass5_qwen3_coder`: `manual_summary` from `reports/verilogeval_v2_qwen3_coder_30b_a3b_instruct_baseline.md`
- `verilogeval_pass5_qwen25_coder`: `manual_summary` from `reports/verilogeval_v2_qwen25_coder_32b_baseline.md`
- `verilogeval_pass5_deepseek_coder`: `manual_summary` from `reports/verilogeval_v2_deepseek_coder_v2_lite_instruct_baseline.md`
- `rtllm2_pass1_qwen36_27b`: `manual_summary` from `reports/rtllm2_qwen36_27b_baseline.md`
- `rtllm2_pass1_qwen36_35b_a3b`: `manual_summary` from `reports/rtllm2_qwen36_35b_a3b_baseline.md`
- `rtllm2_pass1_qwen3_coder`: `manual_summary` from `reports/rtllm2_qwen3_coder_30b_a3b_instruct_baseline.md`
- `rtllm2_pass1_qwen25_coder`: `manual_summary` from `reports/rtllm2_qwen25_coder_32b_baseline.md`
- `rtllm2_pass1_deepseek_coder`: `manual_summary` from `reports/rtllm2_deepseek_coder_v2_lite_instruct_baseline.md`
- `protocollm_lint_qwen36_27b`: `manual_summary` from `reports/protocollm_qwen36_27b_public_lint_baseline.md`
- `protocollm_lint_qwen36_35b_a3b`: `manual_summary` from `reports/protocollm_qwen36_35b_a3b_public_lint_baseline.md`
- `protocollm_lint_qwen3_coder`: `manual_summary` from `reports/protocollm_qwen3_coder_30b_a3b_instruct_public_lint_baseline.md`
- `protocollm_lint_qwen25_coder`: `manual_summary` from `reports/protocollm_qwen25_coder_32b_public_lint_baseline.md`
- `protocollm_lint_deepseek_coder`: `manual_summary` from `reports/protocollm_deepseek_coder_v2_lite_instruct_public_lint_baseline.md`
- `rtlopt_lint_qwen36_27b`: `manual_summary` from `reports/rtlopt_qwen36_27b_public_lint_baseline.md`
- `rtlopt_lint_qwen36_35b_a3b`: `manual_summary` from `reports/rtlopt_qwen36_35b_a3b_yosys_equiv_baseline.md`
- `rtlopt_lint_qwen3_coder`: `manual_summary` from `reports/rtlopt_qwen3_coder_30b_a3b_instruct_yosys_equiv_baseline.md`
- `rtlopt_lint_qwen25_coder`: `manual_summary` from `reports/rtlopt_qwen25_coder_32b_yosys_equiv_baseline.md`
- `rtlopt_lint_deepseek_coder`: `manual_summary` from `reports/rtlopt_deepseek_coder_v2_lite_instruct_yosys_equiv_baseline.md`
- `rtlopt_synthesis_qwen36_27b`: `manual_summary` from `reports/rtlopt_qwen36_27b_yosys_generic_baseline.md`
- `rtlopt_synthesis_qwen36_35b_a3b`: `manual_summary` from `reports/rtlopt_qwen36_35b_a3b_yosys_equiv_baseline.md`
- `rtlopt_synthesis_qwen3_coder`: `manual_summary` from `reports/rtlopt_qwen3_coder_30b_a3b_instruct_yosys_equiv_baseline.md`
- `rtlopt_synthesis_qwen25_coder`: `manual_summary` from `reports/rtlopt_qwen25_coder_32b_yosys_equiv_baseline.md`
- `rtlopt_synthesis_deepseek_coder`: `manual_summary` from `reports/rtlopt_deepseek_coder_v2_lite_instruct_yosys_equiv_baseline.md`
- `rtlopt_equivalence_qwen36_27b`: `manual_summary` from `reports/rtlopt_qwen36_27b_yosys_equiv_baseline.md`
- `rtlopt_equivalence_qwen36_35b_a3b`: `manual_summary` from `reports/rtlopt_qwen36_35b_a3b_yosys_equiv_baseline.md`
- `rtlopt_equivalence_qwen3_coder`: `manual_summary` from `reports/rtlopt_qwen3_coder_30b_a3b_instruct_yosys_equiv_baseline.md`
- `rtlopt_equivalence_qwen25_coder`: `manual_summary` from `reports/rtlopt_qwen25_coder_32b_yosys_equiv_baseline.md`
- `rtlopt_equivalence_deepseek_coder`: `manual_summary` from `reports/rtlopt_deepseek_coder_v2_lite_instruct_yosys_equiv_baseline.md`

## Warnings

- verilogeval_pass1_qwen36_27b: summary.json unavailable at outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b/summary.json; using manual_summary fallback
- verilogeval_pass1_qwen36_35b_a3b: summary.json unavailable at outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z/summary.json; using manual_summary fallback
- verilogeval_pass1_qwen3_coder: summary.json unavailable at outputs/verilogeval/qwen3-coder-30b-a3b/20260612T162441Z/summary.json; using manual_summary fallback
- verilogeval_pass1_qwen25_coder: summary.json unavailable at outputs/verilogeval/qwen25-coder-32b/20260612T210505Z/summary.json; using manual_summary fallback
- verilogeval_pass1_deepseek_coder: summary.json unavailable at outputs/verilogeval/deepseek-coder-v2-lite/20260613T045026Z/summary.json; using manual_summary fallback
- verilogeval_pass5_qwen36_27b: summary.json unavailable at outputs/verilogeval_v2_pass5/20260611T091009Z__verilogeval__qwen36-27b/summary.json; using manual_summary fallback
- verilogeval_pass5_qwen36_35b_a3b: summary.json unavailable at outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z/summary.json; using manual_summary fallback
- verilogeval_pass5_qwen3_coder: summary.json unavailable at outputs/verilogeval/qwen3-coder-30b-a3b/20260612T162949Z/summary.json; using manual_summary fallback
- verilogeval_pass5_qwen25_coder: summary.json unavailable at outputs/verilogeval/qwen25-coder-32b/20260612T230606Z/summary.json; using manual_summary fallback
- verilogeval_pass5_deepseek_coder: summary.json unavailable at outputs/verilogeval/deepseek-coder-v2-lite/20260613T093759Z/summary.json; using manual_summary fallback
- rtllm2_pass1_qwen36_27b: summary.json unavailable at outputs/rtllm2_pass1/20260611T133005Z__rtllm2__qwen36-27b/summary.json; using manual_summary fallback
- rtllm2_pass1_qwen36_35b_a3b: summary.json unavailable at outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z/summary.json; using manual_summary fallback
- rtllm2_pass1_qwen3_coder: summary.json unavailable at outputs/rtllm2/qwen3-coder-30b-a3b/20260612T183418Z/summary.json; using manual_summary fallback
- rtllm2_pass1_qwen25_coder: summary.json unavailable at outputs/rtllm2/qwen25-coder-32b/20260613T010701Z/summary.json; using manual_summary fallback
- rtllm2_pass1_deepseek_coder: summary.json unavailable at outputs/rtllm2/deepseek-coder-v2-lite/20260613T121930Z/summary.json; using manual_summary fallback
- protocollm_lint_qwen36_27b: summary.json unavailable at outputs/protocollm_lint_pass1/20260611T162344Z__protocollm__qwen36-27b/summary.json; using manual_summary fallback
- protocollm_lint_qwen36_35b_a3b: summary.json unavailable at outputs/protocollm/qwen36-35b-a3b/20260612T142333Z/summary.json; using manual_summary fallback
- protocollm_lint_qwen3_coder: summary.json unavailable at outputs/protocollm/qwen3-coder-30b-a3b/20260612T183655Z/summary.json; using manual_summary fallback
- protocollm_lint_qwen25_coder: summary.json unavailable at outputs/protocollm/qwen25-coder-32b/20260613T030734Z/summary.json; using manual_summary fallback
- protocollm_lint_deepseek_coder: summary.json unavailable at outputs/protocollm/deepseek-coder-v2-lite/20260613T143118Z/summary.json; using manual_summary fallback
- rtlopt_lint_qwen36_27b: summary.json unavailable at outputs/rtlopt_lint_pass1/20260612T045332Z__rtlopt__qwen36-27b/summary.json; using manual_summary fallback
- rtlopt_lint_qwen36_35b_a3b: summary.json unavailable at outputs/rtlopt/qwen36-35b-a3b/20260612T144142Z/summary.json; using manual_summary fallback
- rtlopt_lint_qwen3_coder: summary.json unavailable at outputs/rtlopt/qwen3-coder-30b-a3b/20260612T183843Z/summary.json; using manual_summary fallback
- rtlopt_lint_qwen25_coder: summary.json unavailable at outputs/rtlopt/qwen25-coder-32b/20260613T031037Z/summary.json; using manual_summary fallback
- rtlopt_lint_deepseek_coder: summary.json unavailable at outputs/rtlopt/deepseek-coder-v2-lite/20260613T150136Z/summary.json; using manual_summary fallback
- rtlopt_synthesis_qwen36_27b: summary.json unavailable at outputs/rtlopt_yosys_pass1/20260612T052731Z__rtlopt__qwen36-27b/summary.json; using manual_summary fallback
- rtlopt_synthesis_qwen36_35b_a3b: summary.json unavailable at outputs/rtlopt/qwen36-35b-a3b/20260612T144440Z/summary.json; using manual_summary fallback
- rtlopt_synthesis_qwen3_coder: summary.json unavailable at outputs/rtlopt/qwen3-coder-30b-a3b/20260612T184111Z/summary.json; using manual_summary fallback
- rtlopt_synthesis_qwen25_coder: summary.json unavailable at outputs/rtlopt/qwen25-coder-32b/20260613T031340Z/summary.json; using manual_summary fallback
- rtlopt_synthesis_deepseek_coder: summary.json unavailable at outputs/rtlopt/deepseek-coder-v2-lite/20260613T170218Z/summary.json; using manual_summary fallback
- rtlopt_equivalence_qwen36_27b: summary.json unavailable at outputs/rtlopt_equiv_pass1/20260612T060533Z__rtlopt__qwen36-27b/summary.json; using manual_summary fallback
- rtlopt_equivalence_qwen36_35b_a3b: summary.json unavailable at outputs/rtlopt/qwen36-35b-a3b/20260612T143022Z/summary.json; using manual_summary fallback
- rtlopt_equivalence_qwen3_coder: summary.json unavailable at outputs/rtlopt/qwen3-coder-30b-a3b/20260612T184318Z/summary.json; using manual_summary fallback
- rtlopt_equivalence_qwen25_coder: summary.json unavailable at outputs/rtlopt/qwen25-coder-32b/20260613T031649Z/summary.json; using manual_summary fallback
- rtlopt_equivalence_deepseek_coder: summary.json unavailable at outputs/rtlopt/deepseek-coder-v2-lite/20260613T190310Z/summary.json; using manual_summary fallback
