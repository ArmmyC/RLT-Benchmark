import json
from pathlib import Path

from rtlbench.baseline_audit import build_baseline_audit, render_audit_csv, render_audit_markdown
from rtlbench.per_task import SANITIZED_FIELDS
from rtlbench.registry import load_registry
from scripts.audit_baseline_consistency import main
from test_registry import run_record, write_registry


def artifact_row(run_id: str, category: str = "passed", **overrides):
    row = {
        "baseline": "baseline_v0_1",
        "benchmark": "verilogeval",
        "mode": "pass1",
        "model": "model-a",
        "served_model_name": "served-a",
        "task_id": "task-a",
        "sample_id": 0,
        "compile_pass": category == "passed",
        "sim_pass": category == "passed",
        "final_pass": category == "passed",
        "failure_category": category,
        "prompt_hash": "hash",
        "latency_seconds": 1.0,
        "completion_tokens": 10,
        "total_tokens": 15,
        "source_run_id": run_id,
    }
    row.update(overrides)
    return row


def write_artifact(path: Path, rows: list[dict]) -> Path:
    path.write_text(
        "".join(json.dumps({field: row[field] for field in SANITIZED_FIELDS}) + "\n" for row in rows),
        encoding="utf-8",
    )
    return path


def load_fixture(tmp_path: Path, summary: dict, rows: list[dict]):
    registry = write_registry(tmp_path, [run_record(manual_summary=summary)])
    artifact = write_artifact(tmp_path / "artifact.jsonl", rows)
    return load_registry(registry, "baseline_v0_1"), artifact


def test_matching_summary_and_artifact_counts(tmp_path: Path) -> None:
    baseline, artifact = load_fixture(
        tmp_path,
        {"samples": 2, "failure_categories": {"passed": 1, "compile_failure": 1}},
        [artifact_row("run_a"), artifact_row("run_a", "compile_failure", sample_id=1)],
    )
    data = build_baseline_audit(baseline, artifact)
    assert data["overall_status"] == "PASS"
    assert data["counts"] == {"match": 1, "mismatch": 0, "missing": 0}


def test_mismatch_and_unknown_category_detection(tmp_path: Path) -> None:
    baseline, artifact = load_fixture(
        tmp_path,
        {"samples": 1, "failure_categories": {"passed": 1}},
        [artifact_row("run_a", "new_failure")],
    )
    data = build_baseline_audit(baseline, artifact)
    assert data["overall_status"] == "WARN"
    assert set(data["run_results"][0]["mismatch_fields"]) == {"passed"}
    unknown = next(row for row in data["comparisons"] if row["field"] == "new_failure")
    assert unknown["summary_value"] == "N/A"
    assert unknown["status"] == "n/a"


def test_missing_artifact_rows_are_reported(tmp_path: Path) -> None:
    registry = write_registry(tmp_path, [run_record(manual_summary={"samples": 1, "failure_categories": {"passed": 1}})])
    artifact = write_artifact(tmp_path / "artifact.jsonl", [])
    data = build_baseline_audit(load_registry(registry, "baseline_v0_1"), artifact)
    assert data["counts"]["missing"] == 1
    assert data["run_results"][0]["status"] == "missing"


def test_missing_summary_values_render_na(tmp_path: Path) -> None:
    baseline, artifact = load_fixture(tmp_path, {}, [artifact_row("run_a", "new_failure")])
    data = build_baseline_audit(baseline, artifact)
    rows = {row["field"]: row for row in data["comparisons"]}
    assert rows["samples"]["summary_value"] == "N/A"
    assert rows["new_failure"]["summary_value"] == "N/A"
    assert data["overall_status"] == "PASS"


def test_renderers_include_run_and_status(tmp_path: Path) -> None:
    baseline, artifact = load_fixture(
        tmp_path,
        {"samples": 1, "failure_categories": {"passed": 1}},
        [artifact_row("run_a", "compile_failure")],
    )
    data = build_baseline_audit(baseline, artifact)
    assert "run_a" in render_audit_markdown(data)
    assert "mismatch" in render_audit_markdown(data)
    assert "run_a" in render_audit_csv(data)
    assert ",mismatch" in render_audit_csv(data)


def test_cli_default_warns_and_strict_returns_failure_on_mismatch(tmp_path: Path) -> None:
    registry = write_registry(
        tmp_path,
        [run_record(manual_summary={"samples": 1, "failure_categories": {"passed": 1}})],
    )
    artifact = write_artifact(tmp_path / "artifact.jsonl", [artifact_row("run_a", "compile_failure")])
    args = [
        "--registry", str(registry), "--baseline", "baseline_v0_1",
        "--per-task-artifacts", str(artifact),
        "--output-md", str(tmp_path / "audit.md"), "--output-csv", str(tmp_path / "audit.csv"),
    ]
    assert main(args) == 0
    assert main([*args, "--strict"]) == 1


def test_missing_artifact_requires_explicit_allow_flag(tmp_path: Path) -> None:
    registry = write_registry(tmp_path)
    missing = tmp_path / "missing.jsonl"
    base_args = [
        "--registry", str(registry), "--baseline", "baseline_v0_1",
        "--per-task-artifacts", str(missing),
        "--output-md", str(tmp_path / "audit.md"), "--output-csv", str(tmp_path / "audit.csv"),
    ]
    assert main(base_args) == 2
    assert main([*base_args, "--allow-missing-artifact"]) == 0
