# VerilogEval v2 Qwen36-35B-A3B Baseline

## Run

- Benchmark: VerilogEval v2 `dataset_spec-to-rtl`
- Model: `qwen36-35b-a3b`
- Endpoint: `http://lanta-g-034:8000/v1`
- Prompt condition: same neutral benchmark prompt as `qwen36-27b`
- Hidden thinking: disabled with `chat_template_kwargs.enable_thinking=false`
- Evaluator: Icarus Verilog functional simulation

## Smoke

- Output: `outputs/verilogeval/qwen36-35b-a3b/20260612T125544Z`
- Tasks: 3
- Samples: 3
- Result: 3 / 3 passed

## Pass@1

- Output: `outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z`
- Tasks: 156
- Samples per task: 1
- Temperature: 0.2
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.7564
- Functional pass@1: 0.5705

Failure breakdown:

```json
{
  "passed": 89,
  "simulation_failure": 29,
  "compile_failure": 26,
  "code_extraction_failure": 12
}
```

Diagnosis highlights:

- Extraction failures: 10 truncated reasoning/comment outputs, 2 no-module outputs.
- Compile failures: 12 procedural assignment-to-wire-output, 3 procedural-code-outside-always, 2 syntax errors, 2 wrong/undefined submodule, 6 other compile errors, 1 known benchmark artifact.
- Simulation failures: mostly FSM/protocol and sequential timing/state errors.

Detailed analyses:

```text
outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z/logs/code_extraction_failure_analysis.md
outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z/logs/compile_failure_analysis.md
outputs/verilogeval/qwen36-35b-a3b/20260612T125618Z/logs/simulation_failure_analysis.md
```

## Pass@5

- Output: `outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z`
- Tasks: 156
- Samples: 780
- Samples per task: 5
- Temperature: 0.6
- Top-p: 0.95
- Max tokens: 2048
- Syntax pass rate: 0.7449
- Sample functional pass rate: 0.5615
- pass@5: 0.7308

Failure breakdown:

```json
{
  "passed": 438,
  "simulation_failure": 143,
  "compile_failure": 121,
  "code_extraction_failure": 78
}
```

Detailed analyses:

```text
outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z/logs/code_extraction_failure_analysis.md
outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z/logs/compile_failure_analysis.md
outputs/verilogeval/qwen36-35b-a3b/20260612T132806Z/logs/simulation_failure_analysis.md
```

## Interpretation

Under identical VerilogEval v2 settings, `qwen36-35b-a3b` is functional but trails the existing `qwen36-27b` baseline on both pass@1 and pass@5. The main regression is syntax/compile reliability and extraction stability, not just simulation behavior.
