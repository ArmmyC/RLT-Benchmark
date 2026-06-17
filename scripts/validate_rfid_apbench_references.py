from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter, RFIDAPBenchTaskInfo  # noqa: E402
from rtlbench.vcd_activity import VCDActivityError, count_vcd_file  # noqa: E402


REPORT_FIELDS = [
    "task_id",
    "compile_status",
    "simulation_status",
    "activity_status",
    "synthesis_status",
    "area_status",
    "timing_status",
    "reference_area",
    "area_unit",
    "reference_activity",
    "activity_metric",
    "failure_category",
    "notes",
]


@dataclass(frozen=True)
class ToolAvailability:
    iverilog: str | None
    vvp: str | None
    yosys: str | None

    @property
    def has_icarus(self) -> bool:
        return self.iverilog is not None and self.vvp is not None

    @property
    def has_yosys(self) -> bool:
        return self.yosys is not None


@dataclass
class ReferenceValidationRow:
    task_id: str
    compile_status: str
    simulation_status: str
    activity_status: str
    synthesis_status: str
    area_status: str
    timing_status: str
    reference_area: float | None
    area_unit: str | None
    reference_activity: int | None
    activity_metric: str | None
    failure_category: str
    notes: str

    def sanitized_dict(self) -> dict[str, str]:
        raw = asdict(self)
        sanitized: dict[str, str] = {}
        for key in REPORT_FIELDS:
            value = raw[key]
            sanitized[key] = "" if value is None else str(value)
        _reject_unsanitized_payload(sanitized)
        return sanitized


def detect_tools() -> ToolAvailability:
    return ToolAvailability(
        iverilog=shutil.which("iverilog"),
        vvp=shutil.which("vvp"),
        yosys=shutil.which("yosys"),
    )


def validate_references(
    benchmark_root: Path,
    work_dir: Path,
    tools: ToolAvailability | None = None,
) -> list[ReferenceValidationRow]:
    tools = tools or detect_tools()
    tasks = list(RFIDAPBenchAdapter(benchmark_root).load_task_infos())
    rows: list[ReferenceValidationRow] = []
    for task in tasks:
        rows.append(validate_task_reference(task, work_dir / task.task_id, tools))
    return rows


def validate_task_reference(
    task: RFIDAPBenchTaskInfo,
    task_work_dir: Path,
    tools: ToolAvailability,
) -> ReferenceValidationRow:
    task_work_dir.mkdir(parents=True, exist_ok=True)
    timing_status = "not_required" if not task.timing_required else "unavailable"
    activity_metric = str(task.activity_workload.get("activity_metric", "total_signal_toggles"))
    compile_status = "unavailable"
    simulation_status = "unavailable"
    activity_status = "unavailable"
    synthesis_status = "unavailable"
    area_status = "unavailable"
    reference_area: float | None = None
    reference_activity: int | None = None
    area_unit: str | None = None
    notes: list[str] = []
    failure_category = "passed"

    if tools.has_icarus:
        sim_exe = task_work_dir / "reference_sim"
        compile_result = _run_command(
            [
                tools.iverilog or "iverilog",
                "-g2012",
                "-o",
                str(sim_exe),
                str(task.reference_path),
                str(task.testbench_path),
            ],
            cwd=task_work_dir,
        )
        if compile_result.returncode == 0:
            compile_status = "pass"
            sim_result = _run_command([tools.vvp or "vvp", str(sim_exe)], cwd=task_work_dir)
            if sim_result.returncode == 0:
                simulation_status = "pass"
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
                        activity_status = "fail"
                        failure_category = "activity_failure"
                        notes.append(f"VCD activity count failed: {_safe_note(str(exc))}")
                    else:
                        activity_status = "pass"
                        reference_activity = toggle_result.total_toggles
                else:
                    activity_status = "unavailable"
                    failure_category = "activity_unavailable"
                    notes.append("simulation did not produce activity VCD")
            else:
                simulation_status = "fail"
                activity_status = "unavailable"
                failure_category = "simulation_failure"
                notes.append("reference simulation failed")
        else:
            compile_status = "fail"
            simulation_status = "unavailable"
            activity_status = "unavailable"
            failure_category = "compile_failure"
            notes.append("reference compile failed")
    else:
        failure_category = "tool_unavailable"
        missing = []
        if tools.iverilog is None:
            missing.append("iverilog")
        if tools.vvp is None:
            missing.append("vvp")
        notes.append(f"Icarus unavailable: {', '.join(missing)}")

    if tools.has_yosys:
        synth_result = _run_command(
            [
                tools.yosys or "yosys",
                "-p",
                (
                    f"read_verilog -sv {task.reference_path.as_posix()}; "
                    f"hierarchy -top {task.top_module}; "
                    "proc; opt; memory; opt; fsm; opt; stat"
                ),
            ],
            cwd=task_work_dir,
        )
        if synth_result.returncode == 0:
            synthesis_status = "pass"
            cell_count = parse_yosys_generic_cell_count(synth_result.stdout)
            if cell_count is not None:
                area_status = "pass"
                reference_area = float(cell_count)
                area_unit = "generic_cells"
            else:
                area_status = "unavailable"
                if failure_category == "passed":
                    failure_category = "area_unavailable"
                notes.append("Yosys did not report generic cell count")
        else:
            synthesis_status = "fail"
            area_status = "unavailable"
            if failure_category == "passed":
                failure_category = "synthesis_failure"
            notes.append("reference synthesis failed")
    else:
        if failure_category == "passed":
            failure_category = "tool_unavailable"
        notes.append("Yosys unavailable")

    if failure_category == "passed":
        if activity_status != "pass":
            failure_category = "activity_unavailable"
        elif area_status != "pass":
            failure_category = "area_unavailable"

    return ReferenceValidationRow(
        task_id=task.task_id,
        compile_status=compile_status,
        simulation_status=simulation_status,
        activity_status=activity_status,
        synthesis_status=synthesis_status,
        area_status=area_status,
        timing_status=timing_status,
        reference_area=reference_area,
        area_unit=area_unit,
        reference_activity=reference_activity,
        activity_metric=activity_metric if reference_activity is not None else None,
        failure_category=failure_category,
        notes="; ".join(notes) if notes else "reference validated",
    )


def parse_yosys_generic_cell_count(stdout: str) -> int | None:
    matches = re.findall(r"Number of cells:\s+([0-9]+)", stdout)
    if matches:
        return int(matches[-1])
    stat_matches = re.findall(r"^\s*([0-9]+)\s+cells\s*$", stdout, flags=re.MULTILINE)
    if stat_matches:
        return int(stat_matches[-1])
    return None


def write_csv_report(rows: list[ReferenceValidationRow], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.sanitized_dict())


def write_markdown_report(
    rows: list[ReferenceValidationRow],
    output_md: Path,
    tools: ToolAvailability,
) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# v0.5 RFID-APBench Reference Validation",
        "",
        "## Scope",
        "",
        "This report validates the five committed public/synthetic RFID-APBench reference tasks before any model-generated RTL is evaluated.",
        "",
        "Activity is a VCD toggle-count proxy from the declared workload. It is not measured power, signoff power, or final silicon PPA.",
        "",
        "This is reference-only validation. It does not measure model performance, compare models, or evaluate prompt profiles.",
        "",
        "Private RTL, private task text, generated RTL, model outputs, training data, and fine-tuning remain out of scope.",
        "",
        "## Non-Goals",
        "",
        "- No model jobs or benchmark sweeps were run.",
        "- No private benchmarks were added.",
        "- No fine-tuning data, scripts, adapters, checkpoints, or model weights were created.",
        "- No raw VCDs, simulator logs, synthesis logs, compiled artifacts, or tool scratch files are committed.",
        "",
        "## Tool Availability",
        "",
        f"- Icarus Verilog compile: {_tool_status(tools.iverilog)}",
        f"- Icarus runtime vvp: {_tool_status(tools.vvp)}",
        f"- Yosys synthesis: {_tool_status(tools.yosys)}",
        "",
        "## Aggregate Pass Counts",
        "",
        f"- Tasks loaded: {len(rows)}",
        f"- Compile pass: {_count_status(rows, 'compile_status', 'pass')}",
        f"- Simulation pass: {_count_status(rows, 'simulation_status', 'pass')}",
        f"- Activity pass: {_count_status(rows, 'activity_status', 'pass')}",
        f"- Synthesis pass: {_count_status(rows, 'synthesis_status', 'pass')}",
        f"- Area pass: {_count_status(rows, 'area_status', 'pass')}",
        f"- Fully validated references: {sum(1 for row in rows if row.failure_category == 'passed')}",
        "",
        "## Per-Task Results",
        "",
        "| task_id | compile | simulation | activity | synthesis | area | timing | reference_area | area_unit | reference_activity | activity_metric | failure_category | notes/blocker |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        data = row.sanitized_dict()
        lines.append(
            "| "
            + " | ".join(
                [
                    data["task_id"],
                    data["compile_status"],
                    data["simulation_status"],
                    data["activity_status"],
                    data["synthesis_status"],
                    data["area_status"],
                    data["timing_status"],
                    data["reference_area"],
                    data["area_unit"],
                    data["reference_activity"],
                    data["activity_metric"],
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
            "The validation script writes VCDs, simulator binaries, and synthesis scratch material only under the requested temporary work directory. Only this sanitized Markdown report and the companion CSV are intended for commit.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines), encoding="utf-8")


def write_reference_metrics_if_complete(rows: list[ReferenceValidationRow], benchmark_root: Path) -> None:
    for row in rows:
        if (
            row.failure_category != "passed"
            or row.reference_area is None
            or row.reference_activity is None
            or row.area_unit is None
            or row.activity_metric is None
        ):
            continue
        metrics_path = benchmark_root / "tasks" / row.task_id / "expected" / "reference_metrics.yaml"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": "rfid_apbench_reference_metrics/v0.1",
            "task_id": row.task_id,
            "toolchain_id": "iverilog-vcd-yosys-generic",
            "area": {"value": row.reference_area, "unit": row.area_unit},
            "activity": {"value": row.reference_activity, "metric": row.activity_metric},
            "timing": {"required": False, "status": row.timing_status},
        }
        metrics_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


def _tool_status(path: str | None) -> str:
    return "available" if path else "unavailable"


def _count_status(rows: list[ReferenceValidationRow], field: str, status: str) -> int:
    return sum(1 for row in rows if getattr(row, field) == status)


def _safe_note(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")[:160]


def _reject_unsanitized_payload(record: dict[str, str]) -> None:
    forbidden_keys = {
        "raw_prompt",
        "raw_response",
        "generated_rtl",
        "vcd_contents",
        "log",
        "output_path",
        "secret",
        "training_dataset",
        "model_weights",
        "lora_adapter",
        "qlora_adapter",
        "dora_adapter",
    }
    forbidden_tokens = ("$dumpvars", "$var ", "module ", "endmodule", "sk-", "raw_response", "outputs/")
    for key, value in record.items():
        if key.lower() in forbidden_keys:
            raise ValueError(f"forbidden report field: {key}")
        lowered = value.lower()
        if any(token.lower() in lowered for token in forbidden_tokens):
            raise ValueError(f"forbidden report payload in {key}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate public RFID-APBench reference tasks.")
    parser.add_argument("--benchmark-root", type=Path, default=Path("benchmarks/rfid_apbench"))
    parser.add_argument("--work-dir", type=Path, default=Path(".tmp/rfid_apbench_reference_validation"))
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.5_rfid_apbench_reference_validation.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.5_rfid_apbench_reference_validation.csv"))
    parser.add_argument(
        "--write-reference-metrics",
        action="store_true",
        help="Write sanitized per-task reference_metrics.yaml only for fully measured rows.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark_root = args.benchmark_root.resolve()
    work_dir = args.work_dir.resolve()
    output_md = args.output_md.resolve()
    output_csv = args.output_csv.resolve()

    tools = detect_tools()
    rows = validate_references(benchmark_root, work_dir, tools)
    write_csv_report(rows, output_csv)
    write_markdown_report(rows, output_md, tools)
    if args.write_reference_metrics:
        write_reference_metrics_if_complete(rows, benchmark_root)

    print(f"Wrote {output_md}")
    print(f"Wrote {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
