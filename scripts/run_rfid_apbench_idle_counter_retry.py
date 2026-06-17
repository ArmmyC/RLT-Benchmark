from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from evaluate_rfid_apbench_candidates import (  # noqa: E402
    ToolAvailability,
    detect_tools,
    evaluate_task_candidate,
    load_reference_metrics,
)
from run_rfid_apbench_model_smoke import (  # noqa: E402
    DEFAULT_PROMPT_PROFILE,
    SYSTEM_PROMPT,
    EndpointConfig,
    load_endpoint_config,
    make_candidate_id,
    _safe_report_note,
)
from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter, RFIDAPBenchTaskInfo  # noqa: E402
from rtlbench.area_activity_scoring import validate_sanitized_record  # noqa: E402
from rtlbench.client import OpenAICompatibleClient  # noqa: E402
from rtlbench.extraction import extract_all_rtl_modules  # noqa: E402


DEFAULT_TASK_ID = "ap_001_idle_counter"
DEFAULT_SAMPLES = 3
REPORT_FIELDS = [
    "task_id",
    "sample_id",
    "model",
    "prompt_profile",
    "generation_status",
    "extraction_status",
    "candidate_file_available",
    "compile_pass",
    "correctness_pass",
    "synth_pass",
    "timing_status",
    "area_metric_available",
    "activity_metric_available",
    "reference_area",
    "generated_area",
    "reference_activity",
    "generated_activity",
    "area_score",
    "activity_score",
    "score",
    "score_status",
    "failure_category",
    "notes",
]


@dataclass
class RetryRow:
    task_id: str
    sample_id: int
    model: str
    prompt_profile: str
    generation_status: str
    extraction_status: str
    candidate_file_available: bool
    compile_pass: bool
    correctness_pass: bool
    synth_pass: bool
    timing_status: str
    area_metric_available: bool
    activity_metric_available: bool
    reference_area: float | None
    generated_area: float | None
    reference_activity: float | None
    generated_activity: float | None
    area_score: float | None
    activity_score: float | None
    score: float | None
    score_status: str
    failure_category: str
    notes: str

    def sanitized_dict(self) -> dict[str, object]:
        data = asdict(self)
        validate_sanitized_record(data)
        return data

    def csv_dict(self) -> dict[str, str]:
        data = self.sanitized_dict()
        return {key: "" if data[key] is None else str(data[key]) for key in REPORT_FIELDS}


@dataclass(frozen=True)
class RetryGeneration:
    sample_id: int
    generation_status: str
    extraction_status: str
    candidate_file_available: bool
    candidate_path: Path | None
    notes: str


def load_task(benchmark_root: Path, task_id: str) -> RFIDAPBenchTaskInfo:
    for task in RFIDAPBenchAdapter(benchmark_root).load_task_infos():
        if task.task_id == task_id:
            return task
    raise ValueError(f"RFID-APBench task not found: {task_id}")


def tools_available(tools: ToolAvailability) -> bool:
    return tools.has_icarus and tools.has_yosys


def missing_tool_labels(tools: ToolAvailability) -> tuple[str, ...]:
    missing: list[str] = []
    if tools.iverilog is None:
        missing.append("iverilog")
    if tools.vvp is None:
        missing.append("vvp")
    if tools.yosys is None:
        missing.append("yosys")
    return tuple(missing)


def make_blocker_rows(
    *,
    task: RFIDAPBenchTaskInfo,
    endpoint: EndpointConfig,
    tools: ToolAvailability,
    samples: int,
    prompt_profile: str,
) -> list[RetryRow]:
    timing_status = "not_required" if not task.timing_required else "unavailable"
    if not endpoint.available:
        failure_category = "endpoint_unavailable"
        missing = ", ".join(endpoint.missing_labels) or "endpoint"
        notes = f"targeted retry blocked because missing {missing}"
    else:
        failure_category = "tool_unavailable"
        missing = ", ".join(missing_tool_labels(tools)) or "EDA tool"
        notes = f"targeted retry blocked because missing {missing}"
    return [
        RetryRow(
            task_id=task.task_id,
            sample_id=sample_id,
            model=endpoint.model,
            prompt_profile=prompt_profile,
            generation_status="blocked",
            extraction_status="not_run",
            candidate_file_available=False,
            compile_pass=False,
            correctness_pass=False,
            synth_pass=False,
            timing_status=timing_status,
            area_metric_available=False,
            activity_metric_available=False,
            reference_area=None,
            generated_area=None,
            reference_activity=None,
            generated_activity=None,
            area_score=None,
            activity_score=None,
            score=None,
            score_status="invalid",
            failure_category=failure_category,
            notes=notes,
        )
        for sample_id in range(1, samples + 1)
    ]


def generate_retry_samples(
    *,
    task: RFIDAPBenchTaskInfo,
    endpoint: EndpointConfig,
    run_root: Path,
    candidate_root: Path,
    samples: int,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> list[RetryGeneration]:
    raw_dir = run_root / "raw_responses"
    extracted_dir = run_root / "extracted_rtl"
    raw_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)
    candidate_root.mkdir(parents=True, exist_ok=True)

    generations: list[RetryGeneration] = []
    client = OpenAICompatibleClient(
        base_url=endpoint.base_url or "",
        api_key=endpoint.credential or "",
        timeout=endpoint.timeout_seconds,
    )
    try:
        for sample_id in range(1, samples + 1):
            sample_name = f"sample_{sample_id:02d}"
            try:
                result = client.generate(
                    model=endpoint.model,
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=task.prompt,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                )
            except Exception as exc:  # noqa: BLE001 - bounded retry reports request failures per sample.
                generations.append(
                    RetryGeneration(
                        sample_id=sample_id,
                        generation_status="request_failed",
                        extraction_status="not_run",
                        candidate_file_available=False,
                        candidate_path=None,
                        notes=_safe_report_note(f"generation request failed: {exc}"),
                    )
                )
                continue

            (raw_dir / f"{task.task_id}_{sample_name}.txt").write_text(result.text, encoding="utf-8")
            rtl = extract_all_rtl_modules(result.text, required_module=task.top_module)
            if rtl is None:
                generations.append(
                    RetryGeneration(
                        sample_id=sample_id,
                        generation_status="completed",
                        extraction_status="failed",
                        candidate_file_available=False,
                        candidate_path=None,
                        notes="no complete required top module extracted",
                    )
                )
                continue

            sample_candidate_dir = candidate_root / sample_name
            sample_candidate_dir.mkdir(parents=True, exist_ok=True)
            extracted_path = extracted_dir / f"{task.task_id}_{sample_name}.sv"
            candidate_path = sample_candidate_dir / f"{task.task_id}.sv"
            extracted_path.write_text(rtl, encoding="utf-8")
            candidate_path.write_text(rtl, encoding="utf-8")
            generations.append(
                RetryGeneration(
                    sample_id=sample_id,
                    generation_status="completed",
                    extraction_status="passed",
                    candidate_file_available=True,
                    candidate_path=candidate_path,
                    notes="generation and extraction completed",
                )
            )
    finally:
        client.close()
    return generations


def evaluate_retry_samples(
    *,
    task: RFIDAPBenchTaskInfo,
    endpoint: EndpointConfig,
    prompt_profile: str,
    generations: list[RetryGeneration],
    work_dir: Path,
    tools: ToolAvailability,
) -> list[RetryRow]:
    rows: list[RetryRow] = []
    reference = load_reference_metrics(task)
    for generation in generations:
        timing_status = "not_required" if not task.timing_required else "unavailable"
        if generation.candidate_path is None:
            rows.append(
                RetryRow(
                    task_id=task.task_id,
                    sample_id=generation.sample_id,
                    model=endpoint.model,
                    prompt_profile=prompt_profile,
                    generation_status=generation.generation_status,
                    extraction_status=generation.extraction_status,
                    candidate_file_available=False,
                    compile_pass=False,
                    correctness_pass=False,
                    synth_pass=False,
                    timing_status=timing_status,
                    area_metric_available=False,
                    activity_metric_available=False,
                    reference_area=reference.area,
                    generated_area=None,
                    reference_activity=reference.activity,
                    generated_activity=None,
                    area_score=None,
                    activity_score=None,
                    score=None,
                    score_status="invalid",
                    failure_category="candidate_missing"
                    if generation.generation_status == "completed"
                    else "api_failure",
                    notes=_safe_report_note(generation.notes),
                )
            )
            continue

        candidate_id = f"{make_candidate_id(endpoint.model)}_sample_{generation.sample_id:02d}"
        evaluation = evaluate_task_candidate(
            task=task,
            candidate_path=generation.candidate_path,
            candidate_id=candidate_id,
            task_work_dir=work_dir / candidate_id,
            tools=tools,
        )
        notes = _safe_report_note(generation.notes)
        if evaluation.notes and evaluation.notes != "candidate validated":
            notes = _safe_report_note(f"{notes}; {evaluation.notes}")
        rows.append(
            RetryRow(
                task_id=task.task_id,
                sample_id=generation.sample_id,
                model=endpoint.model,
                prompt_profile=prompt_profile,
                generation_status=generation.generation_status,
                extraction_status=generation.extraction_status,
                candidate_file_available=evaluation.candidate_file_available,
                compile_pass=evaluation.compile_pass,
                correctness_pass=evaluation.correctness_pass,
                synth_pass=evaluation.synth_pass,
                timing_status=evaluation.timing_status,
                area_metric_available=(
                    evaluation.reference_area is not None and evaluation.generated_area is not None
                ),
                activity_metric_available=(
                    evaluation.reference_activity is not None and evaluation.generated_activity is not None
                ),
                reference_area=evaluation.reference_area,
                generated_area=evaluation.generated_area,
                reference_activity=evaluation.reference_activity,
                generated_activity=evaluation.generated_activity,
                area_score=evaluation.area_score,
                activity_score=evaluation.activity_score,
                score=evaluation.score,
                score_status=evaluation.score_status,
                failure_category=evaluation.failure_category,
                notes=notes,
            )
        )
    return rows


def classify_retry_outcome(rows: list[RetryRow]) -> str:
    if not rows:
        return "operational_blocker"
    if all(row.failure_category in {"endpoint_unavailable", "tool_unavailable", "api_failure"} for row in rows):
        return "operational_blocker"
    if any(row.extraction_status == "passed" for row in rows):
        return "one_off_extraction_issue"
    return "repeatable_extraction_fragility"


def recommended_next_action(outcome: str, rows: list[RetryRow]) -> str:
    if outcome == "one_off_extraction_issue":
        if any(row.score_status == "valid" for row in rows):
            return "Fold the valid retry evidence into the smoke notes and keep the benchmark/prompt/extractor unchanged."
        return "Treat the original extraction failure as non-repeatable, but open a separate scoped correctness investigation before changing benchmark conclusions."
    if outcome == "repeatable_extraction_fragility":
        return "Open a separate scoped prompt or extractor investigation for ap_001_idle_counter before broader reruns."
    return "Restore endpoint and EDA tool availability, then rerun this exact targeted retry without changing benchmark conclusions."


def write_jsonl_report(rows: list[RetryRow], output_jsonl: Path) -> None:
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.sanitized_dict(), sort_keys=True) + "\n")


def write_csv_report(rows: list[RetryRow], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.csv_dict())


def write_markdown_report(
    rows: list[RetryRow],
    output_md: Path,
    *,
    endpoint: EndpointConfig,
    tools: ToolAvailability,
    task_id: str,
    run_id: str,
) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    outcome = classify_retry_outcome(rows)
    valid_scores = [row.score for row in rows if row.score_status == "valid" and row.score is not None]
    best_valid = max(valid_scores) if valid_scores else None
    sample_count = len(rows)
    lines = [
        "# v0.5 RFID-APBench Idle Counter Targeted Retry",
        "",
        "## Scope",
        "",
        "This is a bounded targeted retry for the public/synthetic RFID-APBench idle-counter task that failed extraction in the first real model smoke.",
        "",
        f"- Task id: `{task_id}`",
        f"- Sample count: {sample_count}",
        f"- Model: `{endpoint.model}`",
        f"- Prompt profile: `{DEFAULT_PROMPT_PROFILE}`",
        "- Temperature: `0.0`",
        "- Top-p: `1.0`",
        "- Max tokens: `4096`",
        f"- Run id: `{run_id}`",
        "",
        "## Non-Goals",
        "",
        "- This is not prompt tuning, fine-tuning, dataset creation, adapter training, or checkpoint work.",
        "- This is not a private RFID evaluation.",
        "- This does not compare models, run broad samples, modify task text, modify prompts, or claim measured power/final silicon PPA.",
        "- This does not commit raw prompts, raw model responses, generated RTL, VCDs, simulator logs, synthesis logs, compiled artifacts, secrets, model weights, training datasets, or LoRA/QLoRA/DoRA adapters.",
        "",
        "## Model and Endpoint Availability",
        "",
        f"- Endpoint status: `{endpoint.status}`",
        f"- Endpoint: `{endpoint.sanitized_endpoint}`",
        f"- Missing endpoint configuration: `{', '.join(endpoint.missing_labels) if endpoint.missing_labels else 'none'}`",
        f"- Icarus Verilog compile: `{_tool_status(tools.iverilog)}`",
        f"- Icarus runtime vvp: `{_tool_status(tools.vvp)}`",
        f"- Yosys synthesis: `{_tool_status(tools.yosys)}`",
        "",
        "## Retry Gate Counts",
        "",
        f"- Generation completed: {sum(1 for row in rows if row.generation_status == 'completed')}",
        f"- Extraction passed: {sum(1 for row in rows if row.extraction_status == 'passed')}",
        f"- Candidate file available: {sum(1 for row in rows if row.candidate_file_available)}",
        f"- Compile pass: {sum(1 for row in rows if row.compile_pass)}",
        f"- Correctness pass: {sum(1 for row in rows if row.correctness_pass)}",
        f"- Synthesis pass: {sum(1 for row in rows if row.synth_pass)}",
        f"- Area metric available: {sum(1 for row in rows if row.area_metric_available)}",
        f"- Activity metric available: {sum(1 for row in rows if row.activity_metric_available)}",
        f"- Valid score count: {len(valid_scores)}",
    ]
    if best_valid is not None:
        lines.append(f"- Best valid retry score: {best_valid:.6f}")
        lines.append("- Original smoke score for this task: invalid/zero-filled")
    elif any(row.extraction_status == "passed" for row in rows):
        lines.append("- Best valid retry score: none")
        lines.append("- Original smoke score for this task: invalid/zero-filled")
    lines.extend(
        [
            "",
            "## Per-Sample Sanitized Results",
            "",
            "| sample_id | generation | extraction | compile | correctness | synthesis | area_metric | activity_metric | score_status | score | failure_category | notes |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in rows:
        data = row.csv_dict()
        lines.append(
            "| "
            + " | ".join(
                [
                    data["sample_id"],
                    data["generation_status"],
                    data["extraction_status"],
                    data["compile_pass"],
                    data["correctness_pass"],
                    data["synth_pass"],
                    data["area_metric_available"],
                    data["activity_metric_available"],
                    data["score_status"],
                    data["score"],
                    data["failure_category"],
                    data["notes"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            f"- Retry outcome: `{outcome}`",
            f"- Recommended next action: {recommended_next_action(outcome, rows)}",
            "",
            "## Activity Proxy Caveat",
            "",
            "Activity is a VCD toggle-count proxy from the declared public workload. It is not measured silicon power, signoff power, or final silicon PPA.",
            "",
            "## Public Synthetic Caveat",
            "",
            "This is public synthetic RFID-APBench smoke analysis. It is not private evaluation and not fine-tuning.",
            "",
            "## Artifact Policy",
            "",
            "Raw model responses, extracted RTL, generated candidates, VCDs, logs, compiled artifacts, and synthesis scratch are kept only under ignored output/work directories. The committed artifacts are sanitized Markdown, CSV, and JSONL summaries.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFID-APBench idle-counter targeted retry.")
    parser.add_argument("--benchmark-root", type=Path, default=Path("benchmarks/rfid_apbench"))
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--work-dir", type=Path, default=Path(".tmp/rfid_apbench_idle_counter_retry"))
    parser.add_argument("--output-root", type=Path, default=Path("outputs/rfid_apbench/idle_counter_retry"))
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.5_rfid_apbench_idle_counter_retry.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.5_rfid_apbench_idle_counter_retry.csv"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("reports/v0.5_rfid_apbench_idle_counter_retry.jsonl"))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--prompt-profile", default=DEFAULT_PROMPT_PROFILE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.samples != DEFAULT_SAMPLES:
        raise ValueError("v0.5 idle-counter targeted retry is bounded to exactly 3 samples")
    if args.task_id != DEFAULT_TASK_ID:
        raise ValueError(f"v0.5 idle-counter targeted retry is bounded to {DEFAULT_TASK_ID}")

    benchmark_root = args.benchmark_root.resolve()
    task = load_task(benchmark_root, args.task_id)
    endpoint = load_endpoint_config()
    tools = detect_tools()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if not endpoint.available or not tools_available(tools):
        rows = make_blocker_rows(
            task=task,
            endpoint=endpoint,
            tools=tools,
            samples=args.samples,
            prompt_profile=args.prompt_profile,
        )
    else:
        candidate_id = make_candidate_id(endpoint.model)
        run_root = (args.output_root / run_id).resolve()
        candidate_root = (args.work_dir / "candidates" / candidate_id).resolve()
        generations = generate_retry_samples(
            task=task,
            endpoint=endpoint,
            run_root=run_root,
            candidate_root=candidate_root,
            samples=args.samples,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
        )
        rows = evaluate_retry_samples(
            task=task,
            endpoint=endpoint,
            prompt_profile=args.prompt_profile,
            generations=generations,
            work_dir=(args.work_dir / "evaluation").resolve(),
            tools=tools,
        )

    output_md = args.output_md.resolve()
    output_csv = args.output_csv.resolve()
    output_jsonl = args.output_jsonl.resolve()
    write_markdown_report(rows, output_md, endpoint=endpoint, tools=tools, task_id=args.task_id, run_id=run_id)
    write_csv_report(rows, output_csv)
    write_jsonl_report(rows, output_jsonl)
    print(f"Wrote {output_md}")
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_jsonl}")
    return 0


def _tool_status(path: str | None) -> str:
    return "available" if path else "unavailable"


if __name__ == "__main__":
    raise SystemExit(main())
