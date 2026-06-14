import json
from pathlib import Path

import pytest
import yaml

from rtlbench.registry import RegistryError, load_registry


def run_record(**overrides):
    record = {
        "id": "run_a",
        "model": "model-a",
        "served_model_name": "served-a",
        "benchmark": "verilogeval",
        "mode": "pass1",
        "evaluation_kind": "functional_simulation",
        "samples_per_task": 1,
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": 2048,
        "evaluator_type": "icarus",
        "result_source": "manual_summary",
        "manual_summary": {"tasks": 1, "samples": 1, "functional_pass_rate": 0.5},
    }
    record.update(overrides)
    return record


def write_registry(tmp_path: Path, runs=None, **baseline_overrides) -> Path:
    baseline = {
        "name": "Test Baseline",
        "description": "Fixture",
        "created_utc": "2026-06-15T00:00:00Z",
        "status": "frozen",
        "models": ["model-a"],
        "benchmarks": ["verilogeval"],
        "runs": runs or [run_record()],
    }
    baseline.update(baseline_overrides)
    path = tmp_path / "runs" / "index.yaml"
    path.parent.mkdir()
    path.write_text(yaml.safe_dump({"baseline_v0_1": baseline}), encoding="utf-8")
    return path


def test_valid_registry_and_manual_summary_fallback(tmp_path: Path) -> None:
    baseline = load_registry(write_registry(tmp_path), "baseline_v0_1")
    assert baseline.runs[0].source == "manual_summary"
    assert baseline.runs[0].summary["functional_pass_rate"] == 0.5


def test_summary_json_overrides_manual_summary(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    summary.write_text(json.dumps({"tasks": 1, "samples": 1, "functional_pass_rate": 0.75}), encoding="utf-8")
    run = run_record(summary_path=str(summary), manual_summary={"tasks": 1, "samples": 1, "functional_pass_rate": 0.5})
    baseline = load_registry(write_registry(tmp_path, [run]), "baseline_v0_1")
    assert baseline.runs[0].source == "summary_json"
    assert baseline.runs[0].summary["functional_pass_rate"] == 0.75


def test_registry_rejects_missing_baseline(tmp_path: Path) -> None:
    with pytest.raises(RegistryError, match="Baseline not found"):
        load_registry(write_registry(tmp_path), "missing")


def test_registry_rejects_missing_required_field(tmp_path: Path) -> None:
    run = run_record()
    del run["model"]
    with pytest.raises(RegistryError, match="missing required field: model"):
        load_registry(write_registry(tmp_path, [run]), "baseline_v0_1")


def test_registry_rejects_invalid_result_source(tmp_path: Path) -> None:
    with pytest.raises(RegistryError, match="invalid result_source"):
        load_registry(write_registry(tmp_path, [run_record(result_source="invented")]), "baseline_v0_1")


def test_registry_rejects_secret_like_keys(tmp_path: Path) -> None:
    path = write_registry(tmp_path)
    data = yaml.safe_load(path.read_text())
    data["baseline_v0_1"]["api_key"] = "do-not-store"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(RegistryError, match="secret-like key"):
        load_registry(path, "baseline_v0_1")
