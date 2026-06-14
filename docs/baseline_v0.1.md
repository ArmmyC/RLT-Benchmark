# Baseline v0.1 Reproducibility Package

Baseline v0.1 is the frozen, five-model public RTL benchmark snapshot registered in `runs/index.yaml`. The registry is the source of truth for selected runs, generation settings, output locations, source reports, and summary values.

## Included Models

- `qwen36-27b`
- `qwen36-35b-a3b`
- `qwen3-coder-30b-a3b-instruct`
- `qwen25-coder-32b`
- `deepseek-coder-v2-lite-instruct`

## Included Benchmarks

- VerilogEval v2 functional simulation, pass@1 and pass@5
- RTLLM 2.0 functional simulation, pass@1
- ProtocolLLM public lint-only
- RTL-OPT lint-only, generic synthesis-only, and Yosys equivalence

These evaluation kinds are deliberately separated. Lint is not functional correctness, synthesis is not behavior preservation, and generic cell counts are not final silicon PPA.

## Registry and Fallback Data

Each selected run records its model, served model alias, benchmark/mode, sampling settings, evaluator, output path, and committed source report. The current checkout does not contain `outputs/`, so Baseline v0.1 uses `manual_summary` values explicitly transcribed from committed reports and manifests.

When a registered `summary_path` is available, the registry loader reads `summary.json` and overrides the manual fallback. When it is unavailable, the loader emits a warning and uses `manual_summary`. If neither source exists, generation fails.

`results.jsonl` is optional for summary reporting. The failure-matrix generator analyzes only accessible registered files and produces an explicit empty state when per-task data is unavailable.

## Regenerate the Package

Run from the repository root:

```bash
python scripts/generate_comparison_report.py --registry runs/index.yaml --baseline baseline_v0_1
python scripts/analyze_cross_model_failures.py --registry runs/index.yaml --baseline baseline_v0_1
python scripts/build_dashboard.py --registry runs/index.yaml --baseline baseline_v0_1
python -m pytest
```

Generated artifacts:

```text
reports/baseline_v0.1_public_rtl_benchmarks.md
reports/baseline_v0.1_public_rtl_benchmarks.json
reports/baseline_v0.1_public_rtl_benchmarks.csv
reports/baseline_v0.1_failure_matrix.md
reports/baseline_v0.1_failure_matrix.csv
dashboard/index.html
dashboard/data/baseline_v0.1.json
dashboard/data/failure_matrix.csv
```

The dashboard embeds comparison and failure data so it works when opened directly with `file://`. The files under `dashboard/data/` are also committed for machine-readable reuse.

## Updating the Baseline

1. Do not edit generated tables by hand.
2. Add or update selected runs in `runs/index.yaml`.
3. Keep one selected run per model, benchmark, and mode.
4. Prefer an accessible `summary.json`; retain a sourced manual fallback for portable regeneration.
5. Register `results_path` only when it points to an authoritative run artifact.
6. Regenerate all reports and the dashboard.
7. Run the complete test suite and inspect the diff for result changes.

Changing selected results should create a new baseline version unless the existing registration is demonstrably incorrect.

## LANTA Ownership Boundary

This repository does not own SSH, Slurm, vLLM deployment, model swapping, OpenWebUI, or LiteLLM. Those concerns belong to the separate `Lanta-LLM-Hosting` repository. See `docs/lanta_single_model_workflow.md` for the handoff between serving and benchmarking.
