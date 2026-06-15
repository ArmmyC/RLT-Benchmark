from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts.v0_3_prompt_smoke_lib import BENCHMARKS, OUTPUT_ROOT, PROFILES, parse_selection
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repository root, to sys.path.
    from v0_3_prompt_smoke_lib import BENCHMARKS, OUTPUT_ROOT, PROFILES, parse_selection


@dataclass(frozen=True)
class SmokeSummary:
    benchmark: str
    profile: str
    status: str
    samples: int | None
    pass_count: int | None
    syntax_pass_count: int | None
    syntax_pass_rate: float | None
    functional_pass_count: int | None
    functional_pass_rate: float | None
    failure_categories: dict[str, int]
    output_path: str


def collect_smoke_summaries(
    outputs_root: Path = OUTPUT_ROOT,
    benchmarks: tuple[str, ...] = BENCHMARKS,
    profiles: tuple[str, ...] = PROFILES,
) -> list[SmokeSummary]:
    return [
        _collect_one(outputs_root, benchmark, profile)
        for benchmark in benchmarks
        for profile in profiles
    ]


def _collect_one(outputs_root: Path, benchmark: str, profile: str) -> SmokeSummary:
    profile_root = outputs_root / benchmark / profile
    metadata_paths = sorted((profile_root / benchmark / "qwen36-27b").glob("*/run_metadata.json"))
    finished: list[tuple[str, Path, dict[str, Any]]] = []
    for metadata_path in metadata_paths:
        metadata = _read_json(metadata_path)
        if metadata.get("status") == "finished" and metadata.get("config", {}).get("prompt_profile") == profile:
            finished.append((str(metadata.get("finished_utc", "")), metadata_path, metadata))

    for _, metadata_path, metadata in sorted(finished, reverse=True):
        summary_path = metadata_path.with_name("summary.json")
        if not summary_path.is_file():
            continue
        summary = _read_json(summary_path)
        samples = _optional_int(summary.get("samples"))
        syntax_rate = _optional_float(summary.get("syntax_pass_rate"))
        functional_rate = _optional_float(summary.get("functional_pass_rate"))
        failures = {
            str(key): int(value)
            for key, value in (summary.get("failure_categories") or {}).items()
        }
        return SmokeSummary(
            benchmark=benchmark,
            profile=profile,
            status="finished",
            samples=samples,
            pass_count=failures.get("passed", 0),
            syntax_pass_count=_count_from_rate(samples, syntax_rate),
            syntax_pass_rate=syntax_rate,
            functional_pass_count=_count_from_rate(samples, functional_rate),
            functional_pass_rate=functional_rate,
            failure_categories=failures,
            output_path=str(metadata_path.parent),
        )

    return SmokeSummary(benchmark, profile, "missing", None, None, None, None, None, None, {}, str(profile_root))


def render_markdown(rows: list[SmokeSummary]) -> str:
    lines = [
        "# v0.3 qwen36-27b Prompt Smoke Summary",
        "",
        "This report reads only `summary.json` and `run_metadata.json` from finished smoke runs.",
    ]
    for benchmark in BENCHMARKS:
        benchmark_rows = [row for row in rows if row.benchmark == benchmark]
        if not benchmark_rows:
            continue
        outcome = "Equivalence pass" if benchmark == "rtlopt" else "Functional pass"
        lines.extend(
            [
                "",
                f"## {benchmark}",
                "",
                f"| Prompt profile | Status | Samples | Passed | Syntax/compile pass | {outcome} | Failures | Output path |",
                "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in benchmark_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row.profile,
                        row.status,
                        _number(row.samples),
                        _number(row.pass_count),
                        _pass_value(row.syntax_pass_count, row.syntax_pass_rate),
                        _pass_value(row.functional_pass_count, row.functional_pass_rate),
                        _failures(row.failure_categories),
                        f"`{row.output_path}`",
                    ]
                )
                + " |"
            )
    lines.extend(["", "Review this smoke summary before scheduling any full benchmark run.", ""])
    return "\n".join(lines)


def render_csv(rows: list[SmokeSummary]) -> str:
    handle = io.StringIO(newline="")
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(
        [
            "benchmark",
            "prompt_profile",
            "status",
            "samples",
            "pass_count",
            "syntax_pass_count",
            "syntax_pass_rate",
            "functional_or_equiv_pass_count",
            "functional_or_equiv_pass_rate",
            "failure_categories",
            "output_path",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.benchmark,
                row.profile,
                row.status,
                _csv_value(row.samples),
                _csv_value(row.pass_count),
                _csv_value(row.syntax_pass_count),
                _csv_value(row.syntax_pass_rate),
                _csv_value(row.functional_pass_count),
                _csv_value(row.functional_pass_rate),
                json.dumps(row.failure_categories, sort_keys=True),
                row.output_path,
            ]
        )
    return handle.getvalue()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def _optional_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _optional_float(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def _count_from_rate(samples: int | None, rate: float | None) -> int | None:
    return round(samples * rate) if samples is not None and rate is not None else None


def _number(value: int | None) -> str:
    return str(value) if value is not None else "missing"


def _pass_value(count: int | None, rate: float | None) -> str:
    return f"{count} ({rate:.4f})" if count is not None and rate is not None else "missing"


def _failures(value: dict[str, int]) -> str:
    return ", ".join(f"{key}={count}" for key, count in sorted(value.items())) or "missing"


def _csv_value(value: Any) -> Any:
    return "" if value is None else value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize qwen36-27b v0.3 prompt smoke runs")
    parser.add_argument("--outputs-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--profiles", default=",".join(PROFILES))
    parser.add_argument("--benchmarks", default=",".join(BENCHMARKS))
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.3_qwen36_27b_prompt_smoke_summary.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.3_qwen36_27b_prompt_smoke_summary.csv"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        benchmarks = parse_selection(args.benchmarks, BENCHMARKS, "benchmark")
        profiles = parse_selection(args.profiles, PROFILES, "prompt profile")
        rows = collect_smoke_summaries(args.outputs_root, benchmarks, profiles)
        for path, content in ((args.output_md, render_markdown(rows)), (args.output_csv, render_csv(rows))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
            print(f"Generated {path}")
        print(f"Finished runs: {sum(row.status == 'finished' for row in rows)}; missing: {sum(row.status == 'missing' for row in rows)}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
