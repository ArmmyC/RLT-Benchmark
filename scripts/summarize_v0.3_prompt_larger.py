from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

try:
    from scripts.v0_3_prompt_smoke_lib import BENCHMARKS, LARGER_OUTPUT_ROOT, LARGER_PROFILES, parse_selection
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repository root, to sys.path.
    from v0_3_prompt_smoke_lib import BENCHMARKS, LARGER_OUTPUT_ROOT, LARGER_PROFILES, parse_selection


SUMMARY_SCRIPT = Path(__file__).with_name("summarize_v0.3_prompt_smoke.py")
_summary_spec = importlib.util.spec_from_file_location("summarize_v0_3_prompt_smoke", SUMMARY_SCRIPT)
if not _summary_spec or not _summary_spec.loader:
    raise RuntimeError(f"Unable to load {SUMMARY_SCRIPT}")
_summary_module = importlib.util.module_from_spec(_summary_spec)
sys.modules[_summary_spec.name] = _summary_module
_summary_spec.loader.exec_module(_summary_module)
collect_smoke_summaries = _summary_module.collect_smoke_summaries
render_csv = _summary_module.render_csv
render_markdown = _summary_module.render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize qwen36-27b v0.3 larger prompt-validation runs")
    parser.add_argument("--outputs-root", type=Path, default=LARGER_OUTPUT_ROOT)
    parser.add_argument("--profiles", default=",".join(LARGER_PROFILES))
    parser.add_argument("--benchmarks", default=",".join(BENCHMARKS))
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.3_qwen36_27b_prompt_larger_summary.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.3_qwen36_27b_prompt_larger_summary.csv"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        benchmarks = parse_selection(args.benchmarks, BENCHMARKS, "benchmark")
        profiles = parse_selection(args.profiles, LARGER_PROFILES, "prompt profile")
        rows = collect_smoke_summaries(args.outputs_root, benchmarks, profiles)
        finished_count = sum(row.status == "finished" for row in rows)
        missing_count = sum(row.status == "missing" for row in rows)
        if finished_count == 0:
            print(
                "No finished larger-validation runs found; no summary reports generated. "
                f"Missing combinations: {missing_count}"
            )
            return 0
        markdown = render_markdown(
            rows,
            title="v0.3 qwen36-27b Prompt Larger Validation Summary",
            description=(
                "This report reads only `summary.json` and `run_metadata.json` from finished larger-validation runs."
            ),
            footer=(
                "Review this larger-validation summary before making any final prompt recommendation."
            ),
        )
        for path, content in ((args.output_md, markdown), (args.output_csv, render_csv(rows))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
            print(f"Generated {path}")
        print(f"Finished runs: {finished_count}; missing: {missing_count}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
