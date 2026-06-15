from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rtlbench.baseline_audit import build_baseline_audit, render_audit_csv, render_audit_markdown
from rtlbench.registry import RegistryError, load_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit baseline summaries against sanitized per-task artifacts")
    parser.add_argument("--registry", default="runs/index.yaml")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--per-task-artifacts", required=True)
    parser.add_argument("--output-md", default="reports/baseline_v0.2_consistency_audit.md")
    parser.add_argument("--output-csv", default="reports/baseline_v0.2_consistency_audit.csv")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--allow-missing-artifact", action="store_true")
    args = parser.parse_args(argv)
    try:
        baseline = load_registry(args.registry, args.baseline, strict=args.strict)
        data = build_baseline_audit(
            baseline,
            args.per_task_artifacts,
            strict=args.strict,
            allow_missing_artifact=args.allow_missing_artifact,
        )
        outputs = (
            (Path(args.output_md), render_audit_markdown(data)),
            (Path(args.output_csv), render_audit_csv(data)),
        )
        for path, content in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
            print(f"Generated {path}")
        counts = data["counts"]
        print(
            f"Status: {data['overall_status']}; matches={counts['match']} "
            f"mismatches={counts['mismatch']} missing={counts['missing']}"
        )
        return 1 if args.strict and data["overall_status"] == "FAIL" else 0
    except (FileNotFoundError, RegistryError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
