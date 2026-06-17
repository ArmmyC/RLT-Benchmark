# RFID-APBench Task Schema

## Purpose

This document defines the public/synthetic task folder schema for RFID-APBench.

RFID-APBench tasks are benchmark assets for RFID/NFC-style RTL area plus activity evaluation. They must be public, synthetic, and safe to commit. They must not contain private RTL, private task text, customer details, raw model outputs, training data, or adapter artifacts.

## Task Root

Proposed benchmark root:

```text
benchmarks/rfid_apbench/
  README.md
  manifest.yaml
  tasks/
    <task_id>/
      task.yaml
      prompt.md
      reference.sv
      testbench.sv
      constraints.sdc
      activity_workload.yaml
      expected/
        reference_metrics.yaml
```

`constraints.sdc` is optional when a task does not require timing. `expected/reference_metrics.yaml` may be generated later by a controlled reference-metric build, but committed values must be sanitized and public.

## Task ID Rules

Task ids should use:

```text
ap_NNN_short_name
```

Initial reserved ids:

- `ap_001_idle_counter`
- `ap_002_command_decoder`
- `ap_003_register_bank_unnecessary_writes`
- `ap_004_crc_serial_parallel_tradeoff`
- `ap_005_fsm_controller_idle_activity`

## `manifest.yaml`

The benchmark manifest should list public tasks and shared settings.

Suggested fields:

```yaml
schema_version: "rfid_apbench_manifest/v0.1"
benchmark: rfid_apbench
description: Public/synthetic RFID/NFC-style area/activity benchmark.
scoring_mode: area_activity
activity_definition: vcd_toggle_count_proxy
tasks:
  - task_id: ap_001_idle_counter
    path: tasks/ap_001_idle_counter
```

The manifest must not include private paths, internal URLs, secrets, or private dataset references.

## `task.yaml`

Each task should define the behavioral contract and evaluation settings.

Suggested fields:

```yaml
schema_version: "rfid_apbench_task/v0.1"
task_id: ap_001_idle_counter
title: Idle counter
domain: rfid_nfc_synthetic
public_synthetic: true
top_module: idle_counter
language: systemverilog
interfaces:
  clock: clk
  reset: rst_n
correctness:
  method: simulation
  testbench: testbench.sv
synthesis:
  flow_id: yosys_generic
  top_module: idle_counter
timing:
  required: false
  constraint_file: null
activity:
  workload: activity_workload.yaml
  metric: total_signal_toggles
  vcd_window:
    start_cycle: 2
    end_cycle: 100
reference_metrics:
  file: expected/reference_metrics.yaml
forbidden_artifacts:
  - private_rtl
  - private_task_text
  - raw_prompts
  - raw_model_responses
  - generated_rtl
  - outputs
  - logs
  - secrets
  - model_weights
  - training_datasets
  - lora_adapters
```

Required semantic fields:

- `task_id`
- `public_synthetic: true`
- `top_module`
- `correctness.method`
- `synthesis.flow_id`
- `timing.required`
- `activity.workload`
- `activity.metric`

## `prompt.md`

The prompt file should contain only public benchmark instructions for the model-facing task.

It should describe:

- module name
- ports
- required behavior
- reset behavior
- latency expectations
- disallowed behavior if needed
- output format expectations

It must not contain:

- private RFID/NFC product details
- private task text
- hidden internal design constraints
- secrets
- references to private repositories
- raw prompts from previous model runs

## `reference.sv`

The reference design is the public baseline used for correctness and reference metrics.

Rules:

- must be synthetic and commit-safe
- must match the public prompt behavior
- must not be copied or derived from private RTL
- should be small enough for transparent review
- should favor clarity over hand-optimized tricks unless the task explicitly defines the reference as an optimized baseline

## `testbench.sv`

The testbench should provide deterministic correctness checking.

It should include:

- reset sequence
- public stimulus
- self-checking assertions or scoreboard checks
- deterministic pass/fail termination
- VCD dump hooks or a stable interface for the evaluator to enable dumps

It must not print private data, raw prompts, generated RTL, or internal paths.

## `activity_workload.yaml`

The activity workload declares the toggle-count measurement scenario.

Suggested fields:

```yaml
schema_version: "rfid_apbench_activity/v0.1"
workload_id: ap_001_default_idle_window
clock: clk
reset: rst_n
measurement_window:
  start_cycle: 2
  end_cycle: 100
stimulus:
  type: deterministic
  description: Public reset, idle, active, and return-to-idle sequence.
vcd:
  include_scope: top
  exclude_signals:
    - clk
activity_metric: total_signal_toggles
```

The workload must be identical for reference and generated RTL. If signal exclusions are used, they must be public and declared.

## `expected/reference_metrics.yaml`

Reference metrics should be sanitized structured values.

Suggested fields:

```yaml
schema_version: "rfid_apbench_reference_metrics/v0.1"
task_id: ap_001_idle_counter
toolchain_id: yosys_generic_iverilog_vcd_v0
area:
  value: 123.0
  unit: generic_cells
activity:
  value: 456.0
  metric: total_signal_toggles
timing:
  required: false
  status: not_required
```

Do not commit raw synthesis logs, VCD files, simulator logs, generated RTL, or raw output directories as reference-metric evidence.

## Initial Task Proposal Requirements

Every task proposal must include these human-readable sections before implementation:

- behavior
- optimization opportunity
- correctness gate
- area/activity expectations
- timing requirement
- RFID/NFC relevance

The initial proposals are documented in `docs/experiments/v0.5_rfid_apbench_planning.md`.

## Pass/Fail Gates

The evaluator must record:

1. extraction
2. compile
3. simulation or equivalence
4. synthesis
5. timing if required
6. area metric availability
7. activity metric availability

Allowed failure categories include:

- `code_extraction_failure`
- `compile_failure`
- `simulation_failure`
- `equiv_failure`
- `synthesis_failure`
- `timing_failure`
- `area_metric_unavailable`
- `activity_metric_unavailable`
- `timeout`
- `passed`

## Sanitized Output Contract

Commit-safe RFID-APBench outputs may include:

- sanitized JSONL rows
- sanitized CSV summaries
- markdown reports
- schema snapshots
- aggregate gate counts
- aggregate area/activity score statistics

They must not include:

- private RTL
- private task text
- raw prompts
- raw model responses
- generated RTL
- VCD files
- outputs
- logs or error logs
- secrets
- model weights
- training datasets
- LoRA, QLoRA, or DoRA adapters

## Fine-Tuning Readiness Gate

RFID-APBench must score 5 to 10 public/synthetic tasks end-to-end before any fine-tuning project uses it as an evaluation dependency.

The gate requires:

- all seven gates recorded per sample
- valid reference and generated area metrics for passing samples
- valid reference and generated activity metrics for passing samples
- sanitized reports
- no private, raw, output, log, or training artifacts committed

Training code and training artifacts do not belong in RTLBench.
