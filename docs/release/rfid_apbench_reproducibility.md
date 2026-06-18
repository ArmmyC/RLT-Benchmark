# RFID-APBench Reproducibility Guide

This guide explains how to reproduce the v0.7 RFID-APBench public/synthetic post-fix baseline. It is written for release owners and reviewers who need to rerun or audit the 10-task, 3-sample baseline without exposing secrets or committing raw artifacts.

Use this guide together with `docs/release/rfid_apbench_release_checklist.md` before tagging a release.

## Scope

RFID-APBench is a public/synthetic RFID/NFC-style RTL benchmark for area plus activity evaluation. The current manifest contains 10 tasks and uses `area_activity` scoring with `vcd_toggle_count_proxy` activity.

Current task inventory:

| task id | description |
| --- | --- |
| `ap_001_idle_counter` | idle-aware counter |
| `ap_002_command_decoder` | small command decoder |
| `ap_003_register_bank_unnecessary_writes` | register bank with stable disabled writes |
| `ap_004_crc_serial_parallel_tradeoff` | small CRC update block |
| `ap_005_fsm_controller_idle_activity` | low-duty-cycle controller FSM |
| `ap_006_wakeup_edge_filter` | enabled rising-edge wakeup pulse filter |
| `ap_007_command_frame_checker` | command-frame validity checker |
| `ap_008_byte_lane_write_gate` | byte-lane gated register writes |
| `ap_009_serial_parity_accumulator` | serial parity and bit-count accumulator |
| `ap_010_retry_timeout_fsm` | retry and timeout controller |

The v0.7 post-fix baseline uses the current public manifest, the approved `ap_001_idle_counter` prompt clarity update, and the fixed runner path that forwards the Qwen thinking-disabled model preset body.

## Prerequisite Checklist

- [ ] Repository checkout is at the intended commit or release tag.
- [ ] Python environment can run the repository tests.
- [ ] Icarus Verilog compile tool `iverilog` is installed and on `PATH`.
- [ ] Icarus runtime `vvp` is installed and on `PATH`.
- [ ] Yosys is installed and on `PATH`.
- [ ] OpenAI-compatible Qwen endpoint is reachable from the machine running the benchmark.
- [ ] `benchmarks/rfid_apbench/manifest.yaml` exists and lists 10 public/synthetic tasks.
- [ ] `.env` or shell environment contains only placeholder or local secrets that will not be committed.

Useful local checks:

```powershell
python -m pytest
where.exe iverilog
where.exe vvp
where.exe yosys
```

## Endpoint Environment

The runner reads endpoint configuration from environment variables. Use placeholders in documentation and commits. Never commit real credentials.

Required:

- `QWEN_BASE_URL`: OpenAI-compatible endpoint base URL.
- `QWEN_API_KEY`: API key or local placeholder accepted by the endpoint.

Optional:

- `QWEN_MODEL`: served model name. Defaults to the configured runner default when unset.
- `QWEN_TIMEOUT`: request timeout in seconds.

PowerShell example with placeholder values:

```powershell
$env:QWEN_BASE_URL = "http://<host>:<port>/v1"
$env:QWEN_API_KEY = "<api-key-or-local-placeholder>"
$env:QWEN_MODEL = "qwen36-27b"
$env:QWEN_TIMEOUT = "120"
```

`.env` example with placeholder values:

```dotenv
QWEN_BASE_URL=http://<host>:<port>/v1
QWEN_API_KEY=<api-key-or-local-placeholder>
QWEN_MODEL=qwen36-27b
QWEN_TIMEOUT=120
```

`.env` is ignored by the repository and should stay local. Do not copy real endpoint URLs with embedded credentials, real API keys, private paths, or private infrastructure details into committed reports.

## Deterministic v0.7 Settings

Use these settings to reproduce the v0.7 post-fix baseline:

| setting | value |
| --- | --- |
| model | `qwen36-27b` |
| prompt profile | `neutral_baseline` |
| temperature | `0.0` |
| top-p | `1.0` |
| max tokens | `4096` |
| samples per task | `3` |
| benchmark root | `benchmarks/rfid_apbench` |
| output root | ignored path under `outputs/` |
| work dir | ignored path under `.tmp/` |

For `qwen36-27b`, `configs/models.yaml` includes the non-secret request body extension:

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

`scripts/run_rfid_apbench_3sample_baseline.py` resolves the selected model preset and forwards this `extra_body` into the OpenAI-compatible request path. Keep this behavior enabled for v0.7 reproducibility.

## Full Baseline Command

This command shape reproduces a full 10-task x 3-sample RFID-APBench baseline. It writes sanitized reports to `reports/` and raw/scratch artifacts to ignored directories.

```powershell
python scripts\run_rfid_apbench_3sample_baseline.py `
  --benchmark-root benchmarks\rfid_apbench `
  --samples-per-task 3 `
  --prompt-profile neutral_baseline `
  --temperature 0.0 `
  --top-p 1.0 `
  --max-tokens 4096 `
  --output-md reports\v0.7_rfid_apbench_post_fix_expanded_10task_baseline.md `
  --output-csv reports\v0.7_rfid_apbench_post_fix_expanded_10task_baseline.csv `
  --output-jsonl reports\v0.7_rfid_apbench_post_fix_expanded_10task_baseline.jsonl `
  --output-root outputs\rfid_apbench\post_fix_expanded_10task_baseline `
  --work-dir .tmp\rfid_apbench_post_fix_expanded_10task_baseline
```

Do not overwrite a committed release baseline unless the release owner explicitly intends to regenerate that artifact. For exploratory reruns, use new report names and a new ignored output/work directory.

## Targeted Validation Commands

Targeted validations are allowed only when a bounded spec calls for them. Keep task filters explicit and preserve deterministic settings.

Three-sample targeted validation example:

```powershell
python scripts\run_rfid_apbench_3sample_baseline.py `
  --benchmark-root benchmarks\rfid_apbench `
  --task-id ap_001_idle_counter `
  --samples-per-task 3 `
  --prompt-profile neutral_baseline `
  --temperature 0.0 `
  --top-p 1.0 `
  --max-tokens 4096 `
  --output-md reports\<targeted_validation>.md `
  --output-csv reports\<targeted_validation>.csv `
  --output-jsonl reports\<targeted_validation>.jsonl `
  --output-root outputs\rfid_apbench\<targeted_validation> `
  --work-dir .tmp\<targeted_validation>
```

One-sample targeted validation is permitted only with the explicit validation flag:

```powershell
python scripts\run_rfid_apbench_3sample_baseline.py `
  --benchmark-root benchmarks\rfid_apbench `
  --task-id ap_010_retry_timeout_fsm `
  --samples-per-task 1 `
  --allow-single-sample-validation `
  --prompt-profile neutral_baseline `
  --temperature 0.0 `
  --top-p 1.0 `
  --max-tokens 4096 `
  --output-md reports\<one_sample_validation>.md `
  --output-csv reports\<one_sample_validation>.csv `
  --output-jsonl reports\<one_sample_validation>.jsonl `
  --output-root outputs\rfid_apbench\<one_sample_validation> `
  --work-dir .tmp\<one_sample_validation>
```

The runner rejects duplicate task IDs, unknown task IDs, and unsupported sample counts.

## Candidate Evaluator Command

Use the candidate evaluator only for explicit candidate-fixture checks or follow-up specs. It is not the normal model-generation baseline command.

```powershell
python scripts\evaluate_rfid_apbench_candidates.py `
  --benchmark-root benchmarks\rfid_apbench `
  --candidate-root benchmarks\rfid_apbench\candidates\reference_copy `
  --work-dir .tmp\rfid_apbench_candidate_smoke `
  --output-md reports\rfid_apbench_candidate_smoke.md `
  --output-csv reports\rfid_apbench_candidate_smoke.csv `
  --output-jsonl reports\rfid_apbench_candidate_smoke.jsonl
```

Do not commit generated candidate RTL, simulator scratch, VCDs, or synthesis logs from evaluator work directories.

## Sanitized Outputs

Committed release evidence should be sanitized reports under `reports/`:

- Markdown: human-readable report and conclusions.
- CSV: tabular row summary when the run produces rows.
- JSONL: sanitized row records when the run produces rows.

Sanitized reports may include:

- model name and prompt profile
- endpoint base URL without secrets
- deterministic settings
- request outcome distribution
- content/token metadata
- extraction, compile, simulation, synthesis, area, activity, and score gates
- failure categories
- score summaries
- benchmark asset and fine-tuning decisions
- public/synthetic and activity-proxy caveats

Sanitized reports must not include raw response bodies, generated RTL, private paths, secrets, VCD snippets, simulator logs, synthesis logs, compiled artifacts, model weights, datasets, adapters, or fine-tuning scripts.

## Ignored Raw Artifacts

The runner and evaluator write raw or scratch artifacts only under ignored locations such as:

- `outputs/`
- `.tmp/`
- `raw_responses/` inside ignored output roots
- `extracted_rtl/` inside ignored output roots
- evaluator work directories
- generated candidate directories under ignored work roots
- VCDs such as `activity.vcd`
- simulator binaries
- synthesis scratch/log material
- Python caches and pytest cache

The repository `.gitignore` excludes `.env`, `.tmp/`, `.pytest_cache/`, `__pycache__/`, `outputs/`, and external benchmark checkouts except the public `benchmarks/rfid_apbench/` tree.

## Verification Before Committing Results

Run this checklist before committing any reproduced results:

- [ ] `python -m pytest` passes.
- [ ] Reports exist under `reports/` with expected Markdown/CSV/JSONL names.
- [ ] Reports include source evidence, settings, endpoint/tool status without secrets, gate counts, score summaries, limitations, and caveats.
- [ ] `git diff -- benchmarks/rfid_apbench configs README.md` is empty unless a separate approved spec changed those files.
- [ ] `git status --short --ignored` shows only intended reports/docs plus expected ignored scratch.
- [ ] No real API key, token, password, private endpoint credential, or private absolute path appears in staged files.
- [ ] No raw model response, generated RTL, VCD, simulator log, synthesis log, compiled artifact, model weight, dataset, adapter, or fine-tuning script is staged.
- [ ] No root-level `activity.vcd` is present.
- [ ] The release checklist in `docs/release/rfid_apbench_release_checklist.md` is satisfied before tagging.

Useful local checks:

```powershell
python -m pytest
git status --short --ignored
git diff -- benchmarks\rfid_apbench configs README.md
Test-Path -LiteralPath activity.vcd
```

## Troubleshooting

### Endpoint Unavailable

Symptoms:

- report rows are blocked with endpoint unavailable
- `/models` preflight fails when required
- request attempts cannot reach `QWEN_BASE_URL`

Checks:

- Confirm `QWEN_BASE_URL` points to an OpenAI-compatible `/v1` endpoint.
- Confirm `QWEN_API_KEY` is set to the value expected by the endpoint.
- Confirm `QWEN_MODEL` matches a served model if overriding the default.
- Confirm firewall, tunnel, or local serving process state outside the repository.

Do not hardcode endpoint credentials in source files or reports.

### Tool Unavailable

Symptoms:

- report rows are blocked with `tool_unavailable`
- Icarus or Yosys health is unavailable

Checks:

```powershell
where.exe iverilog
where.exe vvp
where.exe yosys
python -m pytest
```

Install or expose tools on `PATH` before rerunning. Do not count lint-only or synthesis-only success as functional correctness.

### Request Failed

Symptoms:

- request outcome is `request_failed`
- HTTP status is non-`2xx`
- response parse status is failed or unavailable

Checks:

- Confirm endpoint is reachable and accepts the configured API key.
- Confirm model name is served.
- Confirm timeout is sufficient with `QWEN_TIMEOUT`.
- Preserve sanitized request metadata in the report; do not commit raw response bodies.

### Extraction Failure

Symptoms:

- generation completed but extraction failed
- candidate file is unavailable

Checks:

- Confirm the response contained a complete module for the required top module.
- Review only ignored raw output locally if needed.
- Report the sanitized failure category without committing raw model text or generated RTL.

### Compile Failure

Symptoms:

- extraction passed but Icarus compile failed

Checks:

- Treat this as a candidate validity failure unless tool health is also failing.
- Keep simulator logs in ignored work directories.
- Do not edit reference RTL or testbench behavior without a separate asset-defect spec.

### Simulation Failure

Symptoms:

- compile passed but functional simulation failed

Checks:

- Treat functional simulation as the correctness gate for RFID-APBench tasks.
- Classify the failure from sanitized evidence.
- Do not count synthesis success as behavioral correctness.

### Synthesis Failure

Symptoms:

- functional simulation may pass, but Yosys synthesis fails

Checks:

- Treat the row as invalid for area/activity scoring.
- Keep synthesis logs and scratch under ignored work directories.
- Confirm Yosys health with unit tests or tool checks before blaming candidate behavior.

### Empty Or Null-Content Recurrence

Symptoms:

- visible content is absent
- `finish_reason=length`
- completion tokens hit the 4096 limit
- response-boundary signature resembles the pre-fix v0.6 issue

Checks:

- Confirm `configs/models.yaml` still contains `chat_template_kwargs.enable_thinking=false` for `qwen36-27b`.
- Confirm `scripts/run_rfid_apbench_3sample_baseline.py` still forwards model preset `extra_body`.
- Confirm the run used `neutral_baseline` and max tokens `4096`.
- Record sanitized request/content/token metadata.
- Do not raise the global max-token default unless a separate bounded spec proves it is needed.

## Known v0.7 Limitation

The remaining v0.7 invalid rows are localized to `ap_006_wakeup_edge_filter` and classified as candidate implementation failures. The current evidence does not support endpoint, token-limit, extractor, tool, evaluator, scoring, prompt-profile, or benchmark-asset defects for this limitation.

Carry this forward as a known result limitation, not a release blocker and not a reason to edit benchmark assets.

## Caveats And Non-Goals

- Activity is a VCD toggle-count proxy from the declared public workload.
- Activity is not measured silicon power, signoff power, final silicon PPA, or production QoR.
- RFID-APBench is public/synthetic and does not contain private RTL.
- These runs are not private evaluation.
- These reports are evaluation artifacts, not training datasets.
- This evidence does not justify fine-tuning, LoRA/QLoRA/DoRA adapters, model-weight changes, or training-data creation.
- Reproducing the v0.7 baseline does not compare models.
- Reproducing the v0.7 baseline does not require changing prompt profiles, raising max tokens, editing tasks, editing prompts, editing references, editing testbenches, or changing scoring/evaluator policy.
