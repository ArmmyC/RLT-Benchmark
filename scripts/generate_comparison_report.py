from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rtlbench.comparison import build_comparison, render_csv, render_json, render_markdown
from rtlbench.registry import RegistryError, load_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Baseline v0.1 comparison artifacts")
    parser.add_argument("--registry", default="runs/index.yaml")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--output-md", default="reports/baseline_v0.1_public_rtl_benchmarks.md")
    parser.add_argument("--output-json", default="reports/baseline_v0.1_public_rtl_benchmarks.json")
    parser.add_argument("--output-csv", default="reports/baseline_v0.1_public_rtl_benchmarks.csv")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        baseline = load_registry(args.registry, args.baseline, strict=args.strict)
        data = build_comparison(baseline)
        outputs = ((Path(args.output_md), render_markdown(data)), (Path(args.output_json), render_json(data)), (Path(args.output_csv), render_csv(data)))
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
            print(f"Generated {path}")
        print(f"Loaded baseline: {baseline.key}")
        print(f"Registered runs: {len(baseline.runs)}")
        print(f"Warnings: {len(baseline.warnings)} runs used manual_summary fallback because summary.json was unavailable.")
        return 0
    except (RegistryError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
