# RTLLM 2.0 Qwen3-Coder-30B-A3B-Instruct Baseline

## Run

- Benchmark: RTLLM 2.0 public benchmark
- Model preset: `qwen3-coder-30b-a3b-instruct`
- Served model ID: `qwen3-coder-30b-a3b`
- Endpoint: `http://lanta-g-028:8000/v1`
- Output: `outputs/rtllm2/qwen3-coder-30b-a3b/20260612T183418Z`
- Evaluator: Icarus Verilog functional simulation
- Tasks: 50
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Syntax pass rate: 0.6600
- Functional pass@1: 0.5000

Failure breakdown:

```json
{
  "passed": 25,
  "simulation_failure": 8,
  "compile_failure": 17
}
```

## Interpretation

Under the same RTLLM 2.0 settings as the qwen36 baselines, `qwen3-coder-30b-a3b-instruct` trails both qwen36 models on functional pass@1 and syntax pass rate. The dominant failure mode is compile failure.
