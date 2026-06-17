from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_rfid_apbench_3sample_baseline.py"
SPEC = importlib.util.spec_from_file_location("run_rfid_apbench_3sample_baseline", SCRIPT_PATH)
assert SPEC is not None
baseline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = baseline
SPEC.loader.exec_module(baseline)

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"


def tasks():
    return list(RFIDAPBenchAdapter(BENCHMARK_ROOT).load_task_infos())


def row(**overrides):
    values = {
        "benchmark": "rfid_apbench",
        "task_id": "ap_001_idle_counter",
        "sample_id": 1,
        "model": "qwen36-27b",
        "prompt_profile": "neutral_baseline",
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 4096,
        "endpoint_status": "available",
        "generation_status": "completed",
        "extraction_status": "failed",
        "candidate_file_available": False,
        "compile_pass": False,
        "correctness_pass": False,
        "synth_pass": False,
        "timing_status": "not_required",
        "area_metric_available": False,
        "activity_metric_available": False,
        "reference_area": 15.0,
        "generated_area": None,
        "area_unit": "generic_cells",
        "reference_activity": 34.0,
        "generated_activity": None,
        "activity_metric": "total_signal_toggles",
        "area_score": None,
        "activity_score": None,
        "score": None,
        "score_status": "invalid",
        "failure_category": "extraction_failure",
        "toolchain_id": "iverilog-vcd-yosys-generic",
        "workload_id": "ap_001_idle_counter_default",
        "notes": "no complete required top rtl_unit extracted",
    }
    values.update(overrides)
    return baseline.BaselineRow(**values)


def test_blocker_rows_cover_five_tasks_and_three_samples() -> None:
    config = baseline.EndpointConfig(
        base_url=None,
        credential=None,
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = baseline.make_blocker_rows(
        tasks=tasks(),
        endpoint=config,
        tools=baseline.ToolAvailability(iverilog=None, vvp=None, yosys=None),
        samples=3,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
    )

    assert len(rows) == 15
    assert {item.task_id for item in rows} == {task.task_id for task in tasks()}
    assert {item.sample_id for item in rows} == {1, 2, 3}
    assert {item.failure_category for item in rows} == {"endpoint_unavailable"}
    for item in rows:
        item.sanitized_dict()


def test_aggregate_score_value_zero_fills_invalid_rows() -> None:
    assert baseline.aggregate_score_value(row()) == 0.0
    assert baseline.aggregate_score_value(row(score_status="valid", score=1.25)) == 1.25


def test_report_writers_emit_sanitized_baseline(tmp_path: Path) -> None:
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = [
        row(sample_id=1),
        row(sample_id=2, extraction_status="passed", score_status="valid", score=1.0, failure_category="passed"),
    ]
    output_md = tmp_path / "baseline.md"
    output_csv = tmp_path / "baseline.csv"
    output_jsonl = tmp_path / "baseline.jsonl"

    baseline.write_markdown_report(
        rows,
        output_md,
        endpoint=config,
        tools=baseline.ToolAvailability(iverilog="iverilog", vvp="vvp", yosys="yosys"),
        run_id="test_run",
    )
    baseline.write_csv_report(rows, output_csv)
    baseline.write_jsonl_report(rows, output_jsonl)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    json_rows = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert "Mean all-sample score" in markdown
    assert "raw_model_response" not in csv_text
    assert json_rows[0]["benchmark"] == "rfid_apbench"
