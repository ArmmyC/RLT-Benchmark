from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_rfid_apbench_candidates.py"
SPEC = importlib.util.spec_from_file_location("evaluate_rfid_apbench_candidates", SCRIPT_PATH)
assert SPEC is not None
candidate_eval = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = candidate_eval
SPEC.loader.exec_module(candidate_eval)

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"
CANDIDATE_ROOT = BENCHMARK_ROOT / "candidates" / "reference_copy"


def first_task():
    return next(RFIDAPBenchAdapter(BENCHMARK_ROOT).load_task_infos())


def row(**overrides):
    values = {
        "task_id": "ap_001_idle_counter",
        "candidate_id": "reference_copy",
        "final_pass": True,
        "candidate_file_available": True,
        "compile_pass": True,
        "correctness_pass": True,
        "synth_pass": True,
        "timing_status": "not_required",
        "reference_area": 15.0,
        "generated_area": 15.0,
        "area_unit": "generic_cells",
        "reference_activity": 34.0,
        "generated_activity": 34.0,
        "activity_metric": "total_signal_toggles",
        "area_score": 1.0,
        "activity_score": 1.0,
        "score": 1.0,
        "score_status": "valid",
        "failure_category": "passed",
        "toolchain_id": "iverilog-vcd-yosys-generic",
        "workload_id": "ap_001_idle_counter_default",
        "notes": "candidate validated",
    }
    values.update(overrides)
    return candidate_eval.CandidateEvaluationRow(**values)


def test_candidate_path_mapping() -> None:
    path = candidate_eval.candidate_path_for_task(CANDIDATE_ROOT, "ap_001_idle_counter")

    assert path == CANDIDATE_ROOT / "ap_001_idle_counter.sv"


def test_load_reference_metrics() -> None:
    metrics = candidate_eval.load_reference_metrics(first_task())

    assert metrics.task_id == "ap_001_idle_counter"
    assert metrics.area == 15.0
    assert metrics.area_unit == "generic_cells"
    assert metrics.activity == 34.0
    assert metrics.activity_metric == "total_signal_toggles"


def test_missing_candidate_produces_invalid_row(tmp_path: Path) -> None:
    tools = candidate_eval.ToolAvailability(iverilog=None, vvp=None, yosys=None)
    task = first_task()

    result = candidate_eval.evaluate_task_candidate(
        task=task,
        candidate_path=tmp_path / "missing.sv",
        candidate_id="missing_set",
        task_work_dir=tmp_path / "work",
        tools=tools,
    )

    assert result.candidate_file_available is False
    assert result.score_status == "invalid"
    assert result.score is None
    assert result.failure_category == "candidate_missing"


def test_score_row_uses_area_activity_scoring() -> None:
    task = first_task()
    reference = candidate_eval.load_reference_metrics(task)

    result = candidate_eval._score_row(
        task=task,
        candidate_id="reference_copy",
        candidate_available=True,
        reference=reference,
        generated_area=reference.area,
        generated_activity=reference.activity,
        compile_pass=True,
        correctness_pass=True,
        synth_pass=True,
        timing_status="not_required",
        failure_category="passed",
        notes="candidate validated",
        workload_id="ap_001_idle_counter_default",
    )

    assert result.score_status == "valid"
    assert result.area_score == pytest.approx(1.0)
    assert result.activity_score == pytest.approx(1.0)
    assert result.score == pytest.approx(1.0)


def test_sanitized_row_rejects_raw_payload() -> None:
    with pytest.raises(Exception):
        row(notes="raw_response payload marker").sanitized_dict()


def test_report_writers_emit_sanitized_outputs(tmp_path: Path) -> None:
    rows = [row(), row(task_id="ap_002_command_decoder", score_status="invalid", score=None, final_pass=False)]
    tools = candidate_eval.ToolAvailability(iverilog=None, vvp=None, yosys=None)
    output_md = tmp_path / "candidate.md"
    output_csv = tmp_path / "candidate.csv"
    output_jsonl = tmp_path / "candidate.jsonl"

    candidate_eval.write_markdown_report(rows, output_md, tools, CANDIDATE_ROOT)
    candidate_eval.write_csv_report(rows, output_csv)
    candidate_eval.write_jsonl_report(rows, output_jsonl)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    json_rows = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert "candidate-fixture" not in markdown
    assert "candidate fixture" in markdown
    assert "not model output" in markdown
    assert "benchmarks/rfid_apbench/candidates/reference_copy" in markdown
    assert "raw_response" not in csv_text
    assert json_rows[0]["score"] == 1.0
