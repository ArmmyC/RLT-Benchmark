from __future__ import annotations

import csv
import io
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Iterable, Mapping

from rtlbench.ppa_scoring import PPAScoreRecord


SCHEMA_VERSION = "v0.4"
RECORD_FIELDS = frozenset(field.name for field in fields(PPAScoreRecord))
FORBIDDEN_FIELDS = frozenset(
    {
        "api_key",
        "error_log",
        "error_logs",
        "extracted_rtl",
        "logs",
        "model_response",
        "private_task_text",
        "prompt",
        "raw_response",
        "raw_rtl",
    }
)
SUMMARY_FIELDS = (
    "benchmark",
    "model",
    "prompt_profile",
    "scoring_mode",
    "samples",
    "valid_scores",
    "invalid_scores",
    "extraction_pass_count",
    "compile_pass_count",
    "synth_pass_count",
    "equiv_pass_count",
    "timing_pass_count",
    "mean_valid_score",
    "median_valid_score",
    "mean_all_sample_score",
    "failure_categories",
)


@dataclass(frozen=True)
class PPASummary:
    benchmark: str
    model: str
    prompt_profile: str
    scoring_mode: str
    samples: int
    valid_scores: int
    invalid_scores: int
    extraction_pass_count: int
    compile_pass_count: int
    synth_pass_count: int
    equiv_pass_count: int
    timing_pass_count: int
    mean_valid_score: float | None
    median_valid_score: float | None
    mean_all_sample_score: float
    failure_categories: dict[str, int]


def load_sanitized_jsonl(path: str | Path) -> list[PPAScoreRecord]:
    artifact = Path(path)
    records: list[PPAScoreRecord] = []
    with artifact.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{artifact}:{line_number}: invalid JSON") from exc
            try:
                records.append(validate_sanitized_record(value))
            except ValueError as exc:
                raise ValueError(f"{artifact}:{line_number}: {exc}") from exc
    return records


def validate_sanitized_record(value: Any) -> PPAScoreRecord:
    if not isinstance(value, dict):
        raise ValueError("record must be a JSON object")

    forbidden = sorted(_find_forbidden_fields(value))
    if forbidden:
        raise ValueError(f"forbidden field(s): {', '.join(forbidden)}")

    keys = set(value)
    missing = sorted(RECORD_FIELDS - keys)
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    unexpected = sorted(keys - RECORD_FIELDS)
    if unexpected:
        raise ValueError(f"unexpected field(s): {', '.join(unexpected)}")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version {value['schema_version']!r}; expected {SCHEMA_VERSION!r}"
        )

    for name in ("benchmark", "task_id", "model", "prompt_profile", "source_run_id", "toolchain_id"):
        _require_nonempty_string(value, name)
    for name in ("final_pass", "extraction_pass", "compile_pass", "synth_pass", "equiv_pass"):
        _require_bool(value, name)
    _require_choice(value, "timing_status", {"pass", "fail", "unavailable", "not_required"})
    _require_optional_bool(value, "timing_pass")
    for name in (
        "timing_constraint",
        "timing_slack",
        "reference_area",
        "generated_area",
        "reference_power",
        "generated_power",
        "area_score",
        "power_score",
        "optimization_score",
    ):
        _require_optional_finite_number(value, name)
    for name in ("area_unit", "power_unit"):
        _require_optional_string(value, name)
    _require_choice(value, "power_status", {"available", "power_unavailable"})
    _require_choice(value, "scoring_mode", {"area_power", "area_only"})
    _require_choice(value, "score_status", {"valid", "invalid"})
    _require_nonempty_string(value, "failure_category")
    _validate_score_consistency(value)

    return PPAScoreRecord(**value)


def summarize_records(records: Iterable[PPAScoreRecord]) -> list[PPASummary]:
    groups: dict[tuple[str, str, str, str], list[PPAScoreRecord]] = defaultdict(list)
    for record in records:
        key = (record.benchmark, record.model, record.prompt_profile, record.scoring_mode)
        groups[key].append(record)

    summaries: list[PPASummary] = []
    for key in sorted(groups):
        group = groups[key]
        valid_values = [
            record.optimization_score
            for record in group
            if record.score_status == "valid" and record.optimization_score is not None
        ]
        all_values = [
            record.optimization_score
            if record.score_status == "valid" and record.optimization_score is not None
            else 0.0
            for record in group
        ]
        failures = Counter(record.failure_category for record in group)
        summaries.append(
            PPASummary(
                benchmark=key[0],
                model=key[1],
                prompt_profile=key[2],
                scoring_mode=key[3],
                samples=len(group),
                valid_scores=len(valid_values),
                invalid_scores=len(group) - len(valid_values),
                extraction_pass_count=sum(record.extraction_pass for record in group),
                compile_pass_count=sum(record.compile_pass for record in group),
                synth_pass_count=sum(record.synth_pass for record in group),
                equiv_pass_count=sum(record.equiv_pass for record in group),
                timing_pass_count=sum(record.timing_pass is True for record in group),
                mean_valid_score=statistics.fmean(valid_values) if valid_values else None,
                median_valid_score=statistics.median(valid_values) if valid_values else None,
                mean_all_sample_score=statistics.fmean(all_values),
                failure_categories=dict(sorted(failures.items())),
            )
        )
    return summaries


def render_markdown(summaries: Iterable[PPASummary]) -> str:
    rows = list(summaries)
    lines = [
        "# v0.4 Sanitized PPA Summary",
        "",
        "This report uses sanitized score records only. Full area/power and area-only results are kept separate.",
        "Invalid samples contribute zero to the all-sample mean.",
        "",
        "| Benchmark | Model | Prompt profile | Scoring mode | Samples | Valid | Invalid | Extraction pass | Compile pass | Synth pass | Equiv pass | Timing pass | Mean valid score | Median valid score | Mean all-sample score | Failure categories |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.benchmark,
                    row.model,
                    row.prompt_profile,
                    row.scoring_mode,
                    str(row.samples),
                    str(row.valid_scores),
                    str(row.invalid_scores),
                    str(row.extraction_pass_count),
                    str(row.compile_pass_count),
                    str(row.synth_pass_count),
                    str(row.equiv_pass_count),
                    str(row.timing_pass_count),
                    _format_score(row.mean_valid_score),
                    _format_score(row.median_valid_score),
                    _format_score(row.mean_all_sample_score),
                    _format_failures(row.failure_categories),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def render_csv(summaries: Iterable[PPASummary]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=SUMMARY_FIELDS, lineterminator="\n")
    writer.writeheader()
    for summary in summaries:
        row = {field: getattr(summary, field) for field in SUMMARY_FIELDS}
        row["failure_categories"] = json.dumps(summary.failure_categories, sort_keys=True)
        writer.writerow(row)
    return output.getvalue()


def _find_forbidden_fields(value: Any, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            name = str(key)
            path = f"{prefix}.{name}" if prefix else name
            if name.lower() in FORBIDDEN_FIELDS:
                found.add(path)
            found.update(_find_forbidden_fields(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.update(_find_forbidden_fields(child, f"{prefix}[{index}]"))
    return found


def _validate_score_consistency(value: dict[str, Any]) -> None:
    expected_timing_pass = {
        "pass": True,
        "fail": False,
        "unavailable": None,
        "not_required": None,
    }[value["timing_status"]]
    if value["timing_pass"] is not expected_timing_pass:
        raise ValueError("timing_pass does not match timing_status")

    if value["score_status"] == "valid":
        if not value["final_pass"]:
            raise ValueError("valid score requires final_pass=true")
        if value["area_score"] is None or value["optimization_score"] is None:
            raise ValueError("valid score requires area_score and optimization_score")
        if value["failure_category"] != "passed":
            raise ValueError("valid score requires failure_category='passed'")
    else:
        if any(value[name] is not None for name in ("area_score", "power_score", "optimization_score")):
            raise ValueError("invalid score requires component and optimization scores to be null")
        if value["failure_category"] == "passed":
            raise ValueError("invalid score requires a failure category")

    if value["scoring_mode"] == "area_only":
        if value["power_status"] != "power_unavailable":
            raise ValueError("area_only requires power_status='power_unavailable'")
        for name in ("reference_power", "generated_power", "power_unit", "power_score"):
            if value[name] is not None:
                raise ValueError(f"area_only requires {name}=null")
    elif value["power_status"] != "available":
        raise ValueError("area_power requires power_status='available'")
    elif value["score_status"] == "valid" and value["power_score"] is None:
        raise ValueError("valid area_power score requires power_score")


def _require_nonempty_string(value: dict[str, Any], name: str) -> None:
    if not isinstance(value[name], str) or not value[name].strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_optional_string(value: dict[str, Any], name: str) -> None:
    if value[name] is not None and not isinstance(value[name], str):
        raise ValueError(f"{name} must be a string or null")


def _require_bool(value: dict[str, Any], name: str) -> None:
    if not isinstance(value[name], bool):
        raise ValueError(f"{name} must be a boolean")


def _require_optional_bool(value: dict[str, Any], name: str) -> None:
    if value[name] is not None and not isinstance(value[name], bool):
        raise ValueError(f"{name} must be a boolean or null")


def _require_optional_finite_number(value: dict[str, Any], name: str) -> None:
    item = value[name]
    if item is not None and (
        isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item)
    ):
        raise ValueError(f"{name} must be a finite number or null")


def _require_choice(value: dict[str, Any], name: str, choices: set[str]) -> None:
    if value[name] not in choices:
        raise ValueError(f"{name} must be one of {', '.join(sorted(choices))}")


def _format_score(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _format_failures(value: dict[str, int]) -> str:
    return ", ".join(f"{category}={count}" for category, count in value.items()) or "none"
