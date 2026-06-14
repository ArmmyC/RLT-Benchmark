from __future__ import annotations

import csv
import io
import json
from typing import Any

from rtlbench.registry import LoadedBaseline, LoadedRun


TABLE_SPECS = (
    ("functional_rtl_generation", "Functional RTL Generation", (
        ("verilogeval", "pass1", "functional_pass_rate", "VerilogEval v2 pass@1 functional"),
        ("verilogeval", "pass5", "pass@5", "VerilogEval v2 pass@5 task recovery"),
        ("rtllm2", "pass1", "functional_pass_rate", "RTLLM 2.0 pass@1 functional"),
    )),
    ("syntax_compile_reliability", "Syntax / Compile Reliability", (
        ("verilogeval", "pass1", "syntax_pass_rate", "VerilogEval v2 pass@1 syntax"),
        ("verilogeval", "pass5", "syntax_pass_rate", "VerilogEval v2 pass@5 syntax"),
        ("rtllm2", "pass1", "syntax_pass_rate", "RTLLM 2.0 syntax"),
    )),
    ("protocollm_lint_only", "ProtocolLLM Lint-Only", (
        ("protocollm", "lint", "syntax_pass_rate", "ProtocolLLM public lint pass"),
    )),
    ("rtlopt_lint_only", "RTL-OPT Lint-Only", (
        ("rtlopt", "lint", "syntax_pass_rate", "RTL-OPT lint pass"),
    )),
    ("rtlopt_synthesis_only", "RTL-OPT Synthesis-Only", (
        ("rtlopt", "synthesis", "functional_pass_rate", "RTL-OPT generic synthesis pass"),
    )),
    ("rtlopt_behavior_preserving_optimization", "RTL-OPT Behavior-Preserving Optimization", (
        ("rtlopt", "equivalence", "equivalence_pass_rate", "RTL-OPT equivalence pass"),
        ("rtlopt", "equivalence", "improved_equiv_passing_tasks", "Equiv-passing tasks with fewer generic cells"),
        ("rtlopt", "equivalence", "average_generic_cell_ratio_among_equiv_passing", "Average generic cell ratio among equiv-passing tasks"),
    )),
)


def _find_run(baseline: LoadedBaseline, model: str, benchmark: str, mode: str) -> LoadedRun | None:
    return next((run for run in baseline.runs if run.registration["model"] == model and run.registration["benchmark"] == benchmark and run.registration["mode"] == mode), None)


def _metric(run: LoadedRun | None, metric: str) -> Any:
    if run is None:
        return None
    if metric.startswith("pass@"):
        return run.summary.get("pass_at_k", {}).get(metric)
    if metric in run.registration.get("rtlopt_metrics", {}):
        return run.registration["rtlopt_metrics"].get(metric)
    return run.summary.get(metric)


def _settings_match(runs: list[LoadedRun]) -> bool:
    settings = {(r.registration["samples_per_task"], r.registration["temperature"], r.registration["top_p"], r.registration["max_tokens"]) for r in runs}
    return len(settings) <= 1


def build_comparison(baseline: LoadedBaseline) -> dict[str, Any]:
    models = list(baseline.metadata["models"])
    tables: dict[str, list[dict[str, Any]]] = {}
    long_rows: list[dict[str, Any]] = []
    for key, _title, specs in TABLE_SPECS:
        table_rows: list[dict[str, Any]] = []
        for benchmark, mode, metric, label in specs:
            runs = [_find_run(baseline, model, benchmark, mode) for model in models]
            available = [run for run in runs if run is not None]
            values = {model: _metric(run, metric) for model, run in zip(models, runs)}
            sources = {model: run.source if run else None for model, run in zip(models, runs)}
            row = {
                "benchmark": benchmark,
                "mode": mode,
                "metric": metric,
                "label": label,
                "evaluation_kind": available[0].registration["evaluation_kind"] if available else None,
                "matched_settings": _settings_match(available),
                "values": values,
                "sources": sources,
            }
            table_rows.append(row)
            for model in models:
                long_rows.append({
                    "baseline": baseline.key,
                    "benchmark": benchmark,
                    "mode": mode,
                    "evaluation_kind": row["evaluation_kind"],
                    "metric": metric,
                    "model": model,
                    "value": values[model],
                    "source": sources[model],
                })
        tables[key] = table_rows
    return {
        "baseline": baseline.key,
        "metadata": baseline.metadata,
        "models": models,
        "runs": [
            {
                **run.registration,
                "resolved_source": run.source,
                "summary": run.summary,
            }
            for run in baseline.runs
        ],
        "tables": tables,
        "rows": long_rows,
        "warnings": list(baseline.warnings),
    }


def format_value(value: Any, metric: str = "") -> str:
    if value is None:
        return "N/A"
    if metric == "improved_equiv_passing_tasks" and isinstance(value, (int, float)):
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def render_markdown(data: dict[str, Any]) -> str:
    metadata = data["metadata"]
    models = data["models"]
    lines = [
        f"# {metadata['name']}",
        "",
        "## Scope",
        "",
        metadata["description"],
        "",
        "Functional simulation, lint-only, synthesis-only, and equivalence results are reported in separate sections and are not treated as interchangeable.",
        "",
        "## Matched Settings Audit",
        "",
        "| Benchmark / mode | Samples per task | Temperature | Top-p | Max tokens | Matched across models? |",
        "|---|---:|---:|---:|---:|---|",
    ]
    seen: set[tuple[str, str]] = set()
    for run in data["runs"]:
        key = (run["benchmark"], run["mode"])
        if key in seen:
            continue
        seen.add(key)
        peers = [item for item in data["runs"] if (item["benchmark"], item["mode"]) == key]
        settings = {(item["samples_per_task"], item["temperature"], item["top_p"], item["max_tokens"]) for item in peers}
        first = peers[0]
        lines.append(f"| {first['benchmark']} / {first['mode']} | {first['samples_per_task']} | {first['temperature']} | {first['top_p']} | {first['max_tokens']} | {'yes' if len(settings) == 1 else 'no'} |")
    lines += [
        "",
        "## Artifact Tracking",
        "",
        "The registry is the source of truth. Values marked `manual_summary` were transcribed from committed reports/manifests because raw LANTA output folders are not available in this checkout. Accessible `summary.json` files override manual values automatically.",
        "",
    ]
    titles = {key: title for key, title, _ in TABLE_SPECS}
    for key, rows in data["tables"].items():
        lines += [f"## {titles[key]}", "", "| Metric | " + " | ".join(models) + " |", "|---|" + "---:|" * len(models)]
        for row in rows:
            values = [format_value(row["values"][model], row["metric"]) for model in models]
            lines.append(f"| {row['label']} | " + " | ".join(values) + " |")
        lines.append("")
        if key == "protocollm_lint_only":
            lines += ["This section is lint-only and does not measure protocol functional correctness.", ""]
        if key == "rtlopt_synthesis_only":
            lines += ["Synthesis success is not proof of behavior preservation.", ""]
        if key == "rtlopt_behavior_preserving_optimization":
            lines += ["Generic Yosys cell counts are an early optimization proxy, not final silicon PPA.", ""]
    lines += [
        "## Key Findings",
        "",
        "- `qwen36-27b` is the strongest baseline for functional RTL generation in the registered results.",
        "- `deepseek-coder-v2-lite-instruct` has the highest RTL-OPT equivalence pass rate.",
        "- High syntax or lint rates do not imply functional correctness.",
        "",
        "## Known Limitations",
        "",
        "- Historical results use explicitly labeled manual summaries when local raw outputs are unavailable.",
        "- ProtocolLLM is lint-only in Baseline v0.1.",
        "- RTL-OPT generic cell ratios are not technology-mapped area, timing, or power results.",
        "- Per-task failure analysis is only available for registered, accessible `results.jsonl` files.",
        "",
        "## Regeneration",
        "",
        "```bash",
        "python scripts/generate_comparison_report.py --registry runs/index.yaml --baseline baseline_v0_1",
        "```",
        "",
        "## Data Sources",
        "",
    ]
    for run in data["runs"]:
        lines.append(f"- `{run['id']}`: `{run['resolved_source']}` from `{run.get('report_path') or run.get('summary_path') or 'registered manual summary'}`")
    if data["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {warning}" for warning in data["warnings"]]
    return "\n".join(lines) + "\n"


def render_json(data: dict[str, Any]) -> str:
    serializable = {key: value for key, value in data.items() if key != "rows"}
    return json.dumps(serializable, indent=2, sort_keys=True) + "\n"


def render_csv(data: dict[str, Any]) -> str:
    fields = ("baseline", "benchmark", "mode", "evaluation_kind", "metric", "model", "value", "source")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in data["rows"]:
        writer.writerow({**row, "value": format_value(row["value"], row["metric"])})
    return output.getvalue()
