# ProtocolLLM Public Lint Qwen2.5-Coder-32B-Instruct Baseline

## Run

- Benchmark: ProtocolLLM public repository prompts
- Model preset: `qwen25-coder-32b`
- Served model ID: `qwen25-coder-32b`
- Endpoint: `http://lanta-g-017:8000/v1`
- Output: `outputs/protocollm/qwen25-coder-32b/20260613T030734Z`
- Evaluation mode: Verilator lint-only
- Tasks: 9
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Public lint pass rate: 6 / 9 = 0.6667
- Failure categories: `{"passed": 6, "compile_failure": 3}`

## Interpretation

This is lint-only and must not be counted as functional correctness. Under the same public lint condition, `qwen25-coder-32b` trails `qwen36-27b` and `qwen3-coder-30b-a3b-instruct`, but outperforms `qwen36-35b-a3b`.
