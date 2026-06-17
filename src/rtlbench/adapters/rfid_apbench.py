from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from rtlbench.adapters.base import BenchmarkAdapter
from rtlbench.types import BenchmarkTask


REQUIRED_TASK_FILES = (
    "task.yaml",
    "prompt.md",
    "reference.sv",
    "testbench.sv",
    "activity_workload.yaml",
)
REQUIRED_TASK_FIELDS = (
    "schema_version",
    "task_id",
    "public_synthetic",
    "top_module",
    "correctness",
    "synthesis",
    "timing",
    "activity",
)


class RFIDAPBenchAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class RFIDAPBenchTaskInfo:
    task_id: str
    prompt: str
    reference_path: Path
    testbench_path: Path
    top_module: str
    activity_workload: dict[str, Any]
    activity_workload_path: Path
    timing_required: bool
    task_path: Path
    metadata: dict[str, Any]


class RFIDAPBenchAdapter(BenchmarkAdapter):
    name = "rfid_apbench"
    extract_all_modules = False
    evaluator_name = "icarus"

    def load_tasks(self) -> Iterator[BenchmarkTask]:
        for task_info in self.load_task_infos():
            yield BenchmarkTask(
                task_id=task_info.task_id,
                prompt=task_info.prompt,
                testbench=task_info.testbench_path.read_text(encoding="utf-8"),
                module_name=task_info.top_module,
                metadata={
                    "source_format": "rfid_apbench",
                    "reference_rtl": str(task_info.reference_path),
                    "testbench_path": str(task_info.testbench_path),
                    "top_module": task_info.top_module,
                    "activity_workload": task_info.activity_workload,
                    "activity_workload_path": str(task_info.activity_workload_path),
                    "timing_required": task_info.timing_required,
                    "task_path": str(task_info.task_path),
                    "task_metadata": task_info.metadata,
                },
            )

    def load_task_infos(self) -> Iterator[RFIDAPBenchTaskInfo]:
        manifest_path = self.root / "manifest.yaml"
        manifest = _load_yaml_mapping(manifest_path, "manifest")
        _validate_manifest(manifest, manifest_path)
        task_entries = manifest["tasks"]
        if self.split:
            wanted = {item.strip() for item in self.split.split(",") if item.strip()}
            task_entries = [entry for entry in task_entries if entry.get("task_id") in wanted]
        if not task_entries:
            raise RFIDAPBenchAdapterError(f"No RFID-APBench tasks selected from {manifest_path}")

        for entry in task_entries:
            task_id = entry["task_id"]
            task_path = self.root / entry["path"]
            yield self._load_task_info(task_id, task_path)

    def build_prompt(self, task: BenchmarkTask) -> str:
        return task.prompt

    def _load_task_info(self, manifest_task_id: str, task_path: Path) -> RFIDAPBenchTaskInfo:
        if not task_path.is_dir():
            raise FileNotFoundError(f"RFID-APBench task directory not found: {task_path}")
        for filename in REQUIRED_TASK_FILES:
            path = task_path / filename
            if not path.is_file():
                raise FileNotFoundError(f"RFID-APBench task {manifest_task_id} missing required file: {path}")

        task_yaml_path = task_path / "task.yaml"
        task_metadata = _load_yaml_mapping(task_yaml_path, f"{manifest_task_id} task.yaml")
        _validate_task_metadata(task_metadata, manifest_task_id, task_yaml_path)

        workload_name = task_metadata["activity"].get("workload")
        if workload_name != "activity_workload.yaml":
            raise RFIDAPBenchAdapterError(
                f"{task_yaml_path} activity.workload must be activity_workload.yaml"
            )
        activity_workload_path = task_path / workload_name
        activity_workload = _load_yaml_mapping(activity_workload_path, f"{manifest_task_id} activity workload")
        _validate_activity_workload(activity_workload, activity_workload_path)

        return RFIDAPBenchTaskInfo(
            task_id=task_metadata["task_id"],
            prompt=(task_path / "prompt.md").read_text(encoding="utf-8"),
            reference_path=task_path / "reference.sv",
            testbench_path=task_path / "testbench.sv",
            top_module=task_metadata["top_module"],
            activity_workload=activity_workload,
            activity_workload_path=activity_workload_path,
            timing_required=bool(task_metadata["timing"]["required"]),
            task_path=task_path,
            metadata=task_metadata,
        )


def _load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RFIDAPBenchAdapterError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RFIDAPBenchAdapterError(f"{path} must contain a YAML mapping")
    return data


def _validate_manifest(manifest: dict[str, Any], path: Path) -> None:
    if manifest.get("benchmark") != "rfid_apbench":
        raise RFIDAPBenchAdapterError(f"{path} benchmark must be rfid_apbench")
    if manifest.get("scoring_mode") != "area_activity":
        raise RFIDAPBenchAdapterError(f"{path} scoring_mode must be area_activity")
    if manifest.get("public_synthetic") is not True:
        raise RFIDAPBenchAdapterError(f"{path} public_synthetic must be true")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise RFIDAPBenchAdapterError(f"{path} tasks must be a non-empty list")
    seen: set[str] = set()
    for index, entry in enumerate(tasks):
        if not isinstance(entry, dict):
            raise RFIDAPBenchAdapterError(f"{path} tasks[{index}] must be a mapping")
        task_id = entry.get("task_id")
        task_path = entry.get("path")
        if not isinstance(task_id, str) or not task_id:
            raise RFIDAPBenchAdapterError(f"{path} tasks[{index}].task_id must be a string")
        if not isinstance(task_path, str) or not task_path:
            raise RFIDAPBenchAdapterError(f"{path} tasks[{index}].path must be a string")
        if task_id in seen:
            raise RFIDAPBenchAdapterError(f"{path} contains duplicate task_id: {task_id}")
        seen.add(task_id)


def _validate_task_metadata(data: dict[str, Any], expected_task_id: str, path: Path) -> None:
    for field in REQUIRED_TASK_FIELDS:
        if field not in data:
            raise RFIDAPBenchAdapterError(f"{path} missing required field: {field}")
    if data["task_id"] != expected_task_id:
        raise RFIDAPBenchAdapterError(
            f"{path} task_id {data['task_id']!r} does not match manifest task_id {expected_task_id!r}"
        )
    if data["public_synthetic"] is not True:
        raise RFIDAPBenchAdapterError(f"{path} public_synthetic must be true")
    if not isinstance(data["top_module"], str) or not data["top_module"].strip():
        raise RFIDAPBenchAdapterError(f"{path} top_module must be a non-empty string")
    correctness = _require_mapping(data["correctness"], f"{path}.correctness")
    if correctness.get("method") not in {"simulation", "equivalence"}:
        raise RFIDAPBenchAdapterError(f"{path} correctness.method must be simulation or equivalence")
    if correctness.get("testbench") != "testbench.sv":
        raise RFIDAPBenchAdapterError(f"{path} correctness.testbench must be testbench.sv")
    synthesis = _require_mapping(data["synthesis"], f"{path}.synthesis")
    if not isinstance(synthesis.get("flow_id"), str) or not synthesis["flow_id"].strip():
        raise RFIDAPBenchAdapterError(f"{path} synthesis.flow_id must be a non-empty string")
    timing = _require_mapping(data["timing"], f"{path}.timing")
    if not isinstance(timing.get("required"), bool):
        raise RFIDAPBenchAdapterError(f"{path} timing.required must be boolean")
    activity = _require_mapping(data["activity"], f"{path}.activity")
    if activity.get("metric") != "total_signal_toggles":
        raise RFIDAPBenchAdapterError(f"{path} activity.metric must be total_signal_toggles")
    if not isinstance(activity.get("vcd_window"), dict):
        raise RFIDAPBenchAdapterError(f"{path} activity.vcd_window must be a mapping")


def _validate_activity_workload(data: dict[str, Any], path: Path) -> None:
    for field in ("schema_version", "workload_id", "measurement_window", "vcd", "activity_metric"):
        if field not in data:
            raise RFIDAPBenchAdapterError(f"{path} missing required field: {field}")
    if data["activity_metric"] != "total_signal_toggles":
        raise RFIDAPBenchAdapterError(f"{path} activity_metric must be total_signal_toggles")
    window = _require_mapping(data["measurement_window"], f"{path}.measurement_window")
    for field in ("start_time", "end_time"):
        if isinstance(window.get(field), bool) or not isinstance(window.get(field), (int, float)):
            raise RFIDAPBenchAdapterError(f"{path} measurement_window.{field} must be numeric")
    if window["end_time"] < window["start_time"]:
        raise RFIDAPBenchAdapterError(f"{path} measurement_window.end_time must be >= start_time")
    vcd = _require_mapping(data["vcd"], f"{path}.vcd")
    exclusions = vcd.get("exclude_signals", [])
    if not isinstance(exclusions, list) or not all(isinstance(item, str) for item in exclusions):
        raise RFIDAPBenchAdapterError(f"{path} vcd.exclude_signals must be a list of strings")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RFIDAPBenchAdapterError(f"{label} must be a mapping")
    return value
