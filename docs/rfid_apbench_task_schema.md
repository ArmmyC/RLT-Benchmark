# RFID-APBench Task Schema

RFID-APBench tasks are public/synthetic RTL benchmark assets. They must be safe to commit and must not contain private RTL, private task text, raw model outputs, training data, adapters, secrets, or model weights.

## Directory Shape

```text
benchmarks/rfid_apbench/
  manifest.yaml
  tasks/
    <task_id>/
      task.yaml
      prompt.md
      reference.sv
      testbench.sv
      activity_workload.yaml
      constraints.sdc                 optional
      expected/
        reference_metrics.yaml
```

## Required Task Metadata

Each `task.yaml` should identify:

- `task_id`
- `public_synthetic: true`
- `top_module`
- correctness method and testbench
- synthesis flow and top module
- timing requirement
- activity workload and metric
- reference metrics file

Task IDs use the form `ap_NNN_short_name`.

## Required Task Assets

- `prompt.md`: public model-facing task text only.
- `reference.sv`: public synthetic reference RTL matching the prompt.
- `testbench.sv`: deterministic self-checking public testbench.
- `activity_workload.yaml`: declared workload and VCD measurement window.
- `expected/reference_metrics.yaml`: sanitized reference area/activity metrics.

## Evaluation Gates

The evaluator records:

1. extraction
2. compile
3. functional simulation
4. synthesis
5. timing when required
6. area metric availability
7. activity metric availability

Commit-safe outputs are sanitized Markdown, CSV, and JSONL summaries. Raw responses, generated RTL, VCDs, logs, compiled artifacts, secrets, datasets, adapters, and model weights must stay out of the repository.
