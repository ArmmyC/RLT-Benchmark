# VerilogEval v2 Qwen2.5-Coder-32B-Instruct Baseline

## Run

- Benchmark: VerilogEval v2 `dataset_spec-to-rtl`
- Model preset: `qwen25-coder-32b`
- Served model ID: `qwen25-coder-32b`
- Model repo: `Qwen/Qwen2.5-Coder-32B-Instruct`
- Endpoint: `http://lanta-g-017:8000/v1`
- Prompt condition: same neutral benchmark prompt as the previous public baselines
- Hidden thinking compatibility setting: `chat_template_kwargs.enable_thinking=false`
- Evaluator: Icarus Verilog functional simulation
- Date: 2026-06-13

## Smoke

- Output: `outputs/verilogeval/qwen25-coder-32b/20260612T210431Z`
- Tasks: 3
- Samples: 3
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 2048
- Result: 3 / 3 passed

## Pass@1

- Output: `outputs/verilogeval/qwen25-coder-32b/20260612T210505Z`
- Tasks: 156
- Samples: 156
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.8846
- Functional pass@1: 0.4487

Failure breakdown:

```json
{
  "passed": 70,
  "simulation_failure": 68,
  "compile_failure": 18
}
```

## Pass@5

- Output: `outputs/verilogeval/qwen25-coder-32b/20260612T230606Z`
- Tasks: 156
- Samples: 780
- Samples per task: 5
- Temperature: 0.6
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.8654
- Sample functional pass rate: 0.4577
- pass@5: 0.5385

Pass@k:

| Metric | Score |
|---|---:|
| pass@1 | 0.4577 |
| pass@2 | 0.4968 |
| pass@3 | 0.5167 |
| pass@4 | 0.5295 |
| pass@5 | 0.5385 |

Failure breakdown:

```json
{
  "passed": 357,
  "simulation_failure": 318,
  "compile_failure": 104,
  "code_extraction_failure": 1
}
```

## Output Artifacts

Each run folder contains:

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

Under identical VerilogEval v2 settings, `qwen25-coder-32b` has the highest syntax pass rate among the public baselines tested so far, but the lowest functional pass@1 and pass@5. The main issue is not extraction stability; it is functional simulation failure after syntactically valid RTL is produced.

This is a baseline result only. Prompt engineering or repair loops should be reported as separate benchmark conditions.
