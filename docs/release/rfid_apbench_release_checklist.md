# RFID-APBench Release Checklist

Use this checklist before tagging a public/synthetic RFID-APBench milestone. Copy it into the release issue, PR, or release notes draft and check each item with current repository evidence.

This checklist does not create or push tags. Run tag commands only after the release owner has reviewed the checked evidence.

## Release Evidence

- [ ] Release closeout report exists and states release readiness.
- [ ] Baseline report exists for the release evidence set.
- [ ] Baseline CSV and JSONL row artifacts exist when the baseline produced tabular rows.
- [ ] Failure-analysis or limitation report exists for any concentrated invalid pattern.
- [ ] Reports include source evidence and report-to-report lineage.
- [ ] Reports are sanitized and do not include raw response bodies, generated RTL, logs, VCD snippets, private paths, or secrets.

For v0.7, expected evidence:

- [ ] `reports/v0.7_rfid_apbench_release_closeout.md`
- [ ] `reports/v0.7_rfid_apbench_post_fix_expanded_10task_baseline.md`
- [ ] `reports/v0.7_rfid_apbench_post_fix_expanded_10task_baseline.csv`
- [ ] `reports/v0.7_rfid_apbench_post_fix_expanded_10task_baseline.jsonl`
- [ ] `reports/v0.7_rfid_apbench_post_fix_failure_analysis.md`
- [ ] `reports/v0.7_rfid_apbench_ap001_post_clarity_targeted_validation.md`
- [ ] `reports/v0.7_rfid_apbench_ap001_prompt_clarity.md`

## Benchmark Inventory

- [ ] `benchmarks/rfid_apbench/manifest.yaml` exists.
- [ ] Manifest benchmark name is `rfid_apbench`.
- [ ] Manifest states `public_synthetic: true`.
- [ ] Manifest scoring mode is `area_activity`.
- [ ] Manifest activity definition is `vcd_toggle_count_proxy`.
- [ ] Manifest task count matches the release report.
- [ ] Release notes list the task IDs or point to the manifest.
- [ ] `benchmarks/rfid_apbench/README.md` states public/synthetic scope and artifact policy.

For v0.7, expected task count is 10:

- [ ] `ap_001_idle_counter`
- [ ] `ap_002_command_decoder`
- [ ] `ap_003_register_bank_unnecessary_writes`
- [ ] `ap_004_crc_serial_parallel_tradeoff`
- [ ] `ap_005_fsm_controller_idle_activity`
- [ ] `ap_006_wakeup_edge_filter`
- [ ] `ap_007_command_frame_checker`
- [ ] `ap_008_byte_lane_write_gate`
- [ ] `ap_009_serial_parity_accumulator`
- [ ] `ap_010_retry_timeout_fsm`

## Model, Config, And Run Settings

- [ ] Release report records model name.
- [ ] Release report records prompt profile.
- [ ] Release report records temperature, top-p, max tokens, and samples per task.
- [ ] Release report records endpoint status without credentials.
- [ ] `configs/models.yaml` contains the selected model preset.
- [ ] Required model preset `extra_body` is documented when applicable.
- [ ] `configs/prompt_profiles.yaml` contains the selected prompt profile.
- [ ] The release did not change prompt profiles.
- [ ] The release did not raise the global max-token default.
- [ ] The release did not use `completion_reliability` unless a separate approved spec explicitly requires it.

For v0.7, expected settings:

- [ ] Model: `qwen36-27b`
- [ ] Prompt profile: `neutral_baseline`
- [ ] Temperature: `0.0`
- [ ] Top-p: `1.0`
- [ ] Max tokens: `4096`
- [ ] Samples per task: `3`
- [ ] `chat_template_kwargs.enable_thinking=false` forwarded through model preset `extra_body`

## Endpoint And Tool Status

- [ ] Endpoint base URL is reported without API keys or secrets.
- [ ] Missing endpoint configuration is reported if applicable.
- [ ] Icarus compile status is reported.
- [ ] Icarus runtime `vvp` status is reported.
- [ ] Yosys synthesis status is reported.
- [ ] Any endpoint or tool blocker is recorded as a blocker row or explicit report limitation.
- [ ] No release claim relies on unavailable or unhealthy tools.

## Validation Guardrails

- [ ] Baseline runs use exactly 3 samples per task.
- [ ] Any targeted validation exception is explicitly bounded and documented.
- [ ] Single-sample validation is used only with an explicit validation exception.
- [ ] Task filters are explicit and limited to manifest task IDs.
- [ ] Unknown or duplicate task IDs are rejected by the runner.
- [ ] Model preset `extra_body` forwarding is preserved.
- [ ] Unit tests covering sample-count, task-filter, sanitized-row, and `extra_body` behavior pass.
- [ ] No live model endpoint is required by unit tests.

Useful local check:

```powershell
python -m pytest
```

## Report Hygiene

- [ ] Report filenames are stable and versioned.
- [ ] Reports include scope and non-goals.
- [ ] Reports include source evidence.
- [ ] Reports include endpoint and tool status without secrets.
- [ ] Reports include request outcome distribution when model requests were made.
- [ ] Reports include content/token metadata when available.
- [ ] Reports include extraction, compile, functional simulation, synthesis, area, activity, and score gates.
- [ ] Reports separate functional correctness from compile-only or synthesis-only success.
- [ ] Reports include valid-score and all-sample zero-filled score summaries when scores exist.
- [ ] Reports include failure categories and known limitations.
- [ ] Reports include benchmark asset and fine-tuning readiness decisions.
- [ ] Reports include activity-proxy and public synthetic/no-private/not-fine-tuning caveats.

## Artifact And Privacy Policy

- [ ] `.gitignore` excludes `.env`, `.tmp/`, `.pytest_cache/`, `__pycache__/`, `outputs/`, and external benchmark checkouts.
- [ ] No private RTL or private task text is staged.
- [ ] No raw prompts beyond public benchmark prompt text are staged.
- [ ] No raw model responses or response bodies are staged.
- [ ] No generated model RTL is staged.
- [ ] No raw benchmark output directories are staged.
- [ ] No VCD files are staged.
- [ ] No simulator logs, synthesis logs, compiled artifacts, or tool scratch files are staged.
- [ ] No endpoint credentials, secrets, or private absolute paths are staged.
- [ ] No model weights, datasets, adapters, or fine-tuning scripts are staged.

Useful local checks:

```powershell
git status --short --ignored
git diff -- benchmarks/rfid_apbench configs README.md
Test-Path -LiteralPath activity.vcd
```

## Git And Tag Readiness

- [ ] Working tree contains only intended documentation/report changes and expected ignored scratch.
- [ ] Benchmark assets are unchanged except explicitly approved public benchmark changes.
- [ ] Config changes are absent or explicitly approved and documented.
- [ ] `python -m pytest` passes.
- [ ] Release report states the exact tag name.
- [ ] Release owner has reviewed the final diff.
- [ ] Tag commands are run manually only after all checklist items pass.

Example v0.7 tag commands only:

```bash
git tag v0.7-rfid-apbench-post-fix-baseline
git push origin v0.7-rfid-apbench-post-fix-baseline
```

Do not run these commands from the checklist itself.

## Claim Safety

- [ ] Release notes do not claim measured power.
- [ ] Release notes do not claim signoff power.
- [ ] Release notes do not claim final silicon PPA or production QoR.
- [ ] Release notes do not claim private evaluation.
- [ ] Release notes do not claim model superiority unless a matched model comparison was actually run.
- [ ] Release notes do not claim fine-tuning readiness.
- [ ] Compile and synthesis results are not described as functional correctness.
- [ ] Area/activity scores are described as benchmark metrics only.

## Known Limitations

- [ ] Known limitations are listed in release notes.
- [ ] Any known limitation is classified as benchmark asset, runner, endpoint, tool, evaluator, scoring, prompt, or candidate behavior only when evidence supports that classification.
- [ ] Known limitations do not block release unless the closeout report says they are release blockers.
- [ ] Any future investigation is kept as a separate bounded follow-up.

For v0.7:

- [ ] `ap_006_wakeup_edge_filter` is carried as a candidate implementation limitation.
- [ ] The `ap_006` limitation is not treated as an endpoint, token-limit, extractor, tool, evaluator, scoring, prompt-profile, or benchmark-asset defect.
- [ ] `ap_001_idle_counter` prompt clarity is recorded as approved and validated.
- [ ] Response-boundary reliability is recorded as closed for v0.7 evidence.

## Post-Release Next-Step Planning

- [ ] Exactly one next bounded direction is recommended.
- [ ] The next direction does not require private benchmarks, model comparison, prompt-profile changes, global max-token changes, training-data creation, or fine-tuning unless a separate approved spec requires it.
- [ ] The next direction is recorded in the release report or follow-up planning report.
- [ ] Open follow-ups distinguish immediate work from future/non-goal work.

Recommended after this checklist step:

- [ ] `v0.8_reproducibility_docs_spec`

## Caveats To Preserve

- [ ] Activity is described as a VCD toggle-count proxy from the declared public workload.
- [ ] Activity is not described as measured silicon power, signoff power, final silicon PPA, or production QoR.
- [ ] RFID-APBench is described as public/synthetic.
- [ ] The release contains no private data or private RTL.
- [ ] The release is not private evaluation.
- [ ] The release does not create training data and is not fine-tuning evidence.
