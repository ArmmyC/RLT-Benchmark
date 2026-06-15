from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rtlbench.ppa_reporting import (
    load_sanitized_jsonl,
    render_csv,
    render_markdown,
    summarize_records,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize sanitized v0.4 PPA score records without reading benchmark run directories"
    )
    parser.add_argument("input_jsonl", type=Path, help="Sanitized v0.4 PPA JSONL artifact")
    parser.add_argument("--output-md", type=Path, default=Path("reports/v0.4_ppa_summary.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("reports/v0.4_ppa_summary.csv"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = load_sanitized_jsonl(args.input_jsonl)
        summaries = summarize_records(records)
        for path, content in (
            (args.output_md, render_markdown(summaries)),
            (args.output_csv, render_csv(summaries)),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
            print(f"Generated {path}")
        print(f"Loaded {len(records)} sanitized records across {len(summaries)} groups")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
