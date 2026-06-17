from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields
from typing import Any, Literal


TimingStatus = Literal["pass", "fail", "unavailable", "not_required"]
CorrectnessMethod = Literal["simulation", "equivalence"]
ScoreStatus = Literal["valid", "invalid"]

FORBIDDEN_SANITIZED_KEYS = {
    "private_rtl",
    "private_task_text",
    "raw_prompt",
    "raw_prompts",
    "prompt",
    "raw_response",
    "raw_model_response",
    "raw_model_responses",
    "model_response",
    "generated_rtl",
    "vcd",
    "vcd_contents",
    "log",
    "logs",
    "error_log",
    "error_logs",
    "output_path",
    "raw_output_path",
    "secret",
    "api_key",
    "token",
    "password",
    "training_dataset",
    "training_datasets",
    "model_weight",
    "model_weights",
    "lora_adapter",
    "qlora_adapter",
    "dora_adapter",
}
FORBIDDEN_SANITIZED_TOKENS = (
    "$dumpvars",
    "$var ",
    "module ",
    "endmodule",
    "BEGIN PRIVATE",
    "PRIVATE RTL",
    "RAW MODEL RESPONSE",
    "raw_response",
    "raw_prompt",
    "outputs/",
    "raw_responses/",
    "sk-",
    "api_key",
    "password",
    "lora",
    "qlora",
    "dora",
)


class SanitizedRecordError(ValueError):
    pass


@dataclass(frozen=True)
class GateOutcomes:
    extraction_pass: bool = True
    compile_pass: bool = True
    correctness_pass: bool = True
    correctness_method: CorrectnessMethod = "simulation"
    synth_pass: bool = True
    timing_required: bool = False
    timing_status: TimingStatus = "not_required"


@dataclass(frozen=True)
class MetricInputs:
    reference_area: float | None
    generated_area: float | None
    area_unit: str | None
    reference_activity: float | None
    generated_activity: float | None
    activity_metric: str | None
    generated_area_unit: str | None = None
    generated_activity_metric: str | None = None
    timing_constraint: float | None = None
    timing_unit: str | None = None


@dataclass(frozen=True)
class SampleIdentity:
    benchmark: str
    task_id: str
    model: str
    prompt_profile: str
    source_run_id: str
    toolchain_id: str
    workload_id: str


@dataclass(frozen=True)
class AreaActivityScoreRecord:
    schema_version: str
    benchmark: str
    task_id: str
    model: str
    prompt_profile: str
    source_run_id: str
    toolchain_id: str
    workload_id: str
    scoring_mode: Literal["area_activity"]
    final_pass: bool
    extraction_pass: bool
    compile_pass: bool
    correctness_pass: bool
    correctness_method: CorrectnessMethod
    synth_pass: bool
    timing_status: TimingStatus
    timing_pass: bool | None
    timing_constraint: float | None
    timing_unit: str | None
    reference_area: float | None
    generated_area: float | None
    area_unit: str | None
    area_metric_status: Literal["available", "unavailable"]
    reference_activity: float | None
    generated_activity: float | None
    activity_metric: str | None
    activity_metric_status: Literal["available", "unavailable"]
    area_score: float | None
    activity_score: float | None
    score: float | None
    score_status: ScoreStatus
    failure_category: str

    def sanitized_dict(self) -> dict[str, object]:
        data = asdict(self)
        validate_sanitized_record(data)
        return data


def first_failure_category(gates: GateOutcomes) -> str | None:
    if not gates.extraction_pass:
        return "code_extraction_failure"
    if not gates.compile_pass:
        return "compile_failure"
    if not gates.correctness_pass:
        return "equiv_failure" if gates.correctness_method == "equivalence" else "simulation_failure"
    if not gates.synth_pass:
        return "synthesis_failure"
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
) -> AreaActivityScoreRecord:
    timing_pass = _timing_pass(gates)
    gate_failure = first_failure_category(gates)
    if gate_failure is not None:
        return _invalid_record(identity, gates, metrics, gate_failure, timing_pass)

    metric_failure = _metric_failure(metrics)
    if metric_failure is not None:
        return _invalid_record(identity, gates, metrics, metric_failure, timing_pass)

    area_score = capped_ratio(metrics.reference_area, metrics.generated_area)  # type: ignore[arg-type]
    activity_score = capped_ratio(metrics.reference_activity, metrics.generated_activity)  # type: ignore[arg-type]
    score = 0.5 * area_score + 0.5 * activity_score

    return AreaActivityScoreRecord(
        schema_version="v0.5",
        benchmark=identity.benchmark,
        task_id=identity.task_id,
        model=identity.model,
        prompt_profile=identity.prompt_profile,
        source_run_id=identity.source_run_id,
        toolchain_id=identity.toolchain_id,
        workload_id=identity.workload_id,
        scoring_mode="area_activity",
        final_pass=True,
        extraction_pass=gates.extraction_pass,
        compile_pass=gates.compile_pass,
        correctness_pass=gates.correctness_pass,
        correctness_method=gates.correctness_method,
        synth_pass=gates.synth_pass,
        timing_status=gates.timing_status,
        timing_pass=timing_pass,
        timing_constraint=metrics.timing_constraint,
        timing_unit=metrics.timing_unit,
        reference_area=metrics.reference_area,
        generated_area=metrics.generated_area,
        area_unit=metrics.area_unit,
        area_metric_status="available",
        reference_activity=metrics.reference_activity,
        generated_activity=metrics.generated_activity,
        activity_metric=metrics.activity_metric,
        activity_metric_status="available",
        area_score=area_score,
        activity_score=activity_score,
        score=score,
        score_status="valid",
        failure_category="passed",
    )


def aggregate_score_value(record: AreaActivityScoreRecord) -> float:
    if record.score_status == "invalid" or record.score is None:
        return 0.0
    return record.score


def mean_zero_filled_score(records: list[AreaActivityScoreRecord]) -> float:
    if not records:
        return 0.0
    return sum(aggregate_score_value(record) for record in records) / len(records)


def validate_sanitized_record(record: dict[str, Any]) -> None:
    for key, value in record.items():
        normalized_key = str(key).lower()
        if normalized_key in FORBIDDEN_SANITIZED_KEYS:
            raise SanitizedRecordError(f"sanitized record contains forbidden field: {key}")
        _reject_forbidden_payload(value, f"record.{key}")


def _metric_failure(metrics: MetricInputs) -> str | None:
    if not _valid_metric(metrics.reference_area) or not _valid_metric(metrics.generated_area):
        return "area_metric_unavailable"
    if not _units_match(metrics.area_unit, metrics.generated_area_unit):
        return "area_unit_mismatch"
    if not _valid_metric(metrics.reference_activity) or not _valid_metric(metrics.generated_activity):
        return "activity_metric_unavailable"
    if not _units_match(metrics.activity_metric, metrics.generated_activity_metric):
        return "activity_metric_mismatch"
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
    failure_category: str,
    timing_pass: bool | None,
) -> AreaActivityScoreRecord:
    area_status = "available" if (
        _valid_metric(metrics.reference_area)
        and _valid_metric(metrics.generated_area)
        and _units_match(metrics.area_unit, metrics.generated_area_unit)
    ) else "unavailable"
    activity_status = "available" if (
        _valid_metric(metrics.reference_activity)
        and _valid_metric(metrics.generated_activity)
        and _units_match(metrics.activity_metric, metrics.generated_activity_metric)
    ) else "unavailable"
    return AreaActivityScoreRecord(
        schema_version="v0.5",
        benchmark=identity.benchmark,
        task_id=identity.task_id,
        model=identity.model,
        prompt_profile=identity.prompt_profile,
        source_run_id=identity.source_run_id,
        toolchain_id=identity.toolchain_id,
        workload_id=identity.workload_id,
        scoring_mode="area_activity",
        final_pass=False,
        extraction_pass=gates.extraction_pass,
        compile_pass=gates.compile_pass,
        correctness_pass=gates.correctness_pass,
        correctness_method=gates.correctness_method,
        synth_pass=gates.synth_pass,
        timing_status=gates.timing_status,
        timing_pass=timing_pass,
        timing_constraint=metrics.timing_constraint,
        timing_unit=metrics.timing_unit,
        reference_area=metrics.reference_area,
        generated_area=metrics.generated_area,
        area_unit=metrics.area_unit,
        area_metric_status=area_status,  # type: ignore[arg-type]
        reference_activity=metrics.reference_activity,
        generated_activity=metrics.generated_activity,
        activity_metric=metrics.activity_metric,
        activity_metric_status=activity_status,  # type: ignore[arg-type]
        area_score=None,
        activity_score=None,
        score=None,
        score_status="invalid",
        failure_category=failure_category,
    )


def _reject_forbidden_payload(value: Any, location: str) -> None:
    if isinstance(value, dict):
        validate_sanitized_record(value)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_payload(item, f"{location}[{index}]")
    elif isinstance(value, str):
        lowered = value.lower()
        for token in FORBIDDEN_SANITIZED_TOKENS:
            if token.lower() in lowered:
                raise SanitizedRecordError(f"{location} contains forbidden raw/private payload")


SANITIZED_RECORD_FIELDS = tuple(field.name for field in fields(AreaActivityScoreRecord))
