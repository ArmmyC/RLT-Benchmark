# RTLLM 2.0 Qwen2.5-Coder-32B-Instruct Baseline

## Run

- Benchmark: RTLLM 2.0 public benchmark
- Model preset: `qwen25-coder-32b`
- Served model ID: `qwen25-coder-32b`
- Endpoint: `http://lanta-g-017:8000/v1`
- Output: `outputs/rtllm2/qwen25-coder-32b/20260613T010701Z`
- Evaluator: Icarus Verilog functional simulation
- Tasks: 50
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Syntax pass rate: 0.7400
- Functional pass@1: 0.5400

Failure breakdown:

```json
{
  "passed": 27,
  "simulation_failure": 9,
  "compile_failure": 13,
  "timeout": 1
}
```

## Interpretation

Under the same RTLLM 2.0 settings as the previous public baselines, `qwen25-coder-32b` is below both qwen36 models on functional pass@1, but above `qwen3-coder-30b-a3b-instruct`. Its syntax pass rate is also below both qwen36 models and above qwen3-coder.
