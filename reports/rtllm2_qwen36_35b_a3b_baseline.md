# RTLLM 2.0 Qwen36-35B-A3B Baseline

## Run

- Benchmark: RTLLM 2.0 public benchmark
- Model: `qwen36-35b-a3b`
- Endpoint: `http://lanta-g-034:8000/v1`
- Output: `outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z`
- Evaluator: Icarus Verilog functional simulation
- Tasks: 50
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 4096

## Results

- Syntax pass rate: 0.7800
- Functional pass@1: 0.6000

Failure breakdown:

```json
{
  "passed": 30,
  "simulation_failure": 8,
  "compile_failure": 10,
  "code_extraction_failure": 1,
  "timeout": 1
}
```

Detailed analyses:

```text
outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z/logs/code_extraction_failure_analysis.md
outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z/logs/compile_failure_analysis.md
outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z/logs/simulation_failure_analysis.md
outputs/rtllm2/qwen36-35b-a3b/20260612T141752Z/logs/timeout_analysis.md
```

## Interpretation

`qwen36-35b-a3b` matches the existing `qwen36-27b` RTLLM 2.0 functional pass@1 score at 0.6000, while improving syntax pass rate from 0.7000 to 0.7800. The failure mix shifts from more compile failures in the 27B run to more simulation failures in the 35B-A3B run.
