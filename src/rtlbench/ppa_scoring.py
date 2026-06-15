from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Literal


TimingStatus = Literal["pass", "fail", "unavailable", "not_required"]
PowerStatus = Literal["available", "power_unavailable"]
ScoringMode = Literal["area_power", "area_only"]
ScoreStatus = Literal["valid", "invalid"]


@dataclass(frozen=True)
class GateOutcomes:
    extraction_pass: bool = True
    compile_pass: bool = True
    synth_pass: bool = True
    equiv_pass: bool = True
    timing_required: bool = False
    timing_status: TimingStatus = "not_required"


@dataclass(frozen=True)
class MetricInputs:
    reference_area: float | None
    generated_area: float | None
    area_unit: str | None
    generated_area_unit: str | None = None
    reference_power: float | None = None
    generated_power: float | None = None
    power_unit: str | None = None
    generated_power_unit: str | None = None
    power_status: PowerStatus = "power_unavailable"
    timing_constraint: float | None = None
    timing_slack: float | None = None


@dataclass(frozen=True)
class SampleIdentity:
    benchmark: str
    task_id: str
    model: str
    prompt_profile: str
    source_run_id: str
    toolchain_id: str


@dataclass(frozen=True)
class PPAScoreRecord:
    schema_version: str
    benchmark: str
    task_id: str
    model: str
    prompt_profile: str
    source_run_id: str
    toolchain_id: str
    final_pass: bool
    extraction_pass: bool
    compile_pass: bool
    synth_pass: bool
    equiv_pass: bool
    timing_status: TimingStatus
    timing_pass: bool | None
    timing_constraint: float | None
    timing_slack: float | None
    reference_area: float | None
    generated_area: float | None
    area_unit: str | None
    reference_power: float | None
    generated_power: float | None
    power_unit: str | None
    power_status: PowerStatus
    area_score: float | None
    power_score: float | None
    optimization_score: float | None
    scoring_mode: ScoringMode
    score_status: ScoreStatus
    failure_category: str

    def sanitized_dict(self) -> dict[str, object]:
        return asdict(self)


def first_failure_category(gates: GateOutcomes) -> str | None:
    if not gates.extraction_pass:
        return "code_extraction_failure"
    if not gates.compile_pass:
        return "compile_failure"
    if not gates.synth_pass:
        return "synthesis_failure"
    if not gates.equiv_pass:
        return "equiv_failure"
    if gates.timing_required and gates.timing_status != "pass":
        return "timing_failure"
    return None


def capped_ratio(reference: float, generated: float) -> float:
    if not _valid_metric(reference) or not _valid_metric(generated):
        raise ValueError("metrics must be finite and greater than zero")
    return min(reference / generated, 2.0)


def score_sample(
    identity: SampleIdentity,
    gates: GateOutcomes,
    metrics: MetricInputs,
) -> PPAScoreRecord:
    scoring_mode: ScoringMode = "area_power" if metrics.power_status == "available" else "area_only"
    timing_pass = _timing_pass(gates)
    gate_failure = first_failure_category(gates)
    if gate_failure is not None:
        return _invalid_record(identity, gates, metrics, scoring_mode, gate_failure, timing_pass)

    metric_failure = _metric_failure(metrics, scoring_mode)
    if metric_failure is not None:
        return _invalid_record(identity, gates, metrics, scoring_mode, metric_failure, timing_pass)

    area_score = capped_ratio(metrics.reference_area, metrics.generated_area)  # type: ignore[arg-type]
    if scoring_mode == "area_only":
        power_score = None
        optimization_score = area_score
    else:
        power_score = capped_ratio(metrics.reference_power, metrics.generated_power)  # type: ignore[arg-type]
        optimization_score = 0.5 * area_score + 0.5 * power_score

    return PPAScoreRecord(
        schema_version="v0.4",
        benchmark=identity.benchmark,
        task_id=identity.task_id,
        model=identity.model,
        prompt_profile=identity.prompt_profile,
        source_run_id=identity.source_run_id,
        toolchain_id=identity.toolchain_id,
        final_pass=True,
        extraction_pass=gates.extraction_pass,
        compile_pass=gates.compile_pass,
        synth_pass=gates.synth_pass,
        equiv_pass=gates.equiv_pass,
        timing_status=gates.timing_status,
        timing_pass=timing_pass,
        timing_constraint=metrics.timing_constraint,
        timing_slack=metrics.timing_slack,
        reference_area=metrics.reference_area,
        generated_area=metrics.generated_area,
        area_unit=metrics.area_unit,
        reference_power=metrics.reference_power if scoring_mode == "area_power" else None,
        generated_power=metrics.generated_power if scoring_mode == "area_power" else None,
        power_unit=metrics.power_unit if scoring_mode == "area_power" else None,
        power_status=metrics.power_status,
        area_score=area_score,
        power_score=power_score,
        optimization_score=optimization_score,
        scoring_mode=scoring_mode,
        score_status="valid",
        failure_category="passed",
    )


def aggregate_score_value(record: PPAScoreRecord) -> float:
    if record.score_status == "invalid" or record.optimization_score is None:
        return 0.0
    return record.optimization_score


def _metric_failure(metrics: MetricInputs, scoring_mode: ScoringMode) -> str | None:
    if not _valid_metric(metrics.reference_area) or not _valid_metric(metrics.generated_area):
        return "invalid_area_metric"
    if not _units_match(metrics.area_unit, metrics.generated_area_unit):
        return "area_unit_mismatch"

    if scoring_mode == "area_only":
        return None

    if not _valid_metric(metrics.reference_power) or not _valid_metric(metrics.generated_power):
        return "invalid_power_metric"
    if not _units_match(metrics.power_unit, metrics.generated_power_unit):
        return "power_unit_mismatch"
    return None


def _valid_metric(value: float | None) -> bool:
    return value is not None and not isinstance(value, bool) and math.isfinite(value) and value > 0


def _units_match(reference_unit: str | None, generated_unit: str | None) -> bool:
    if not isinstance(reference_unit, str) or not reference_unit.strip():
        return False
    effective_generated_unit = generated_unit if generated_unit is not None else reference_unit
    return (
        isinstance(effective_generated_unit, str)
        and bool(effective_generated_unit.strip())
        and reference_unit.strip() == effective_generated_unit.strip()
    )


def _timing_pass(gates: GateOutcomes) -> bool | None:
    if gates.timing_status in {"unavailable", "not_required"}:
        return None
    return gates.timing_status == "pass"


def _invalid_record(
    identity: SampleIdentity,
    gates: GateOutcomes,
    metrics: MetricInputs,
    scoring_mode: ScoringMode,
    failure_category: str,
    timing_pass: bool | None,
) -> PPAScoreRecord:
    correctness_pass = first_failure_category(gates) is None
    return PPAScoreRecord(
        schema_version="v0.4",
        benchmark=identity.benchmark,
        task_id=identity.task_id,
        model=identity.model,
        prompt_profile=identity.prompt_profile,
        source_run_id=identity.source_run_id,
        toolchain_id=identity.toolchain_id,
        final_pass=correctness_pass,
        extraction_pass=gates.extraction_pass,
        compile_pass=gates.compile_pass,
        synth_pass=gates.synth_pass,
        equiv_pass=gates.equiv_pass,
        timing_status=gates.timing_status,
        timing_pass=timing_pass,
        timing_constraint=metrics.timing_constraint,
        timing_slack=metrics.timing_slack,
        reference_area=metrics.reference_area,
        generated_area=metrics.generated_area,
        area_unit=metrics.area_unit,
        reference_power=metrics.reference_power if scoring_mode == "area_power" else None,
        generated_power=metrics.generated_power if scoring_mode == "area_power" else None,
        power_unit=metrics.power_unit if scoring_mode == "area_power" else None,
        power_status=metrics.power_status,
        area_score=None,
        power_score=None,
        optimization_score=None,
        scoring_mode=scoring_mode,
        score_status="invalid",
        failure_category=failure_category,
    )
