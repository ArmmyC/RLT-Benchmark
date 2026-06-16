from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

from rtlbench.ppa_scoring import GateOutcomes, MetricInputs, PPAScoreRecord, SampleIdentity, score_sample


GENERIC_CELL_TOOLCHAIN_ID = "yosys-generic-cell-count-proxy"
MAPPED_AREA_TOOLCHAIN_ID = "yosys-mapped-area"


def load_result_rows(path: str | Path) -> list[dict[str, Any]]:
    artifact = Path(path)
    rows: list[dict[str, Any]] = []
    with artifact.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{artifact}:{line_number}: invalid JSON") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{artifact}:{line_number}: result row must be a JSON object")
            rows.append(value)
    return rows


def export_ppa_records(
    rows: Iterable[dict[str, Any]],
    *,
    prompt_profile: str,
    source_run_id: str | None = None,
) -> list[PPAScoreRecord]:
    if not prompt_profile.strip():
        raise ValueError("prompt_profile is required")
    return [
        result_row_to_ppa_record(row, prompt_profile=prompt_profile, source_run_id=source_run_id)
        for row in rows
    ]


def render_ppa_jsonl(records: Iterable[PPAScoreRecord]) -> str:
    return "".join(json.dumps(record.sanitized_dict(), sort_keys=False) + "\n" for record in records)


def result_row_to_ppa_record(
    row: dict[str, Any],
    *,
    prompt_profile: str,
    source_run_id: str | None = None,
) -> PPAScoreRecord:
    benchmark = _required_string(row, "benchmark")
    if benchmark != "rtlopt":
        raise ValueError(f"unsupported benchmark {benchmark!r}; only 'rtlopt' is supported")

    metrics = _metrics(row)
    area_source = _select_area_source(metrics)
    power_source = _select_power_source(metrics)
    compile_pass = _required_bool(row, "compile_pass")
    failure_category = str(row.get("failure_category", "unknown"))
    extraction_pass = failure_category != "code_extraction_failure"
    generated_metric_available = _valid_metric(area_source.generated_area)
    synth_pass = compile_pass and generated_metric_available
    equiv_pass = compile_pass and bool(row.get("final_pass", False) or metrics.get("equivalence_proven") == 1)
    timing_status, timing_required = _timing_status(metrics)

    identity = SampleIdentity(
        benchmark=benchmark,
        task_id=_sanitized_task_id(row),
        model=_required_string(row, "model"),
        prompt_profile=prompt_profile,
        source_run_id=_source_run_id(row, source_run_id),
        toolchain_id=_toolchain_id(metrics, area_source.generic_proxy),
    )
    gates = GateOutcomes(
        extraction_pass=extraction_pass,
        compile_pass=compile_pass,
        synth_pass=synth_pass,
        equiv_pass=equiv_pass,
        timing_required=timing_required,
        timing_status=timing_status,
    )
    metric_inputs = MetricInputs(
        reference_area=area_source.reference_area,
        generated_area=area_source.generated_area,
        area_unit=area_source.area_unit,
        reference_power=power_source.reference_power,
        generated_power=power_source.generated_power,
        power_unit=power_source.power_unit,
        power_status="available" if power_source.available else "power_unavailable",
        timing_constraint=_optional_number(metrics.get("timing_constraint")),
        timing_slack=_optional_number(metrics.get("timing_slack")),
    )
    return score_sample(identity, gates, metric_inputs)


class _AreaSource:
    def __init__(
        self,
        *,
        reference_area: float | None,
        generated_area: float | None,
        area_unit: str | None,
        generic_proxy: bool,
    ) -> None:
        self.reference_area = reference_area
        self.generated_area = generated_area
        self.area_unit = area_unit
        self.generic_proxy = generic_proxy


class _PowerSource:
    def __init__(
        self,
        *,
        reference_power: float | None,
        generated_power: float | None,
        power_unit: str | None,
    ) -> None:
        self.reference_power = reference_power
        self.generated_power = generated_power
        self.power_unit = power_unit

    @property
    def available(self) -> bool:
        return _valid_metric(self.reference_power) and _valid_metric(self.generated_power)


def _metrics(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("evaluation_metrics")
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("evaluation_metrics must be an object when present")
    return value


def _select_area_source(metrics: dict[str, Any]) -> _AreaSource:
    generated_area = _optional_number(metrics.get("generated_area"))
    reference_area = _optional_number(metrics.get("reference_area"))
    baseline_area = _optional_number(metrics.get("baseline_area"))
    generic_baseline_cells = _optional_number(metrics.get("generic_baseline_cells"))
    generated_cells = _optional_number(metrics.get("generated_cells"))
    if _valid_metric(generated_area) and _valid_metric(reference_area):
        return _AreaSource(
            reference_area=reference_area,
            generated_area=generated_area,
            area_unit=_area_unit(metrics, "mapped_area"),
            generic_proxy=False,
        )

    if _valid_metric(generated_area) and _valid_metric(baseline_area):
        return _AreaSource(
            reference_area=baseline_area,
            generated_area=generated_area,
            area_unit=_area_unit(metrics, "mapped_area"),
            generic_proxy=False,
        )

    if _valid_metric(generic_baseline_cells) and _valid_metric(generated_cells):
        return _AreaSource(
            reference_area=generic_baseline_cells,
            generated_area=generated_cells,
            area_unit="generic_cells",
            generic_proxy=True,
        )

    if generated_area is not None or reference_area is not None:
        return _AreaSource(
            reference_area=reference_area,
            generated_area=generated_area,
            area_unit=_area_unit(metrics, "mapped_area"),
            generic_proxy=False,
        )

    if baseline_area is not None:
        return _AreaSource(
            reference_area=baseline_area,
            generated_area=generated_area,
            area_unit=_area_unit(metrics, "mapped_area"),
            generic_proxy=False,
        )

    return _AreaSource(
        reference_area=generic_baseline_cells,
        generated_area=generated_cells,
        area_unit="generic_cells",
        generic_proxy=True,
    )


def _select_power_source(metrics: dict[str, Any]) -> _PowerSource:
    reference_power = _optional_number(metrics.get("reference_power"))
    generated_power = _optional_number(metrics.get("generated_power"))
    if not (_valid_metric(reference_power) and _valid_metric(generated_power)):
        return _PowerSource(reference_power=None, generated_power=None, power_unit=None)
    return _PowerSource(
        reference_power=reference_power,
        generated_power=generated_power,
        power_unit=_string_or_none(metrics.get("power_unit")) or "W",
    )


def _timing_status(metrics: dict[str, Any]) -> tuple[str, bool]:
    if metrics.get("timing_required") is not True:
        return "not_required", False
    status = metrics.get("timing_status")
    if status not in {"pass", "fail", "unavailable"}:
        return "unavailable", True
    return str(status), True


def _toolchain_id(metrics: dict[str, Any], generic_proxy: bool) -> str:
    explicit = _string_or_none(metrics.get("toolchain_id"))
    if explicit:
        return explicit
    return GENERIC_CELL_TOOLCHAIN_ID if generic_proxy else MAPPED_AREA_TOOLCHAIN_ID


def _area_unit(metrics: dict[str, Any], default: str) -> str:
    return _string_or_none(metrics.get("area_unit")) or default


def _source_run_id(row: dict[str, Any], explicit: str | None) -> str:
    if explicit is not None and explicit.strip():
        return explicit
    for key in ("source_run_id", "run_id"):
        value = _string_or_none(row.get(key))
        if value:
            return value
    return "unspecified-run"


def _sanitized_task_id(row: dict[str, Any]) -> str:
    task_id = _required_string(row, "task_id")
    sample_id = row.get("sample_id")
    if sample_id is None:
        return task_id
    if isinstance(sample_id, bool) or not isinstance(sample_id, int):
        raise ValueError("sample_id must be an integer when present")
    return f"{task_id}#sample-{sample_id}"


def _required_string(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_bool(row: dict[str, Any], key: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _optional_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _valid_metric(value: float | None) -> bool:
    return value is not None and value > 0.0


def _string_or_none(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
