# ProtocolLLM Public Lint Qwen3-Coder-30B-A3B-Instruct Baseline

## Run

- Benchmark: ProtocolLLM public repository prompts
- Model preset: `qwen3-coder-30b-a3b-instruct`
- Served model ID: `qwen3-coder-30b-a3b`
- Endpoint: `http://lanta-g-028:8000/v1`
- Output: `outputs/protocollm/qwen3-coder-30b-a3b/20260612T183655Z`
- Evaluation mode: Verilator lint-only
- Tasks: 9
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Public lint pass rate: 7 / 9 = 0.7778
- Failure categories: `{"passed": 7, "compile_failure": 2}`

## Interpretation

This is lint-only and must not be counted as functional correctness. Under the same public lint condition, `qwen3-coder-30b-a3b-instruct` matches the `qwen36-27b` lint pass rate and outperforms `qwen36-35b-a3b`.
