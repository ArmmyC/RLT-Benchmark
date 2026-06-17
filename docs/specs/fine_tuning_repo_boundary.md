# Fine-Tuning Repository Boundary

## Purpose

This document defines the boundary between RTLBench and a future fine-tuning repository.

RTLBench is the benchmark and evaluation foundation. A future fine-tuning repository may call into RTLBench after RFID-APBench is mature enough, but training code and training artifacts must not be added to RTLBench.

## Decision

Fine-tuning is gated on an RFID-APBench MVP that can score 5 to 10 public/synthetic RFID/NFC-style area/activity tasks end-to-end.

Until that gate is met, the work stays in RTLBench as benchmark planning, task schema design, evaluation gates, scoring design, sanitized artifacts, and reports.

## RTLBench Owns

RTLBench owns:

- benchmark definitions
- public/synthetic task folders
- benchmark manifests
- adapters
- extraction, compile, correctness, synthesis, timing, area, and activity gates
- `area_activity` scoring
- VCD toggle-count activity proxy evaluation
- sanitized result artifacts
- aggregate summaries
- honest reports

RTLBench may contain public/synthetic reference RTL and public testbenches when they are part of a benchmark task. It must not contain private RTL or private task text.

## Future Fine-Tuning Repo Owns

A future fine-tuning repository owns:

- dataset construction from public or sanitized artifacts
- QLoRA scripts
- DoRA scripts
- other training scripts
- training configuration
- adapters and checkpoints
- model routing experiments
- post-training evaluation orchestration that calls into RTLBench

The fine-tuning repo should treat RTLBench as an evaluator, not as a place to store training datasets or model artifacts.

## Forbidden In RTLBench

Do not commit these to RTLBench:

- private RTL
- private task text
- raw prompts
- raw model responses
- generated RTL
- benchmark outputs
- logs
- error logs
- secrets
- model weights
- training datasets
- LoRA adapters
- QLoRA adapters
- DoRA adapters
- fine-tuning checkpoints
- private evaluation traces

This rule applies even when artifacts are useful for debugging. Keep raw and private materials outside the repository or under a separately approved storage policy.

## Allowed In RTLBench

Allowed RTLBench artifacts include:

- public/synthetic task specs
- public/synthetic reference RTL
- public/synthetic testbenches
- public manifests
- scoring code
- export code for sanitized fields
- sanitized JSONL/CSV summaries
- markdown reports
- schema documentation
- unit tests using synthetic fixtures

Allowed artifacts must still avoid secrets, raw model responses, raw prompts, private paths, private task text, and generated RTL from benchmark runs.

## Evaluation Interface

The future fine-tuning repo should call RTLBench through stable CLI or Python interfaces that:

- select a benchmark and task subset
- provide a model endpoint or local model adapter through environment variables
- run evaluation gates
- compute sanitized scores
- emit sanitized summaries

Environment variables should be used for endpoint configuration and secrets. Do not hardcode API keys, endpoint URLs, passwords, or absolute private paths in source files.

## Sanitized Dataset Boundary

Sanitized RTLBench artifacts may be used as inputs to future dataset construction only after review.

Sanitized records may include:

- task id
- public benchmark id
- gate outcomes
- failure category
- area/activity metrics
- score fields
- toolchain id
- workload id
- prompt profile label
- model label

Sanitized records must not include:

- raw prompt text
- raw response text
- generated RTL
- private RTL
- private task text
- VCD contents
- logs
- paths to raw artifacts
- secrets

If a future training dataset needs prompt/response pairs, that dataset belongs in the fine-tuning repo or external dataset storage, not in RTLBench.

## Readiness Gate

Fine-tuning may begin only after an RFID-APBench MVP demonstrates:

1. 5 to 10 public/synthetic tasks exist.
2. Each task has a public folder schema and deterministic correctness workload.
3. The evaluator records extraction, compile, simulation or equivalence, synthesis, timing-if-required, area metric availability, and activity metric availability.
4. `area_activity` scoring is implemented and tested.
5. VCD toggle-count activity flow is implemented and deterministic.
6. Sanitized result exports contain no raw/private/training artifacts.
7. Reports clearly state that activity is a toggle-count proxy, not measured silicon power.

Before this gate, training experiments risk optimizing against an unstable or incomplete measurement target.

## Handoff Contract

When the gate is met, RTLBench should expose:

- benchmark version or commit hash
- task ids and schema version
- scoring schema version
- CLI or Python evaluator entry point
- expected sanitized output schema
- known limitations

The future fine-tuning repo should record:

- dataset source and filtering rules
- training method
- adapter/checkpoint locations outside RTLBench
- post-training evaluation calls into RTLBench
- comparison settings and benchmark versions

## Current Status

As of v0.5 planning, fine-tuning is not ready to start. RFID-APBench still needs its public/synthetic MVP and end-to-end scoring flow.

No training code, private data, model weights, training datasets, or adapter checkpoints should be added to RTLBench for this milestone.
