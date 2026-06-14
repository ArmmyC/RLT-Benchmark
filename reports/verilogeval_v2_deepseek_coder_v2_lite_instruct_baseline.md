# VerilogEval v2 DeepSeek-Coder-V2-Lite-Instruct Baseline

## Run

- Benchmark: VerilogEval v2 `dataset_spec-to-rtl`
- Model preset: `deepseek-coder-v2-lite-instruct`
- Served model ID: `deepseek-coder-v2-lite`
- Model repo: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- Endpoint: Lanta vLLM OpenAI-compatible API
- Prompt condition: same neutral benchmark prompt as the previous public baselines
- Evaluator: Icarus Verilog functional simulation
- Date: 2026-06-13

## Smoke

- Output: `outputs/verilogeval/deepseek-coder-v2-lite/20260613T044942Z`
- Tasks: 3
- Samples: 3
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 2048
- Result: 3 / 3 passed

## Pass@1

- Output: `outputs/verilogeval/deepseek-coder-v2-lite/20260613T045026Z`
- Tasks: 156
- Samples: 156
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.8590
- Functional pass@1: 0.4872

Failure breakdown:

```json
{
  "passed": 76,
  "simulation_failure": 58,
  "compile_failure": 21,
  "code_extraction_failure": 1
}
```

## Pass@5

- Output: `outputs/verilogeval/deepseek-coder-v2-lite/20260613T093759Z`
- Tasks: 156
- Samples: 780
- Samples per task: 5
- Temperature: 0.6
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.8551
- Sample functional pass rate: 0.4821
- pass@5: 0.5641

Pass@k:

| Metric | Score |
|---|---:|
| pass@1 | 0.4821 |
| pass@2 | 0.5263 |
| pass@3 | 0.5455 |
| pass@4 | 0.5564 |
| pass@5 | 0.5641 |

Failure breakdown:

```json
{
  "passed": 376,
  "simulation_failure": 291,
  "compile_failure": 111,
  "code_extraction_failure": 2
}
```

## Incomplete Attempt

The first pass@5 attempt at `outputs/verilogeval/deepseek-coder-v2-lite/20260613T065118Z` produced raw/extracted/error artifacts but did not produce `results.jsonl`, `summary.json`, or `summary.csv`. It is preserved as an incomplete run and is not used in comparisons.

## Output Artifacts

The smoke, pass@1, and valid pass@5 run folders contain:

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

## Interpretation

Under identical VerilogEval v2 settings, `deepseek-coder-v2-lite-instruct` trails both Qwen3.6 baselines on functional pass@1 and pass@5. It is slightly above `qwen3-coder-30b-a3b-instruct` on pass@1 functional correctness, slightly below it on pass@5 task recovery, and above `qwen25-coder-32b` on both functional metrics.

This is a baseline result only. Prompt engineering, repair loops, or alternate extraction logic should be reported as separate benchmark conditions.
