import json
from pathlib import Path

from rtlbench.failure_matrix import build_failure_matrix, render_failure_csv, render_failure_markdown
from rtlbench.registry import load_registry
from test_registry import run_record, write_registry


def write_results(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_failure_matrix_detects_shared_and_unique_outcomes(tmp_path: Path) -> None:
    a = tmp_path / "a.jsonl"
    b = tmp_path / "b.jsonl"
    write_results(a, [
        {"task_id": "all_pass", "sample_id": 0, "final_pass": True, "compile_pass": True, "sim_pass": True, "failure_category": "passed"},
        {"task_id": "all_fail", "sample_id": 0, "final_pass": False, "compile_pass": False, "sim_pass": False, "failure_category": "compile_failure"},
        {"task_id": "unique", "sample_id": 0, "final_pass": True, "compile_pass": True, "sim_pass": True, "failure_category": "passed"},
    ])
    write_results(b, [
        {"task_id": "all_pass", "sample_id": 0, "final_pass": True, "compile_pass": True, "sim_pass": True, "failure_category": "passed"},
        {"task_id": "all_fail", "sample_id": 0, "final_pass": False, "compile_pass": True, "sim_pass": False, "failure_category": "simulation_failure"},
        {"task_id": "unique", "sample_id": 0, "final_pass": False, "compile_pass": True, "sim_pass": False, "failure_category": "simulation_failure"},
    ])
    runs = [run_record(id="a", model="model-a", results_path=str(a)), run_record(id="b", model="model-b", served_model_name="served-b", results_path=str(b))]
    registry = write_registry(tmp_path, runs, models=["model-a", "model-b"])
    data = build_failure_matrix(load_registry(registry, "baseline_v0_1"))
    markdown = render_failure_markdown(data)
    assert "all_fail" in markdown
    assert "all_pass" in markdown
    assert "unique: model-a" in markdown
    assert "compile_failure" in markdown
    assert len(render_failure_csv(data).splitlines()) == 7


def test_missing_results_warns_without_crashing(tmp_path: Path) -> None:
    run = run_record(results_path="missing/results.jsonl")
    data = build_failure_matrix(load_registry(write_registry(tmp_path, [run]), "baseline_v0_1"))
    assert not data["rows"]
    assert "unavailable" in data["warnings"][0]
    assert "Per-task failure data is not available" in render_failure_markdown(data)
