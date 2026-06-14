# ProtocolLLM Public Lint DeepSeek-Coder-V2-Lite-Instruct Baseline

## Run

- Benchmark: ProtocolLLM public repository prompts
- Model preset: `deepseek-coder-v2-lite-instruct`
- Served model ID: `deepseek-coder-v2-lite`
- Model repo: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- Endpoint: Lanta vLLM OpenAI-compatible API
- Output: `outputs/protocollm/deepseek-coder-v2-lite/20260613T143118Z`
- Evaluation mode: Verilator lint-only
- Date: 2026-06-13
- Tasks: 9
- Samples: 9
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Public lint pass rate: 6 / 9 = 0.6667
- Failure categories: `{"passed": 6, "compile_failure": 3}`

## Failed Endpoint Attempt

The earlier attempt at `outputs/protocollm/deepseek-coder-v2-lite/20260613T142014Z` failed because the previous vLLM job had reached the Slurm time limit and the endpoint refused connections. That run is preserved as an endpoint failure and is not used as model-quality evidence.

## Output Artifacts

The valid retry run folder contains:

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

This is lint-only and must not be counted as functional correctness. Under the same public lint condition, `deepseek-coder-v2-lite-instruct` ties `qwen25-coder-32b`, trails `qwen36-27b` and `qwen3-coder-30b-a3b-instruct`, and beats `qwen36-35b-a3b`.
