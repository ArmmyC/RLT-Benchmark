from __future__ import annotations

import csv
import io
import json

import pytest

from rtlbench.ppa_reporting import (
    load_sanitized_jsonl,
    render_csv,
    render_markdown,
    summarize_records,
    validate_sanitized_record,
)
from rtlbench.ppa_scoring import GateOutcomes, MetricInputs, SampleIdentity, score_sample


def make_record(
    *,
    task_id: str = "task-1",
    scoring_mode: str = "area_power",
    score: float = 1.25,
    failure_category: str = "passed",
) -> dict[str, object]:
    identity = SampleIdentity(
        benchmark="rtlopt",
        task_id=task_id,
        model="qwen36-27b",
        prompt_profile="neutral_baseline",
        source_run_id="sanitized-run-1",
        toolchain_id="yosys-test-flow",
    )
    gates = GateOutcomes()
    if failure_category == "compile_failure":
        gates = GateOutcomes(compile_pass=False)
    metrics = MetricInputs(
        reference_area=100.0,
        generated_area=100.0 / score,
        area_unit="um2",
        reference_power=10.0 if scoring_mode == "area_power" else None,
        generated_power=10.0 / score if scoring_mode == "area_power" else None,
        power_unit="W" if scoring_mode == "area_power" else None,
        power_status="available" if scoring_mode == "area_power" else "power_unavailable",
    )
    return score_sample(identity, gates, metrics).sanitized_dict()


def test_loads_valid_sanitized_jsonl(tmp_path) -> None:
    path = tmp_path / "scores.jsonl"
    expected = make_record()
    path.write_text(json.dumps(expected) + "\n\n", encoding="utf-8")

    records = load_sanitized_jsonl(path)

    assert len(records) == 1
    assert records[0].task_id == "task-1"
    assert records[0].optimization_score == pytest.approx(1.25)


@pytest.mark.parametrize(
    "field",
    ["raw_rtl", "prompt", "raw_response", "model_response", "logs", "error_log", "api_key"],
)
def test_rejects_forbidden_fields(field: str) -> None:
    record = make_record()
    record[field] = "private payload"

    with pytest.raises(ValueError, match="forbidden field"):
        validate_sanitized_record(record)


def test_rejects_nested_forbidden_fields() -> None:
    record = make_record()
    record["metadata"] = {"api_key": "secret"}

    with pytest.raises(ValueError, match="metadata.api_key"):
        validate_sanitized_record(record)


def test_rejects_missing_required_fields() -> None:
    record = make_record()
    del record["toolchain_id"]

    with pytest.raises(ValueError, match="missing required field.*toolchain_id"):
        validate_sanitized_record(record)


def test_rejects_schema_version_mismatch() -> None:
    record = make_record()
    record["schema_version"] = "v0.3"

    with pytest.raises(ValueError, match="unsupported schema_version"):
        validate_sanitized_record(record)


def test_rejects_internally_inconsistent_score() -> None:
    record = make_record()
    record["area_score"] = None

    with pytest.raises(ValueError, match="valid score requires area_score"):
        validate_sanitized_record(record)


def test_area_only_and_area_power_are_separate_groups() -> None:
    records = [
        validate_sanitized_record(make_record(task_id="full", scoring_mode="area_power")),
        validate_sanitized_record(make_record(task_id="area", scoring_mode="area_only")),
    ]

    summaries = summarize_records(records)

    assert [summary.scoring_mode for summary in summaries] == ["area_only", "area_power"]
    assert [summary.samples for summary in summaries] == [1, 1]


def test_valid_statistics_and_invalid_zero_fill() -> None:
    records = [
        validate_sanitized_record(make_record(task_id="one", score=1.0)),
        validate_sanitized_record(make_record(task_id="two", score=1.5)),
        validate_sanitized_record(
            make_record(task_id="bad", score=2.0, failure_category="compile_failure")
        ),
    ]

    summary = summarize_records(records)[0]

    assert summary.valid_scores == 2
    assert summary.invalid_scores == 1
    assert summary.mean_valid_score == pytest.approx(1.25)
    assert summary.median_valid_score == pytest.approx(1.25)
    assert summary.mean_all_sample_score == pytest.approx(2.5 / 3.0)


def test_gate_and_failure_category_counts() -> None:
    records = [
        validate_sanitized_record(make_record(task_id="good")),
        validate_sanitized_record(make_record(task_id="bad", failure_category="compile_failure")),
    ]

    summary = summarize_records(records)[0]

    assert summary.extraction_pass_count == 2
    assert summary.compile_pass_count == 1
    assert summary.synth_pass_count == 2
    assert summary.equiv_pass_count == 2
    assert summary.timing_pass_count == 0
    assert summary.failure_categories == {"compile_failure": 1, "passed": 1}


def test_markdown_rendering() -> None:
    summary = summarize_records([validate_sanitized_record(make_record())])

    rendered = render_markdown(summary)

    assert "# v0.4 Sanitized PPA Summary" in rendered
    assert "| rtlopt | qwen36-27b | neutral_baseline | area_power |" in rendered
    assert "Invalid samples contribute zero" in rendered
    assert "passed=1" in rendered


def test_csv_rendering() -> None:
    summary = summarize_records([validate_sanitized_record(make_record())])

    rendered = render_csv(summary)
    rows = list(csv.DictReader(io.StringIO(rendered)))

    assert rows[0]["benchmark"] == "rtlopt"
    assert rows[0]["scoring_mode"] == "area_power"
    assert rows[0]["mean_valid_score"] == "1.25"
    assert json.loads(rows[0]["failure_categories"]) == {"passed": 1}
