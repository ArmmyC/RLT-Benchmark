from __future__ import annotations

from dataclasses import fields

import pytest

from rtlbench.ppa_scoring import (
    GateOutcomes,
    MetricInputs,
    PPAScoreRecord,
    SampleIdentity,
    aggregate_score_value,
    first_failure_category,
    score_sample,
)


IDENTITY = SampleIdentity(
    benchmark="rtlopt",
    task_id="adder",
    model="qwen36-27b",
    prompt_profile="neutral_baseline",
    source_run_id="run-1",
    toolchain_id="yosys-test-flow",
)


def full_metrics(**overrides) -> MetricInputs:
    values = {
        "reference_area": 100.0,
        "generated_area": 80.0,
        "area_unit": "um2",
        "reference_power": 10.0,
        "generated_power": 8.0,
        "power_unit": "W",
        "power_status": "available",
    }
    values.update(overrides)
    return MetricInputs(**values)


def test_valid_full_area_power_score() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics())

    assert record.score_status == "valid"
    assert record.scoring_mode == "area_power"
    assert record.area_score == pytest.approx(1.25)
    assert record.power_score == pytest.approx(1.25)
    assert record.optimization_score == pytest.approx(1.25)
    assert record.final_pass is True
    assert aggregate_score_value(record) == pytest.approx(1.25)


def test_area_score_is_capped_at_two() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics(generated_area=10.0))

    assert record.area_score == 2.0


def test_power_score_is_capped_at_two() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics(generated_power=1.0))

    assert record.power_score == 2.0


def test_area_only_mode_does_not_retain_or_fake_power() -> None:
    metrics = MetricInputs(
        reference_area=100.0,
        generated_area=80.0,
        area_unit="um2",
        power_status="power_unavailable",
    )

    record = score_sample(IDENTITY, GateOutcomes(), metrics)

    assert record.score_status == "valid"
    assert record.scoring_mode == "area_only"
    assert record.power_status == "power_unavailable"
    assert record.reference_power is None
    assert record.generated_power is None
    assert record.power_score is None
    assert record.optimization_score == pytest.approx(1.25)


@pytest.mark.parametrize(
    ("gates", "category"),
    [
        (GateOutcomes(extraction_pass=False), "code_extraction_failure"),
        (GateOutcomes(compile_pass=False), "compile_failure"),
        (GateOutcomes(synth_pass=False), "synthesis_failure"),
        (GateOutcomes(equiv_pass=False), "equiv_failure"),
        (GateOutcomes(timing_required=True, timing_status="fail"), "timing_failure"),
    ],
)
def test_each_invalid_gate(gates: GateOutcomes, category: str) -> None:
    record = score_sample(IDENTITY, gates, full_metrics())

    assert first_failure_category(gates) == category
    assert record.score_status == "invalid"
    assert record.optimization_score is None
    assert record.failure_category == category
    assert aggregate_score_value(record) == 0.0


def test_first_decisive_gate_wins() -> None:
    gates = GateOutcomes(extraction_pass=False, compile_pass=False, synth_pass=False)

    assert first_failure_category(gates) == "code_extraction_failure"


@pytest.mark.parametrize("value", [None, 0.0, -1.0, float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("field", ["reference_area", "generated_area"])
def test_bad_area_metrics_are_invalid(field: str, value: float | None) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics(**{field: value}))

    assert record.score_status == "invalid"
    assert record.final_pass is True
    assert record.failure_category == "invalid_area_metric"
    assert record.optimization_score is None


@pytest.mark.parametrize("value", [None, 0.0, -1.0, float("inf"), float("-inf"), float("nan")])
@pytest.mark.parametrize("field", ["reference_power", "generated_power"])
def test_bad_power_metrics_are_invalid(field: str, value: float | None) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics(**{field: value}))

    assert record.score_status == "invalid"
    assert record.failure_category == "invalid_power_metric"


@pytest.mark.parametrize(
    ("overrides", "category"),
    [
        ({"area_unit": None}, "area_unit_mismatch"),
        ({"area_unit": ""}, "area_unit_mismatch"),
        ({"generated_area_unit": "cells"}, "area_unit_mismatch"),
        ({"power_unit": None}, "power_unit_mismatch"),
        ({"power_unit": "  "}, "power_unit_mismatch"),
        ({"generated_power_unit": "mW"}, "power_unit_mismatch"),
    ],
)
def test_missing_or_mismatched_units_are_invalid(overrides: dict[str, object], category: str) -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics(**overrides))

    assert record.score_status == "invalid"
    assert record.failure_category == category


def test_timing_unavailable_is_allowed_when_not_required() -> None:
    gates = GateOutcomes(timing_required=False, timing_status="unavailable")

    record = score_sample(IDENTITY, gates, full_metrics())

    assert record.score_status == "valid"
    assert record.timing_pass is None


def test_timing_unavailable_is_invalid_when_required() -> None:
    gates = GateOutcomes(timing_required=True, timing_status="unavailable")

    record = score_sample(IDENTITY, gates, full_metrics())

    assert record.score_status == "invalid"
    assert record.failure_category == "timing_failure"
    assert record.timing_pass is None


def test_sanitized_record_has_no_raw_or_private_payload_fields() -> None:
    record = score_sample(IDENTITY, GateOutcomes(), full_metrics())
    sanitized = record.sanitized_dict()
    forbidden = {
        "raw_rtl",
        "extracted_rtl",
        "prompt",
        "raw_response",
        "model_response",
        "logs",
        "error_log",
        "api_key",
    }

    assert forbidden.isdisjoint(sanitized)
    assert forbidden.isdisjoint(field.name for field in fields(PPAScoreRecord))
