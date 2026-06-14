from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rtlbench.registry import LoadedBaseline, resolve_registered_path


FIELDS = (
    "baseline",
    "benchmark",
    "mode",
    "task_id",
    "model",
    "sample_id",
    "final_pass",
    "compile_pass",
    "sim_pass",
    "failure_category",
    "source_results_path",
)


def build_failure_matrix(
    baseline: LoadedBaseline,
    *,
    benchmark: str | None = None,
    mode: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    coverage: list[dict[str, Any]] = []
    summary_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for run in baseline.runs:
        registration = run.registration
        if benchmark and registration["benchmark"] != benchmark:
            continue
        if mode and registration["mode"] != mode:
            continue
        summary_counts[registration["model"]].update(run.summary.get("failure_categories", {}))
        path = resolve_registered_path(run, "results_path", baseline.repo_root)
        if not path or not path.is_file():
            warnings.append(f"{registration['id']}: results.jsonl unavailable; skipped per-task analysis")
            coverage.append({"run_id": registration["id"], "available": False, "rows": 0})
            continue
        count = 0
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    message = f"{registration['id']}:{line_number}: malformed JSON skipped"
                    if strict:
                        raise ValueError(message) from exc
                    warnings.append(message)
                    continue
                rows.append({
                    "baseline": baseline.key,
                    "benchmark": registration["benchmark"],
                    "mode": registration["mode"],
                    "task_id": record.get("task_id", "unknown"),
                    "model": registration["model"],
                    "sample_id": record.get("sample_id", 0),
                    "final_pass": bool(record.get("final_pass", False)),
                    "compile_pass": bool(record.get("compile_pass", False)),
                    "sim_pass": bool(record.get("sim_pass", False)),
                    "failure_category": record.get("failure_category", "unknown"),
                    "source_results_path": registration.get("results_path", str(path)),
                })
                count += 1
        coverage.append({"run_id": registration["id"], "available": True, "rows": count})
    rows.sort(key=lambda row: (row["benchmark"], row["mode"], row["task_id"], row["model"], row["sample_id"]))
    per_task_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        per_task_counts[row["model"]][row["failure_category"]] += 1
    for model, counts in per_task_counts.items():
        if not summary_counts[model]:
            summary_counts[model].update(counts)
    return {
        "baseline": baseline.key,
        "models": list(baseline.metadata["models"]),
        "rows": rows,
        "coverage": coverage,
        "summary_failure_categories": {model: dict(counts) for model, counts in summary_counts.items()},
        "warnings": warnings,
    }


def _task_outcomes(data: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, bool]]:
    outcomes: dict[tuple[str, str, str], dict[str, bool]] = defaultdict(dict)
    grouped: dict[tuple[str, str, str, str], list[bool]] = defaultdict(list)
    for row in data["rows"]:
        grouped[(row["benchmark"], row["mode"], row["task_id"], row["model"])].append(row["final_pass"])
    for (benchmark, mode, task_id, model), values in grouped.items():
        outcomes[(benchmark, mode, task_id)][model] = any(values)
    return outcomes


def render_failure_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Baseline v0.1 Cross-Model Failure Matrix",
        "",
        "## Coverage Summary",
        "",
        "| Run | Per-task data | Rows |",
        "|---|---|---:|",
    ]
    for item in data["coverage"]:
        lines.append(f"| {item['run_id']} | {'available' if item['available'] else 'unavailable'} | {item['rows']} |")
    summary_counts = data.get("summary_failure_categories", {})
    categories = sorted({category for counts in summary_counts.values() for category in counts})
    lines += ["", "## Failure Category Counts by Model", ""]
    if categories:
        lines += ["| Model | " + " | ".join(categories) + " |", "|---|" + "---:|" * len(categories)]
        for model in data["models"]:
            lines.append(f"| {model} | " + " | ".join(str(summary_counts.get(model, {}).get(category, 0)) for category in categories) + " |")
        lines += ["", "Counts in this table come from registered run summaries; they are available even when per-task files are not local."]
    else:
        lines.append("No summary-level failure categories are registered.")
    if not data["rows"]:
        lines += [
            "",
            "## Per-Task Analysis",
            "",
            "Per-task failure data is not available for this run. The summary-level baseline is still shown from registered summaries.",
            "",
            "## Tasks Failed by All Available Models",
            "",
            "Unavailable without per-task results.",
            "",
            "## Tasks Solved by All Available Models",
            "",
            "Unavailable without per-task results.",
            "",
            "## Tasks Uniquely Solved by One Model",
            "",
            "Unavailable without per-task results.",
            "",
            "## Tasks Recovered by Pass@5",
            "",
            "Unavailable without paired pass@1 and pass@5 per-task results.",
        ]
    else:
        outcomes = _task_outcomes(data)
        failed_all, solved_all, unique = [], [], []
        for key, model_values in sorted(outcomes.items()):
            if len(model_values) < 2:
                continue
            passed = [model for model, result in model_values.items() if result]
            label = "/".join(key)
            if not passed:
                failed_all.append(label)
            if len(passed) == len(model_values):
                solved_all.append(label)
            if len(passed) == 1:
                unique.append(f"{label}: {passed[0]}")
        for title, values in (
            ("Tasks Failed by All Available Models", failed_all),
            ("Tasks Solved by All Available Models", solved_all),
            ("Tasks Uniquely Solved by One Model", unique),
        ):
            lines += ["", f"## {title}", ""] + ([f"- {value}" for value in values] or ["None detected in available data."])
        pass1: dict[tuple[str, str], bool] = {}
        pass5: dict[tuple[str, str], bool] = {}
        for (benchmark, mode, task_id), model_values in outcomes.items():
            if benchmark != "verilogeval":
                continue
            target = pass1 if mode == "pass1" else pass5 if mode == "pass5" else None
            if target is not None:
                for model, passed in model_values.items():
                    target[(task_id, model)] = passed
        recovered = [f"{task}: {model}" for (task, model), passed in sorted(pass5.items()) if passed and not pass1.get((task, model), False)]
        lines += ["", "## Tasks Recovered by Pass@5", ""] + ([f"- {value}" for value in recovered] or ["No pass@1/pass@5 paired per-task data is available."])
    lines += ["", "## Missing Data Warnings", ""] + ([f"- {warning}" for warning in data["warnings"]] or ["None."])
    return "\n".join(lines) + "\n"


def render_failure_csv(data: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data["rows"])
    return output.getvalue()
