# Qwen2.5-Coder-32B-Instruct Output Manifest

## Git Tracking Policy

The raw benchmark output folders are not committed to Git.

Reason:

- `outputs/` is intentionally ignored by `.gitignore`.
- Run outputs contain raw model responses, extracted RTL, logs, and generated work directories.
- The committed artifacts are configs and reports that point to the authoritative Lanta output folders.

## Lanta Output Folders

| Benchmark / Mode | Output folder |
|---|---|
| VerilogEval smoke | `outputs/verilogeval/qwen25-coder-32b/20260612T210431Z` |
| VerilogEval pass@1 | `outputs/verilogeval/qwen25-coder-32b/20260612T210505Z` |
| VerilogEval pass@5 | `outputs/verilogeval/qwen25-coder-32b/20260612T230606Z` |
| RTLLM 2.0 pass@1 | `outputs/rtllm2/qwen25-coder-32b/20260613T010701Z` |
| ProtocolLLM public lint | `outputs/protocollm/qwen25-coder-32b/20260613T030734Z` |
| RTL-OPT lint | `outputs/rtlopt/qwen25-coder-32b/20260613T031037Z` |
| RTL-OPT generic synthesis | `outputs/rtlopt/qwen25-coder-32b/20260613T031340Z` |
| RTL-OPT equivalence | `outputs/rtlopt/qwen25-coder-32b/20260613T031649Z` |

Each run folder contains the AGENTS-required artifacts:

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

## Committed Report Files

```text
reports/verilogeval_v2_qwen25_coder_32b_baseline.md
reports/rtllm2_qwen25_coder_32b_baseline.md
reports/protocollm_qwen25_coder_32b_public_lint_baseline.md
reports/rtlopt_qwen25_coder_32b_yosys_equiv_baseline.md
reports/qwen25_coder_32b_output_manifest.md
```
