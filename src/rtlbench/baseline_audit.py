from __future__ import annotations

import csv
import io
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rtlbench.per_task import load_per_task_artifact
from rtlbench.registry import LoadedBaseline


CSV_FIELDS = (
    "run_id",
    "benchmark",
    "mode",
    "model",
    "field",
    "summary_value",
    "artifact_value",
    "delta",
    "status",
)

STANDARD_CATEGORIES = (
    "passed",
    "compile_failure",
    "simulation_failure",
    "code_extraction_failure",
    "timeout",
    "synthesis_failure",
    "equiv_failure",
)


def build_baseline_audit(
    baseline: LoadedBaseline,
    per_task_artifacts: str | Path,
    *,
    strict: bool = False,
    allow_missing_artifact: bool = False,
) -> dict[str, Any]:
    artifact_path = Path(per_task_artifacts)
    if not artifact_path.is_file() and not allow_missing_artifact:
        raise FileNotFoundError(f"Sanitized per-task artifact not found: {artifact_path}")

    artifact_rows, warnings = load_per_task_artifact(artifact_path, strict=strict)
    rows_by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in artifact_rows:
        if row["baseline"] == baseline.key:
            rows_by_run[str(row["source_run_id"])].append(row)

    run_results: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    registered_ids = {run.registration["id"] for run in baseline.runs}
    unknown_run_ids = sorted(set(rows_by_run) - registered_ids)
    if unknown_run_ids:
        warnings.append("Artifact contains unregistered source_run_id values: " + ", ".join(unknown_run_ids))

    for run in baseline.runs:
        registration = run.registration
        run_id = registration["id"]
        run_rows = rows_by_run.get(run_id, [])
        summary_categories = run.summary.get("failure_categories", {})
        artifact_categories = Counter(str(row["failure_category"]) for row in run_rows)
        categories = list(STANDARD_CATEGORIES)
        categories.extend(sorted((set(summary_categories) | set(artifact_categories)) - set(categories)))
        fields = [("samples", run.summary.get("samples"), len(run_rows))]
        fields.extend(
            (category, summary_categories.get(category), artifact_categories.get(category, 0))
            for category in categories
        )

        mismatch_fields: list[str] = []
        missing_artifact = not run_rows
        for field, summary_value, artifact_value in fields:
            if missing_artifact:
                status = "missing"
                delta: int | str = ""
            elif summary_value is None:
                status = "n/a"
                delta = ""
            elif summary_value == artifact_value:
                status = "match"
                delta = 0
            else:
                status = "mismatch"
                delta = artifact_value - summary_value
                mismatch_fields.append(field)
            comparisons.append(
                {
                    "run_id": run_id,
                    "benchmark": registration["benchmark"],
                    "mode": registration["mode"],
                    "model": registration["model"],
                    "field": field,
                    "summary_value": "N/A" if summary_value is None else summary_value,
                    "artifact_value": "N/A" if missing_artifact else artifact_value,
                    "delta": delta,
                    "status": status,
                }
            )
        run_status = "missing" if missing_artifact else "mismatch" if mismatch_fields else "match"
        run_results.append(
            {
                "run_id": run_id,
                "benchmark": registration["benchmark"],
                "mode": registration["mode"],
                "model": registration["model"],
                "summary_samples": run.summary.get("samples"),
                "artifact_rows": None if missing_artifact else len(run_rows),
                "status": run_status,
                "mismatch_fields": mismatch_fields,
            }
        )

    counts = Counter(result["status"] for result in run_results)
    has_findings = bool(counts["mismatch"] or counts["missing"] or unknown_run_ids)
    overall_status = "FAIL" if strict and has_findings else "WARN" if has_findings else "PASS"
    return {
        "baseline": baseline.key,
        "baseline_name": baseline.metadata["name"],
        "artifact_path": artifact_path.as_posix(),
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "strict": strict,
        "overall_status": overall_status,
        "run_results": run_results,
        "comparisons": comparisons,
        "counts": {
            "match": counts["match"],
            "mismatch": counts["mismatch"],
            "missing": counts["missing"],
        },
        "warnings": warnings,
        "unknown_run_ids": unknown_run_ids,
    }


def render_audit_markdown(data: dict[str, Any]) -> str:
    counts = data["counts"]
    lines = [
        "# Baseline v0.2 Consistency Audit",
        "",
        "## Audit Scope",
        "",
        f"- Registry baseline: `{data['baseline']}` ({data['baseline_name']})",
        f"- Sanitized artifact: `{data['artifact_path']}`",
        f"- Generated UTC: {data['generated_utc']}",
        "- Comparison: registered summary sample/category counts versus sanitized per-task rows grouped by `source_run_id`.",
        "",
        "## Overall Status",
        "",
        f"**{data['overall_status']}**",
        "",
        f"- Matching runs: {counts['match']}",
        f"- Mismatching runs: {counts['mismatch']}",
        f"- Missing artifact runs: {counts['missing']}",
        "",
        "Default mode reports mismatches as warnings. Strict mode reports the same findings as FAIL and exits nonzero.",
        "",
        "## Run Summary",
        "",
        "| Run ID | Benchmark | Mode | Model | Summary samples | Artifact rows | Status | Mismatch fields |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for result in data["run_results"]:
        summary_samples = "N/A" if result["summary_samples"] is None else result["summary_samples"]
        artifact_rows = "N/A" if result["artifact_rows"] is None else result["artifact_rows"]
        mismatch_fields = ", ".join(result["mismatch_fields"]) or "-"
        lines.append(
            f"| {result['run_id']} | {result['benchmark']} | {result['mode']} | {result['model']} | "
            f"{summary_samples} | {artifact_rows} | {result['status']} | {mismatch_fields} |"
        )

    lines.extend(
        [
            "",
            "## Category-Count Comparison",
            "",
            "| Run ID | Field | Summary | Artifact | Delta | Status |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for comparison in data["comparisons"]:
        lines.append(
            f"| {comparison['run_id']} | {comparison['field']} | {comparison['summary_value']} | "
            f"{comparison['artifact_value']} | {comparison['delta']} | {comparison['status']} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This audit is diagnostic. It does not rewrite `runs/index.yaml`, `manual_summary`, or benchmark outputs.",
            "- A difference may indicate that an accessible `summary.json` overrides an older manual summary, that the sanitized per-task export reflects corrected source rows, or that the registry has drifted from its registered output.",
            "- `N/A` means the registered summary did not provide that value, so no equality decision was made for that field.",
            "- Review every mismatch before tagging Baseline v0.2; do not edit counts merely to make the audit pass.",
            "",
            "## Loader Warnings",
            "",
        ]
    )
    lines.extend([f"- {warning}" for warning in data["warnings"]] or ["None."])
    return "\n".join(lines) + "\n"


def render_audit_csv(data: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data["comparisons"])
    return output.getvalue()
