from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_rfid_apbench_idle_counter_retry.py"
SPEC = importlib.util.spec_from_file_location("run_rfid_apbench_idle_counter_retry", SCRIPT_PATH)
assert SPEC is not None
retry = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = retry
SPEC.loader.exec_module(retry)

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"


def idle_task():
    return next(
        task
        for task in RFIDAPBenchAdapter(BENCHMARK_ROOT).load_task_infos()
        if task.task_id == "ap_001_idle_counter"
    )


def row(**overrides):
    values = {
        "task_id": "ap_001_idle_counter",
        "sample_id": 1,
        "model": "qwen36-27b",
        "prompt_profile": "neutral_baseline",
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
        "reference_activity": 34.0,
        "generated_activity": None,
        "area_score": None,
        "activity_score": None,
        "score": None,
        "score_status": "invalid",
        "failure_category": "candidate_missing",
        "notes": "no complete required top rtl_unit extracted",
    }
    values.update(overrides)
    return retry.RetryRow(**values)


def test_classify_retry_outcomes() -> None:
    assert retry.classify_retry_outcome([row(), row(sample_id=2), row(sample_id=3)]) == (
        "repeatable_extraction_fragility"
    )
    assert retry.classify_retry_outcome([row(extraction_status="passed", score_status="valid", score=1.0)]) == (
        "one_off_extraction_issue"
    )
    assert retry.classify_retry_outcome([row(failure_category="endpoint_unavailable")]) == "operational_blocker"
    assert "correctness investigation" in retry.recommended_next_action(
        "one_off_extraction_issue",
        [row(extraction_status="passed", failure_category="simulation_failure")],
    )


def test_blocker_rows_are_sanitized() -> None:
    config = retry.EndpointConfig(
        base_url=None,
        credential=None,
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = retry.make_blocker_rows(
        task=idle_task(),
        endpoint=config,
        tools=retry.ToolAvailability(iverilog=None, vvp=None, yosys=None),
        samples=3,
        prompt_profile="neutral_baseline",
    )

    assert len(rows) == 3
    assert {item.failure_category for item in rows} == {"endpoint_unavailable"}
    for item in rows:
        item.sanitized_dict()


def test_report_writers_emit_sanitized_retry(tmp_path: Path) -> None:
    config = retry.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = [row(), row(sample_id=2, extraction_status="passed", score_status="valid", score=1.0)]
    output_md = tmp_path / "retry.md"
    output_csv = tmp_path / "retry.csv"
    output_jsonl = tmp_path / "retry.jsonl"

    retry.write_markdown_report(
        rows,
        output_md,
        endpoint=config,
        tools=retry.ToolAvailability(iverilog="iverilog", vvp="vvp", yosys="yosys"),
        task_id="ap_001_idle_counter",
        run_id="test_run",
    )
    retry.write_csv_report(rows, output_csv)
    retry.write_jsonl_report(rows, output_jsonl)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    json_rows = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert "one_off_extraction_issue" in markdown
    assert "raw_model_response" not in csv_text
    assert json_rows[0]["task_id"] == "ap_001_idle_counter"
