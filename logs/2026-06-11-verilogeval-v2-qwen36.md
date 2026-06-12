# 2026-06-11 VerilogEval v2 Qwen3.6-27B Benchmark Log

## Context

- Host: Lanta via `ssh lanta`
- Remote benchmark directory: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark`
- Model endpoint: `http://lanta-g-013:8000/v1`
- Served model: `qwen36-27b`
- Benchmark: NVlabs VerilogEval v2, `dataset_spec-to-rtl`, 156 tasks
- Evaluator: Icarus Verilog 12.0 through the benchmark harness

## What We Built

- Created reusable `rtlbench` Python package.
- Added OpenAI-compatible model client.
- Added benchmark adapter interface.
- Added native VerilogEval v2 adapter for `_prompt.txt`, `_test.sv`, `_ref.sv` triples.
- Added RTL extraction, Icarus compile/sim evaluation, pass@k metrics, JSONL/JSON/CSV reports.
- Added Lanta setup and Slurm launch scripts.
- Added tests for extraction, metrics, evaluator helpers, native VerilogEval loading, and an end-to-end mocked model run through Icarus.

## Findings

- The official VerilogEval v2 dataset is not JSONL-only. It is distributed as prompt/test/reference triples under `dataset_spec-to-rtl`.
- The official testbenches instantiate generated `TopModule` plus golden `RefModule`, so the evaluator must compile support files with each generated sample.
- Qwen initially returned blank final content on some short tasks while consuming the full `max_tokens=2048`. This was caused by hidden thinking consuming the completion budget.
- Disabling Qwen thinking through vLLM chat template kwargs fixed the empty response issue:

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

## Runs

### Smoke Test

- Output: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark/outputs/smoke/20260611T084916Z__verilogeval__qwen36-27b`
- Result: 1/1 passed

### Initial 20-Task Sanity

- Output: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark/outputs/verilogeval_v2_sanity/20260611T085903Z__verilogeval__qwen36-27b`
- Result: 14/20 passed
- Failure mode: 6 empty responses

### 20-Task Sanity With Thinking Disabled

- Output: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark/outputs/verilogeval_v2_sanity_no_thinking/20260611T090404Z__verilogeval__qwen36-27b`
- Result: 20/20 passed
- Finding: empty responses disappeared

### Full Pass@1

- Output: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark/outputs/verilogeval_v2_pass1/20260611T090440Z__verilogeval__qwen36-27b`
- Samples: 156
- Tasks: 156
- Syntax pass rate: 0.8397
- Functional pass rate / pass@1: 0.6154
- Failures:
  - compile_failure: 17
  - simulation_failure: 35
  - code_extraction_failure: 8

### Full Pass@5

- Output: `/project/zz992000-zdevb/zz992005/ub127/SiliconCraft/benchmark/outputs/verilogeval_v2_pass5/20260611T091009Z__verilogeval__qwen36-27b`
- Samples: 780
- Tasks: 156
- Passed samples: 477
- Syntax pass rate: 0.7962
- Functional sample pass rate: 0.6115
- pass@1: 0.6115
- pass@2: 0.6910
- pass@3: 0.7327
- pass@4: 0.7577
- pass@5: 0.7756
- Failures:
  - compile_failure: 104
  - simulation_failure: 144
  - code_extraction_failure: 55

## Next Notes

- Inspect code extraction failures first; they may be recoverable harness-side.
- Compare pass@1 run and pass@5 sample-0 behavior to ensure temperature changes are the main difference.
- Add a `--notes` CLI option so future runs can record experiment intent directly in the run report.
