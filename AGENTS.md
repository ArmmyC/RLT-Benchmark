# AGENTS.md

## Project purpose

This repository evaluates LLMs for RTL/SystemVerilog/Verilog generation.

The current priority is normal public RTL benchmarks, not private RFID/PPA optimization yet.

Primary goals:
- Run reproducible benchmarks on multiple models.
- Save complete logs and raw outputs.
- Produce honest reports.
- Keep the repository organized.
- Commit meaningful milestones to Git.

## Current known infrastructure

Qwen models are served on LANTA through a vLLM OpenAI-compatible API.

Use environment variables, not hardcoded secrets:

- QWEN_BASE_URL
- QWEN_API_KEY
- QWEN_MODEL
- BENCHMARK_ROOT
- OUTPUT_ROOT

Do not hardcode endpoint URLs, API keys, passwords, or absolute private paths in source files.

## Benchmark priority order

Run benchmarks in this order unless instructed otherwise:

1. VerilogEval v2
2. RTLLM 2.0
3. ProtocolLLM public lint
4. RTL-OPT lint/synthesis/equivalence

Do not start private RFID benchmarks unless explicitly asked.

## Model comparison policy

When comparing models:
- Use the same benchmark version.
- Use the same task set.
- Use the same prompt template.
- Use the same temperature, top_p, max_tokens, timeout, and samples_per_task.
- Use separate output directories per model and benchmark.
- Never compare pass rates from different evaluation modes as if they are equivalent.

Expected models may include:
- qwen36-27b
- qwen36-35b-a3b
- qwen25-coder-32b or another baseline if available

If a model endpoint is unavailable, log the failure and continue with available models.

## Output organization

All benchmark runs must be saved under:

outputs/<benchmark>/<model>/<run_timestamp>/

Each run directory should contain:

- config_snapshot.yaml
- results.jsonl
- summary.json
- summary.csv
- raw_responses/
- extracted_rtl/
- logs/
- error_logs/
- report.md

Do not overwrite previous benchmark outputs.
If rerunning, create a new timestamped directory.

## Logging requirements

Every benchmark sample must record:

- benchmark name
- task id
- model name
- endpoint base URL without secrets
- timestamp
- prompt hash
- generation settings
- raw response path
- extracted RTL path
- compile result
- simulation result
- synthesis result if applicable
- equivalence result if applicable
- failure category
- error log path
- latency
- token usage if available

Failure categories should include:

- api_failure
- empty_response
- code_extraction_failure
- compile_failure
- lint_failure
- simulation_failure
- synthesis_failure
- equiv_failure
- timeout
- passed

## Evaluation rules

Do not count lint-only results as functional correctness.

Do not count synthesis-only results as behavioral correctness.

For RTL-OPT, the trustworthy result is equivalence-passing optimization.

For VerilogEval and RTLLM, the trustworthy result is functional simulation pass.

For ProtocolLLM public, clearly label the result as lint-only unless functional tests are available.

## Report rules

Reports must be honest and must not exaggerate.

Every report should include:

- model
- endpoint
- date
- benchmark version or commit hash
- number of tasks
- number of samples
- generation settings
- syntax/lint pass rate
- functional pass rate if available
- pass@k if samples_per_task > 1
- failure breakdown
- known limitations
- next recommended experiments

Never claim a model is better unless it was tested under the same conditions.

Never claim PPA improvement unless synthesis/equivalence/PPA data supports it.

## Git policy

Before starting work:
- Check git status.
- Do not overwrite user changes.
- If there are unrelated dirty files, ask before modifying them.

Commit after each meaningful milestone:

1. Harness or script improvement.
2. New benchmark integration.
3. New model run result.
4. New report generation.
5. Bug fix with tests.

Use clear commit messages, for example:

- benchmark: add multi-model runner
- benchmark: run qwen36-35b-a3b on VerilogEval
- report: add Qwen3.6 model comparison summary
- fix: preserve raw responses on extraction failure

Do not commit secrets, large temporary files, virtual environments, caches, or model weights.

## Testing policy

Before committing code changes:
- Run unit tests if available.
- Run a small smoke benchmark if the endpoint is available.
- If tests fail, fix them or clearly document the failure.

## Stop conditions

Stop and ask for help if:

- Benchmark dataset path is missing.
- Required EDA tool is missing and cannot be installed safely.
- Endpoint authentication fails.
- A command may delete or overwrite previous outputs.
- A benchmark run would take unusually long and no limit was specified.
- Results contradict previous reports and the reason is unclear.
- Git has unrelated user changes that could be overwritten.

## Style

Prefer small, reviewable changes.

Keep scripts modular.

Use pathlib and type hints in Python where practical.

Keep benchmark logic separate from report-generation logic.

Use deterministic configs and save config snapshots for every run.