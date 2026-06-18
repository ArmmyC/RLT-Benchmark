# Fine-Tuning Boundary

RTLBench is an evaluation harness, not a fine-tuning repository.

## RTLBench Owns

- public/synthetic benchmark definitions
- task manifests
- adapters
- extraction, compile, simulation, synthesis, timing, area, and activity gates
- scoring code
- sanitized reports and summaries
- unit tests using synthetic fixtures

RTLBench may contain public/synthetic reference RTL and testbenches when they are part of a benchmark task.

## RTLBench Must Not Contain

- private RTL or private task text
- raw prompts or raw model responses
- generated RTL from benchmark runs
- VCDs, simulator logs, synthesis logs, compiled artifacts, or raw output folders
- secrets or endpoint credentials
- datasets, adapters, checkpoints, or model weights
- LoRA, QLoRA, DoRA, or other fine-tuning scripts/artifacts

## Future Training Work

Any future fine-tuning project should live in a separate repository or storage boundary. It may call RTLBench as an evaluator after the benchmark, scoring schema, and sanitized output contracts are stable.

Public/synthetic RFID-APBench evidence is useful evaluation data, but it is not fine-tuning readiness evidence by itself.
