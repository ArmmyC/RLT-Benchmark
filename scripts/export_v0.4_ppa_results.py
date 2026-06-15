from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rtlbench.ppa_export import export_ppa_records, load_result_rows, render_ppa_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export sanitized v0.4 PPA score records from structured RTLBench results.jsonl rows"
    )
    parser.add_argument("input_jsonl", type=Path, help="Structured RTLBench results.jsonl")
    parser.add_argument("output_jsonl", type=Path, help="Sanitized v0.4 PPA JSONL output")
    parser.add_argument("--prompt-profile", required=True)
    parser.add_argument("--source-run-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows = load_result_rows(args.input_jsonl)
        records = export_ppa_records(
            rows,
            prompt_profile=args.prompt_profile,
            source_run_id=args.source_run_id,
        )
        args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
        args.output_jsonl.write_text(render_ppa_jsonl(records), encoding="utf-8", newline="")
        print(f"Generated {args.output_jsonl} ({len(records)} rows)")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
