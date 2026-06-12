# ProtocolLLM Public Lint Qwen36-35B-A3B Baseline

## Run

- Benchmark: ProtocolLLM public repository prompts
- Model: `qwen36-35b-a3b`
- Endpoint: `http://lanta-g-034:8000/v1`
- Output: `outputs/protocollm/qwen36-35b-a3b/20260612T142333Z`
- Evaluation mode: Verilator lint-only
- Tasks: 9
- Samples per task: 1

## Results

- Public lint pass rate: 2 / 9 = 0.2222
- Failure categories: `{"passed": 2, "compile_failure": 4, "code_extraction_failure": 3}`

Detailed analyses:

```text
outputs/protocollm/qwen36-35b-a3b/20260612T142333Z/logs/code_extraction_failure_analysis.md
outputs/protocollm/qwen36-35b-a3b/20260612T142333Z/logs/compile_failure_analysis.md
```

## Interpretation

This is lint-only and must not be counted as functional correctness. Under the same public lint condition, `qwen36-35b-a3b` performs substantially worse than `qwen36-27b` on ProtocolLLM public prompts.
