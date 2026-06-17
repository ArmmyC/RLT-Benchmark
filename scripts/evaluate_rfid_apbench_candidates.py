from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter, RFIDAPBenchTaskInfo  # noqa: E402
from rtlbench.area_activity_scoring import (  # noqa: E402
    GateOutcomes,
    MetricInputs,
    SampleIdentity,
    aggregate_score_value,
    score_sample,
    validate_sanitized_record,
)
from rtlbench.vcd_activity import VCDActivityError, count_vcd_file  # noqa: E402
from rtlbench.tool_health import (  # noqa: E402
    ToolAvailability,
    ToolCommandResult,
    detect_tools,
    run_tool_command,
)


REPORT_FIELDS = [
    "task_id",
    "candidate_id",
    "final_pass",
    "candidate_file_available",
    "compile_pass",
    "correctness_pass",
    "synth_pass",
    "timing_status",
    "reference_area",
    "generated_area",
    "area_unit",
    "reference_activity",
    "generated_activity",
    "activity_metric",
    "area_score",
    "activity_score",
    "score",
    "score_status",
    "failure_category",
    "toolchain_id",
    "workload_id",
    "notes",
]


@dataclass(frozen=True)
class ReferenceMetrics:
    task_id: str
    area: float
    area_unit: str
    activity: float
    activity_metric: str
    toolchain_id: str
    timing_required: bool
    timing_status: str


@dataclass
class CandidateEvaluationRow:
    task_id: str
    candidate_id: str
    final_pass: bool
    candidate_file_available: bool
    compile_pass: bool
    correctness_pass: bool
    synth_pass: bool
    timing_status: str
    reference_area: float | None
    generated_area: float | None
    area_unit: str | None
    reference_activity: float | None
    generated_activity: float | None
    activity_metric: str | None
    area_score: float | None
    activity_score: float | None
    score: float | None
    score_status: str
    failure_category: str
    toolchain_id: str
    workload_id: str
    notes: str

    def sanitized_dict(self) -> dict[str, object]:
        data = asdict(self)
        validate_sanitized_record(data)
        return data

    def csv_dict(self) -> dict[str, str]:
        data = self.sanitized_dict()
        return {key: "" if data[key] is None else str(data[key]) for key in REPORT_FIELDS}


def candidate_path_for_task(candidate_root: Path, task_id: str) -> Path:
    return candidate_root / f"{task_id}.sv"


def load_reference_metrics(task: RFIDAPBenchTaskInfo) -> ReferenceMetrics:
    metrics_path = task.task_path / "expected" / "reference_metrics.yaml"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"Missing reference metrics for {task.task_id}: {metrics_path}")
    data = yaml.safe_load(metrics_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{metrics_path} must contain a mapping")
    area = data.get("area")
    activity = data.get("activity")
    timing = data.get("timing", {})
    if not isinstance(area, dict) or not isinstance(activity, dict) or not isinstance(timing, dict):
        raise ValueError(f"{metrics_path} missing area/activity/timing mappings")
    return ReferenceMetrics(
        task_id=str(data["task_id"]),
        area=float(area["value"]),
        area_unit=str(area["unit"]),
        activity=float(activity["value"]),
        activity_metric=str(activity["metric"]),
        toolchain_id=str(data.get("toolchain_id", "iverilog-vcd-yosys-generic")),
        timing_required=bool(timing.get("required", False)),
        timing_status=str(timing.get("status", "not_required")),
    )


def evaluate_candidates(
    benchmark_root: Path,
    candidate_root: Path,
    work_dir: Path,
    tools: ToolAvailability | None = None,
) -> list[CandidateEvaluationRow]:
    tools = tools or detect_tools()
    tasks = list(RFIDAPBenchAdapter(benchmark_root).load_task_infos())
    candidate_id = candidate_root.name
    rows: list[CandidateEvaluationRow] = []
    for task in tasks:
        rows.append(
            evaluate_task_candidate(
                task=task,
                candidate_path=candidate_path_for_task(candidate_root, task.task_id),
                candidate_id=candidate_id,
                task_work_dir=work_dir / candidate_id / task.task_id,
                tools=tools,
            )
        )
    return rows


def evaluate_task_candidate(
    task: RFIDAPBenchTaskInfo,
    candidate_path: Path,
    candidate_id: str,
    task_work_dir: Path,
    tools: ToolAvailability,
) -> CandidateEvaluationRow:
    task_work_dir.mkdir(parents=True, exist_ok=True)
    workload_id = str(task.activity_workload.get("workload_id", "unknown_workload"))
    timing_status = "not_required" if not task.timing_required else "unavailable"
    try:
        reference = load_reference_metrics(task)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        return _invalid_row(
            task=task,
            candidate_id=candidate_id,
            candidate_available=candidate_path.is_file(),
            failure_category="reference_metrics_unavailable",
            notes=f"reference metrics unavailable: {_safe_note(str(exc))}",
            workload_id=workload_id,
            timing_status=timing_status,
        )

    if not candidate_path.is_file():
        return _score_row(
            task=task,
            candidate_id=candidate_id,
            candidate_available=False,
            reference=reference,
            generated_area=None,
            generated_activity=None,
            compile_pass=False,
            correctness_pass=False,
            synth_pass=False,
            timing_status=timing_status,
            failure_category="candidate_missing",
            notes="candidate file missing",
            workload_id=workload_id,
        )

    compile_pass = False
    correctness_pass = False
    synth_pass = False
    generated_activity: float | None = None
    generated_area: float | None = None
    failure_category = "passed"
    notes: list[str] = []

    if not tools.has_icarus:
        failure_category = "tool_unavailable"
        missing = []
        if tools.iverilog is None:
            missing.append("iverilog")
        if tools.vvp is None:
            missing.append("vvp")
        notes.append(f"Icarus unavailable: {', '.join(missing)}")
    elif not tools.healthy_icarus:
        failure_category = "tool_health_failed"
        notes.append("compile or simulation tool failed health check")
    else:
        sim_exe = task_work_dir / "candidate_sim"
        compile_result = _run_command(
            [
                tools.iverilog or "iverilog",
                "-g2012",
                "-o",
                str(sim_exe),
                str(candidate_path),
                str(task.testbench_path),
            ],
            cwd=task_work_dir,
        )
        if compile_result.startup_failed:
            failure_category = "tool_startup_failure"
            notes.append("compile tool failed to start")
        else:
            compile_pass = compile_result.returncode == 0
        if compile_pass:
            sim_result = _run_command([tools.vvp or "vvp", str(sim_exe)], cwd=task_work_dir)
            if sim_result.startup_failed:
                failure_category = "tool_startup_failure"
                notes.append("simulation tool failed to start")
            else:
                correctness_pass = sim_result.returncode == 0
            if correctness_pass:
                vcd_path = task_work_dir / "activity.vcd"
                if vcd_path.is_file():
                    try:
                        window = task.activity_workload["measurement_window"]
                        exclusions = set(task.activity_workload.get("vcd", {}).get("exclude_signals", []))
                        toggle_result = count_vcd_file(
                            vcd_path,
                            exclude_signals=exclusions,
                            start_time=int(window["start_time"]),
                            end_time=int(window["end_time"]),
                        )
                    except (KeyError, TypeError, ValueError, VCDActivityError) as exc:
                        failure_category = "activity_failure"
                        notes.append(f"candidate activity count failed: {_safe_note(str(exc))}")
                    else:
                        generated_activity = float(toggle_result.total_toggles)
                else:
                    failure_category = "activity_unavailable"
                    notes.append("candidate simulation did not produce activity VCD")
            elif not sim_result.startup_failed:
                failure_category = "simulation_failure"
                notes.append("candidate simulation failed")
        elif not compile_result.startup_failed:
            failure_category = "compile_failure"
            notes.append("candidate compile failed")

    if not tools.has_yosys:
        if failure_category == "passed":
            failure_category = "tool_unavailable"
        notes.append("Yosys unavailable")
    elif not tools.healthy_yosys:
        if failure_category == "passed":
            failure_category = "tool_health_failed"
        notes.append("synthesis tool failed health check")
    else:
        synth_result = _run_command(
            [
                tools.yosys or "yosys",
                "-p",
                (
                    f"read_verilog -sv {candidate_path.as_posix()}; "
                    f"hierarchy -top {task.top_module}; "
                    "proc; opt; memory; opt; fsm; opt; stat"
                ),
            ],
            cwd=task_work_dir,
        )
        if synth_result.startup_failed:
            if failure_category == "passed":
                failure_category = "tool_startup_failure"
            notes.append("synthesis tool failed to start")
        else:
            synth_pass = synth_result.returncode == 0
        if synth_pass:
            generated_cells = parse_yosys_generic_cell_count(synth_result.stdout)
            if generated_cells is not None:
                generated_area = float(generated_cells)
            else:
                if failure_category == "passed":
                    failure_category = "area_metric_unavailable"
                notes.append("Yosys did not report candidate generic cell count")
        elif not synth_result.startup_failed:
            if failure_category == "passed":
                failure_category = "synthesis_failure"
            notes.append("candidate synthesis failed")

    if failure_category == "passed":
        if generated_activity is None:
            failure_category = "activity_metric_unavailable"
        elif generated_area is None:
            failure_category = "area_metric_unavailable"

    return _score_row(
        task=task,
        candidate_id=candidate_id,
        candidate_available=True,
        reference=reference,
        generated_area=generated_area,
        generated_activity=generated_activity,
        compile_pass=compile_pass,
        correctness_pass=correctness_pass,
        synth_pass=synth_pass,
        timing_status=timing_status,
        failure_category=failure_category,
        notes="; ".join(notes) if notes else "candidate validated",
        workload_id=workload_id,
    )


def parse_yosys_generic_cell_count(stdout: str) -> int | None:
    from validate_rfid_apbench_references import parse_yosys_generic_cell_count as parse_reference_count

    return parse_reference_count(stdout)


def write_jsonl_report(rows: list[CandidateEvaluationRow], output_jsonl: Path) -> None:
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.sanitized_dict(), sort_keys=True) + "\n")


def write_csv_report(rows: list[CandidateEvaluationRow], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.csv_dict())


def write_markdown_report(
    rows: list[CandidateEvaluationRow],
    output_md: Path,
    tools: ToolAvailability,
    candidate_root: Path,
) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    valid_scores = [row.score for row in rows if row.score_status == "valid" and row.score is not None]
    valid_mean = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    all_sample_mean = sum(_aggregate_row_value(row) for row in rows) / len(rows) if rows else 0.0
    lines = [
        "# v0.5 RFID-APBench Candidate Smoke",
        "",
        "## Scope",
        "",
        "This report evaluates public/synthetic RFID-APBench candidate fixtures against committed reference metrics.",
        "",
        "The candidate fixture source is `reference_copy`, a public smoke set that mirrors reference RTL. It is not model output and does not measure model performance.",
        "",
        "Activity is a VCD toggle-count proxy from the declared workload. It is not measured power, signoff power, or final silicon PPA.",
        "",
        "## Non-Goals",
        "",
        "- No LLM or model evaluations were run.",
        "- No private benchmarks were integrated.",
        "- No training data, fine-tuning scripts, adapters, checkpoints, or model weights were created.",
        "- No raw VCDs, simulator logs, synthesis logs, compiled artifacts, or tool scratch files are committed.",
        "",
        "## Tool Availability",
        "",
        f"- Icarus Verilog compile: {_tool_status(tools.iverilog, tools.iverilog_healthy)}",
        f"- Icarus runtime vvp: {_tool_status(tools.vvp, tools.vvp_healthy)}",
        f"- Yosys synthesis: {_tool_status(tools.yosys, tools.yosys_healthy)}",
        "",
        "## Candidate Fixture Source",
        "",
        f"- Candidate root: `{_display_path(candidate_root)}`",
        "- Candidate id: `reference_copy`",
        "",
        "## Aggregate Gate Counts",
        "",
        f"- Tasks evaluated: {len(rows)}",
        f"- Candidate file available: {sum(1 for row in rows if row.candidate_file_available)}",
        f"- Compile pass: {sum(1 for row in rows if row.compile_pass)}",
        f"- Correctness pass: {sum(1 for row in rows if row.correctness_pass)}",
        f"- Synthesis pass: {sum(1 for row in rows if row.synth_pass)}",
        f"- Final pass: {sum(1 for row in rows if row.final_pass)}",
        "",
        "## Scores",
        "",
        f"- Valid score count: {len(valid_scores)}",
        f"- Mean valid score: {valid_mean:.6f}",
        f"- Mean all-sample score with invalid rows as zero: {all_sample_mean:.6f}",
        "",
        "## Per-Task Candidate Results",
        "",
        "| task_id | candidate_id | final_pass | compile | correctness | synthesis | reference_area | generated_area | reference_activity | generated_activity | area_score | activity_score | score | score_status | failure_category | notes |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        data = row.csv_dict()
        lines.append(
            "| "
            + " | ".join(
                [
                    data["task_id"],
                    data["candidate_id"],
                    data["final_pass"],
                    data["compile_pass"],
                    data["correctness_pass"],
                    data["synth_pass"],
                    data["reference_area"],
                    data["generated_area"],
                    data["reference_activity"],
                    data["generated_activity"],
                    data["area_score"],
                    data["activity_score"],
                    data["score"],
                    data["score_status"],
                    data["failure_category"],
                    data["notes"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Artifact Policy",
            "",
            "The evaluator writes VCDs, simulator binaries, and synthesis scratch material only under the requested temporary work directory. Only sanitized Markdown, CSV, and JSONL reports are intended for commit.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines), encoding="utf-8")


def _score_row(
    *,
    task: RFIDAPBenchTaskInfo,
    candidate_id: str,
    candidate_available: bool,
    reference: ReferenceMetrics,
    generated_area: float | None,
    generated_activity: float | None,
    compile_pass: bool,
    correctness_pass: bool,
    synth_pass: bool,
    timing_status: str,
    failure_category: str,
    notes: str,
    workload_id: str,
) -> CandidateEvaluationRow:
    gates = GateOutcomes(
        extraction_pass=candidate_available,
        compile_pass=compile_pass,
        correctness_pass=correctness_pass,
        correctness_method="simulation",
        synth_pass=synth_pass,
        timing_required=task.timing_required,
        timing_status=timing_status,  # type: ignore[arg-type]
    )
    metrics = MetricInputs(
        reference_area=reference.area,
        generated_area=generated_area,
        area_unit=reference.area_unit,
        reference_activity=reference.activity,
        generated_activity=generated_activity,
        activity_metric=reference.activity_metric,
    )
    identity = SampleIdentity(
        benchmark="rfid_apbench",
        task_id=task.task_id,
        model=candidate_id,
        prompt_profile="candidate_fixture",
        source_run_id="v0.5_candidate_smoke",
        toolchain_id=reference.toolchain_id,
        workload_id=workload_id,
    )
    score_record = score_sample(identity, gates, metrics)
    effective_failure = "passed" if score_record.score_status == "valid" else failure_category
    return CandidateEvaluationRow(
        task_id=task.task_id,
        candidate_id=candidate_id,
        final_pass=score_record.score_status == "valid",
        candidate_file_available=candidate_available,
        compile_pass=compile_pass,
        correctness_pass=correctness_pass,
        synth_pass=synth_pass,
        timing_status=timing_status,
        reference_area=reference.area,
        generated_area=generated_area,
        area_unit=reference.area_unit,
        reference_activity=reference.activity,
        generated_activity=generated_activity,
        activity_metric=reference.activity_metric,
        area_score=score_record.area_score,
        activity_score=score_record.activity_score,
        score=score_record.score,
        score_status=score_record.score_status,
        failure_category=effective_failure,
        toolchain_id=reference.toolchain_id,
        workload_id=workload_id,
        notes=notes,
    )


def _invalid_row(
    *,
    task: RFIDAPBenchTaskInfo,
    candidate_id: str,
    candidate_available: bool,
    failure_category: str,
    notes: str,
    workload_id: str,
    timing_status: str,
) -> CandidateEvaluationRow:
    return CandidateEvaluationRow(
        task_id=task.task_id,
        candidate_id=candidate_id,
        final_pass=False,
        candidate_file_available=candidate_available,
        compile_pass=False,
        correctness_pass=False,
        synth_pass=False,
        timing_status=timing_status,
        reference_area=None,
        generated_area=None,
        area_unit=None,
        reference_activity=None,
        generated_activity=None,
        activity_metric=None,
        area_score=None,
        activity_score=None,
        score=None,
        score_status="invalid",
        failure_category=failure_category,
        toolchain_id="unavailable",
        workload_id=workload_id,
        notes=notes,
    )


def _aggregate_row_value(row: CandidateEvaluationRow) -> float:
    if row.score_status == "invalid" or row.score is None:
        return 0.0
    return row.score


def _run_command(command: list[str], cwd: Path) -> ToolCommandResult:
    return run_tool_command(command, cwd=cwd)


def _tool_status(path: str | None, healthy: bool) -> str:
    if path is None:
        return "unavailable"
    return "healthy" if healthy else "health_failed"


def _safe_note(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")[:160]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate public RFID-APBench candidate RTL fixtures.")
    parser.add_argument("--benchmark-root", type=Path, default=Path("benchmarks/rfid_apbench"))
    parser.add_argument(
        "--candidate-root",
        type=Path,
        default=Path("benchmarks/rfid_apbench/candidates/reference_copy"),
    )
    parser.add_argument("--work-dir", type=Path, default=Path(".tmp/rfid_apbench_candidate_smoke"))
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.5_rfid_apbench_candidate_smoke.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.5_rfid_apbench_candidate_smoke.csv"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("reports/v0.5_rfid_apbench_candidate_smoke.jsonl"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark_root = args.benchmark_root.resolve()
    candidate_root = args.candidate_root.resolve()
    work_dir = args.work_dir.resolve()
    output_md = args.output_md.resolve()
    output_csv = args.output_csv.resolve()
    output_jsonl = args.output_jsonl.resolve()

    tools = detect_tools()
    rows = evaluate_candidates(benchmark_root, candidate_root, work_dir, tools)
    write_jsonl_report(rows, output_jsonl)
    write_csv_report(rows, output_csv)
    write_markdown_report(rows, output_md, tools, candidate_root)

    print(f"Wrote {output_md}")
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
