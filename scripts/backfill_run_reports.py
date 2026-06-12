from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    for run_dir in sorted(Path("outputs").glob("*/*")):
        summary_path = run_dir / "summary.json"
        report_path = run_dir / "logs" / "run_report.md"
        if not summary_path.is_file() or report_path.is_file():
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(run_dir, summary), encoding="utf-8")
        print(report_path)


def render_report(run_dir: Path, summary: dict) -> str:
    lines = [
        "# RTLBench Run Report",
        "",
        "- Status: finished",
        "- Note: Backfilled report for a run created before automatic run logging was added.",
        f"- Output directory: `{run_dir}`",
        "",
        "## Findings",
        "",
        f"- Samples: {summary.get('samples')}",
        f"- Tasks: {summary.get('tasks')}",
        f"- Syntax pass rate: {summary.get('syntax_pass_rate')}",
        f"- Functional pass rate: {summary.get('functional_pass_rate')}",
    ]
    for key, value in (summary.get("pass_at_k") or {}).items():
        lines.append(f"- {key}: {value}")
    lines.append(
        "- Failure categories: "
        + json.dumps(summary.get("failure_categories") or {}, sort_keys=True)
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
