# RTLLM 2.0 DeepSeek-Coder-V2-Lite-Instruct Baseline

## Run

- Benchmark: RTLLM 2.0 public benchmark
- Model preset: `deepseek-coder-v2-lite-instruct`
- Served model ID: `deepseek-coder-v2-lite`
- Model repo: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- Endpoint: Lanta vLLM OpenAI-compatible API
- Output: `outputs/rtllm2/deepseek-coder-v2-lite/20260613T121930Z`
- Evaluator: Icarus Verilog functional simulation
- Date: 2026-06-13
- Tasks: 50
- Samples: 50
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Syntax pass rate: 0.7800
- Functional pass@1: 0.5200

Failure breakdown:

```json
{
  "passed": 26,
  "simulation_failure": 13,
  "compile_failure": 11
}
```

## Output Artifacts

The run folder contains:

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

`deepseek-coder-v2-lite-instruct` reaches the same RTLLM 2.0 syntax pass rate as `qwen36-35b-a3b`, but lower functional correctness than both Qwen3.6 baselines and `qwen25-coder-32b`. It is above `qwen3-coder-30b-a3b-instruct` on this benchmark.
