from __future__ import annotations

from dataclasses import fields

import pytest

from rtlbench.area_activity_scoring import (
    AreaActivityScoreRecord,
    GateOutcomes,
    MetricInputs,
    SampleIdentity,
    SanitizedRecordError,
    aggregate_score_value,
    mean_zero_filled_score,
    score_sample,
    validate_sanitized_record,
)


IDENTITY = SampleIdentity(
    benchmark="rfid_apbench",
    task_id="ap_001_idle_counter",
    model="synthetic-model",
    prompt_profile="neutral_baseline",
    source_run_id="run-1",
    toolchain_id="yosys-generic-vcd-test",
    workload_id="ap_001_idle_counter_default",
)


def metrics(**overrides) -> MetricInputs:
    values = {
        "reference_area": 100.0,
        "generated_area": 80.0,
        "area_unit": "generic_cells",
        "reference_activity": 200.0,
        "generated_activity": 100.0,
        "activity_metric": "total_signal_toggles",
    }
    values.update(overrides)
    return MetricInputs(**values)


def test_valid_area_activity_score() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), metrics())

    assert record.score_status == "valid"
    assert record.scoring_mode == "area_activity"
    assert record.area_score == pytest.approx(1.25)
    assert record.activity_score == pytest.approx(2.0)
    assert record.score == pytest.approx(1.625)
    assert record.final_pass is True
    assert aggregate_score_value(record) == pytest.approx(1.625)


def test_ratios_are_capped_at_two() -> None:
    record = score_sample(
        IDENTITY,
        GateOutcomes(),
        metrics(generated_area=1.0, generated_activity=1.0),
    )

    assert record.area_score == 2.0
    assert record.activity_score == 2.0
    assert record.score == 2.0


@pytest.mark.parametrize(
    ("gates", "category"),
    [
        (GateOutcomes(extraction_pass=False), "code_extraction_failure"),
        (GateOutcomes(compile_pass=False), "compile_failure"),
        (GateOutcomes(correctness_pass=False), "simulation_failure"),
        (GateOutcomes(correctness_pass=False, correctness_method="equivalence"), "equiv_failure"),
        (GateOutcomes(synth_pass=False), "synthesis_failure"),
        (GateOutcomes(timing_required=True, timing_status="fail"), "timing_failure"),
    ],
)
def test_invalid_gate_failure(gates: GateOutcomes, category: str) -> None:
    record = score_sample(IDENTITY, gates, metrics())

    assert record.score_status == "invalid"
    assert record.score is None
    assert record.failure_category == category
    assert aggregate_score_value(record) == 0.0


@pytest.mark.parametrize("value", [None, 0.0, -1.0, float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("field", ["reference_area", "generated_area"])
def test_bad_area_metrics_are_invalid(field: str, value: float | None) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), metrics(**{field: value}))

    assert record.score_status == "invalid"
    assert record.failure_category == "area_metric_unavailable"
    assert record.score is None


@pytest.mark.parametrize("value", [None, 0.0, -1.0, float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("field", ["reference_activity", "generated_activity"])
def test_bad_activity_metrics_are_invalid(field: str, value: float | None) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), metrics(**{field: value}))

    assert record.score_status == "invalid"
    assert record.failure_category == "activity_metric_unavailable"
    assert record.score is None


@pytest.mark.parametrize(
    ("overrides", "category"),
    [
        ({"area_unit": None}, "area_unit_mismatch"),
        ({"area_unit": ""}, "area_unit_mismatch"),
        ({"generated_area_unit": "um2"}, "area_unit_mismatch"),
        ({"activity_metric": None}, "activity_metric_mismatch"),
        ({"activity_metric": ""}, "activity_metric_mismatch"),
        ({"generated_activity_metric": "width_weighted_signal_toggles"}, "activity_metric_mismatch"),
    ],
)
def test_metric_unit_or_method_mismatch_is_invalid(overrides: dict[str, object], category: str) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), metrics(**overrides))

    assert record.score_status == "invalid"
    assert record.failure_category == category


def test_invalid_samples_contribute_zero_to_aggregate() -> None:
    valid = score_sample(IDENTITY, GateOutcomes(), metrics())
    invalid = score_sample(IDENTITY, GateOutcomes(compile_pass=False), metrics())

    assert mean_zero_filled_score([valid, invalid]) == pytest.approx(valid.score / 2)


def test_sanitized_record_has_no_power_or_raw_private_fields() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), metrics())
    sanitized = record.sanitized_dict()
    forbidden = {
        "power",
        "reference_power",
        "generated_power",
        "raw_prompt",
        "raw_response",
        "generated_rtl",
        "vcd_contents",
        "logs",
        "training_datasets",
    }

    assert forbidden.isdisjoint(sanitized)
    assert forbidden.isdisjoint(field.name for field in fields(AreaActivityScoreRecord))


@pytest.mark.parametrize(
    "payload",
    [
        {"raw_prompt": "do not store"},
        {"notes": "module private_payload; endmodule"},
        {"nested": {"api_key": "do-not-store"}},
        {"paths": ["outputs/rfid_apbench/raw_response.jsonl"]},
    ],
)
def test_sanitized_record_rejects_forbidden_payloads(payload: dict[str, object]) -> None:
    with pytest.raises(SanitizedRecordError):
        validate_sanitized_record(payload)
