from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from rtlbench.adapters import ADAPTERS
from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter, RFIDAPBenchAdapterError


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"


def test_rfid_apbench_adapter_is_registered() -> None:
    assert ADAPTERS["rfid_apbench"] is RFIDAPBenchAdapter


def test_rfid_apbench_loads_five_public_tasks() -> None:
    tasks = list(RFIDAPBenchAdapter(BENCHMARK_ROOT).load_tasks())

    assert [task.task_id for task in tasks] == [
        "ap_001_idle_counter",
        "ap_002_command_decoder",
        "ap_003_register_bank_unnecessary_writes",
        "ap_004_crc_serial_parallel_tradeoff",
        "ap_005_fsm_controller_idle_activity",
    ]
    assert all(task.prompt.startswith("Implement the SystemVerilog module") for task in tasks)
    assert all(task.module_name == task.task_id for task in tasks)
    assert all(Path(task.metadata["reference_rtl"]).is_file() for task in tasks)
    assert all(Path(task.metadata["testbench_path"]).is_file() for task in tasks)
    assert all(task.metadata["activity_workload"]["activity_metric"] == "total_signal_toggles" for task in tasks)
    assert all(task.metadata["timing_required"] is False for task in tasks)


def test_rfid_apbench_split_selects_task() -> None:
    tasks = list(RFIDAPBenchAdapter(BENCHMARK_ROOT, split="ap_002_command_decoder").load_tasks())

    assert len(tasks) == 1
    assert tasks[0].task_id == "ap_002_command_decoder"


def test_rfid_apbench_missing_required_file_fails_clearly(tmp_path: Path) -> None:
    root = tmp_path / "rfid_apbench"
    shutil.copytree(BENCHMARK_ROOT, root)
    (root / "tasks" / "ap_001_idle_counter" / "prompt.md").unlink()

    with pytest.raises(FileNotFoundError, match="missing required file"):
        list(RFIDAPBenchAdapter(root).load_tasks())


def test_rfid_apbench_invalid_metadata_fails_clearly(tmp_path: Path) -> None:
    root = tmp_path / "rfid_apbench"
    shutil.copytree(BENCHMARK_ROOT, root)
    task_yaml = root / "tasks" / "ap_001_idle_counter" / "task.yaml"
    text = task_yaml.read_text(encoding="utf-8")
    task_yaml.write_text(text.replace("public_synthetic: true", "public_synthetic: false"), encoding="utf-8")

    with pytest.raises(RFIDAPBenchAdapterError, match="public_synthetic must be true"):
        list(RFIDAPBenchAdapter(root).load_tasks())
