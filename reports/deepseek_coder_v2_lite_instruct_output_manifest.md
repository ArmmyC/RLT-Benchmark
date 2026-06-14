# DeepSeek-Coder-V2-Lite-Instruct Output Manifest

## Git Tracking Policy

The raw benchmark output folders are not committed to Git.

Reason:

- `outputs/` is intentionally ignored by `.gitignore`.
- Run outputs contain raw model responses, extracted RTL, logs, and generated work directories.
- The committed artifacts are configs and reports that point to the authoritative Lanta output folders.

## Model Identity

- Model preset: `deepseek-coder-v2-lite-instruct`
- Served model ID: `deepseek-coder-v2-lite`
- Model repo: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`

## Lanta Output Folders

| Benchmark / Mode | Output folder | Comparison status |
|---|---|---|
| VerilogEval smoke | `outputs/verilogeval/deepseek-coder-v2-lite/20260613T044942Z` | Smoke only |
| VerilogEval pass@1 | `outputs/verilogeval/deepseek-coder-v2-lite/20260613T045026Z` | Used |
| VerilogEval pass@5 incomplete attempt | `outputs/verilogeval/deepseek-coder-v2-lite/20260613T065118Z` | Preserved, not compared |
| VerilogEval pass@5 retry | `outputs/verilogeval/deepseek-coder-v2-lite/20260613T093759Z` | Used |
| RTLLM 2.0 pass@1 | `outputs/rtllm2/deepseek-coder-v2-lite/20260613T121930Z` | Used |
| ProtocolLLM endpoint-failure attempt | `outputs/protocollm/deepseek-coder-v2-lite/20260613T142014Z` | Preserved, not compared |
| ProtocolLLM public lint retry | `outputs/protocollm/deepseek-coder-v2-lite/20260613T143118Z` | Used |
| RTL-OPT lint | `outputs/rtlopt/deepseek-coder-v2-lite/20260613T150136Z` | Used |
| RTL-OPT generic synthesis | `outputs/rtlopt/deepseek-coder-v2-lite/20260613T170218Z` | Used |
| RTL-OPT equivalence | `outputs/rtlopt/deepseek-coder-v2-lite/20260613T190310Z` | Used |

Each completed run folder contains the AGENTS-required artifacts:

```text
config_snapshot.yaml
run_metadata.json
report.md
results.jsonl
summary.json
summary.csv
raw_responses/
extracted_rtl/
logs/
error_logs/
```

The incomplete VerilogEval pass@5 attempt is missing `results.jsonl`, `summary.json`, and `summary.csv`; it is not used in any comparison.

The failed ProtocolLLM endpoint attempt contains completed failure artifacts, but it records endpoint unavailability rather than model quality; it is not used in the comparison.

## Committed Report Files

```text
reports/verilogeval_v2_deepseek_coder_v2_lite_instruct_baseline.md
reports/rtllm2_deepseek_coder_v2_lite_instruct_baseline.md
reports/protocollm_deepseek_coder_v2_lite_instruct_public_lint_baseline.md
reports/rtlopt_deepseek_coder_v2_lite_instruct_yosys_equiv_baseline.md
reports/deepseek_coder_v2_lite_instruct_output_manifest.md
reports/qwen36_27b_vs_qwen36_35b_a3b_verilogeval.md
reports/qwen36_27b_vs_qwen36_35b_a3b_public_benchmarks.md
```
