from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REQUIRED_BASELINE_FIELDS = ("name", "description", "created_utc", "status", "models", "benchmarks", "runs")
REQUIRED_RUN_FIELDS = (
    "id",
    "model",
    "served_model_name",
    "benchmark",
    "mode",
    "evaluation_kind",
    "samples_per_task",
    "temperature",
    "top_p",
    "max_tokens",
    "evaluator_type",
    "result_source",
)
EVALUATION_KINDS = {
    "functional_simulation",
    "lint_only",
    "synthesis_only",
    "equivalence",
    "optimization_summary",
}
RESULT_SOURCES = {"summary_json", "manual_summary", "committed_report", "mixed"}
SECRET_KEYS = {"api_key", "token", "password", "secret"}


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedRun:
    registration: dict[str, Any]
    summary: dict[str, Any]
    source: str
    summary_path: Path | None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class LoadedBaseline:
    key: str
    metadata: dict[str, Any]
    runs: tuple[LoadedRun, ...]
    registry_path: Path
    repo_root: Path
    warnings: tuple[str, ...] = ()


def _reject_secret_keys(value: Any, location: str = "registry") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SECRET_KEYS:
                raise RegistryError(f"{location} contains forbidden secret-like key: {key}")
            _reject_secret_keys(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_secret_keys(child, f"{location}[{index}]")


def _require_mapping(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RegistryError(f"{location} must be a mapping")
    return value


def _validate_number(value: Any, location: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RegistryError(f"{location} must be numeric")


def _validate_summary(summary: Any, location: str) -> dict[str, Any]:
    data = _require_mapping(summary, location)
    for key in ("tasks", "samples"):
        if key in data and (isinstance(data[key], bool) or not isinstance(data[key], int) or data[key] < 0):
            raise RegistryError(f"{location}.{key} must be a non-negative integer")
    for key in ("syntax_pass_rate", "functional_pass_rate"):
        if key in data and data[key] is not None:
            _validate_number(data[key], f"{location}.{key}")
    for section in ("pass_at_k", "failure_categories", "evaluation_metrics"):
        if section in data and not isinstance(data[section], dict):
            raise RegistryError(f"{location}.{section} must be a mapping")
    for key, value in data.get("pass_at_k", {}).items():
        if value is not None:
            _validate_number(value, f"{location}.pass_at_k.{key}")
    for key, value in data.get("failure_categories", {}).items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise RegistryError(f"{location}.failure_categories.{key} must be a non-negative integer")
    return data


def _validate_run(run: Any, index: int, model_set: set[str]) -> dict[str, Any]:
    location = f"run {index}"
    data = _require_mapping(run, location)
    for field in REQUIRED_RUN_FIELDS:
        if field not in data:
            raise RegistryError(f"{location} is missing required field: {field}")
    if data["model"] not in model_set:
        raise RegistryError(f"{location} references model not listed by baseline: {data['model']}")
    if data["evaluation_kind"] not in EVALUATION_KINDS:
        raise RegistryError(f"{location} has invalid evaluation_kind: {data['evaluation_kind']}")
    if data["result_source"] not in RESULT_SOURCES:
        raise RegistryError(f"{location} has invalid result_source: {data['result_source']}")
    if isinstance(data["samples_per_task"], bool) or not isinstance(data["samples_per_task"], int) or data["samples_per_task"] <= 0:
        raise RegistryError(f"{location}.samples_per_task must be a positive integer")
    for field in ("temperature", "top_p"):
        _validate_number(data[field], f"{location}.{field}")
    if isinstance(data["max_tokens"], bool) or not isinstance(data["max_tokens"], int) or data["max_tokens"] <= 0:
        raise RegistryError(f"{location}.max_tokens must be a positive integer")
    if "manual_summary" in data:
        _validate_summary(data["manual_summary"], f"{location}.manual_summary")
    if "rtlopt_metrics" in data:
        rtlopt = _require_mapping(data["rtlopt_metrics"], f"{location}.rtlopt_metrics")
        for key, value in rtlopt.items():
            if value is not None:
                _validate_number(value, f"{location}.rtlopt_metrics.{key}")
    return data


def _resolve_path(raw_path: str | None, repo_root: Path) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def load_registry(path: str | Path, baseline_key: str, *, strict: bool = False) -> LoadedBaseline:
    registry_path = Path(path).resolve()
    if not registry_path.is_file():
        raise RegistryError(f"Registry file not found: {registry_path}")
    try:
        document = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RegistryError(f"Invalid YAML in {registry_path}: {exc}") from exc
    root = _require_mapping(document, str(registry_path))
    _reject_secret_keys(root)
    if baseline_key not in root:
        raise RegistryError(f"Baseline not found in registry: {baseline_key}")
    baseline = _require_mapping(root[baseline_key], baseline_key)
    for field in REQUIRED_BASELINE_FIELDS:
        if field not in baseline:
            raise RegistryError(f"{baseline_key} is missing required field: {field}")
    if not isinstance(baseline["models"], list) or not all(isinstance(item, str) for item in baseline["models"]):
        raise RegistryError(f"{baseline_key}.models must be a list of strings")
    if not isinstance(baseline["benchmarks"], list) or not all(isinstance(item, str) for item in baseline["benchmarks"]):
        raise RegistryError(f"{baseline_key}.benchmarks must be a list of strings")
    if not isinstance(baseline["runs"], list):
        raise RegistryError(f"{baseline_key}.runs must be a list")
    model_set = set(baseline["models"])
    registrations = [_validate_run(run, index, model_set) for index, run in enumerate(baseline["runs"])]
    ids = [run["id"] for run in registrations]
    if len(ids) != len(set(ids)):
        raise RegistryError(f"{baseline_key} contains duplicate run ids")
    selections: set[tuple[str, str, str]] = set()
    for run in registrations:
        key = (run["model"], run["benchmark"], run["mode"])
        if key in selections:
            raise RegistryError(f"Ambiguous selected runs for model/benchmark/mode: {key}")
        selections.add(key)

    repo_root = registry_path.parent.parent
    loaded_runs: list[LoadedRun] = []
    warnings: list[str] = []
    for run in registrations:
        run_warnings: list[str] = []
        summary_path = _resolve_path(run.get("summary_path"), repo_root)
        summary: dict[str, Any] | None = None
        source = ""
        if summary_path and summary_path.is_file():
            try:
                summary = _validate_summary(json.loads(summary_path.read_text(encoding="utf-8")), f"{run['id']}.summary_json")
            except (json.JSONDecodeError, OSError) as exc:
                if strict:
                    raise RegistryError(f"Unable to read summary for {run['id']}: {exc}") from exc
                run_warnings.append(f"{run['id']}: summary.json could not be read; using manual_summary fallback")
            else:
                source = "summary_json"
        elif summary_path:
            run_warnings.append(f"{run['id']}: summary.json unavailable at {run['summary_path']}; using manual_summary fallback")
        if summary is None:
            manual = run.get("manual_summary")
            if manual is None:
                raise RegistryError(f"{run['id']} has no accessible summary.json and no manual_summary")
            summary = _validate_summary(manual, f"{run['id']}.manual_summary")
            source = "manual_summary"
        warnings.extend(run_warnings)
        loaded_runs.append(LoadedRun(run, summary, source, summary_path, tuple(run_warnings)))

    metadata = {key: value for key, value in baseline.items() if key != "runs"}
    return LoadedBaseline(baseline_key, metadata, tuple(loaded_runs), registry_path, repo_root, tuple(warnings))


def resolve_registered_path(run: LoadedRun, field: str, repo_root: Path) -> Path | None:
    return _resolve_path(run.registration.get(field), repo_root)
