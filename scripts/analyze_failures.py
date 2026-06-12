from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import re

MISMATCH_RE = re.compile(r"Mismatches:\s*(\d+)\s+in\s+(\d+)\s+samples", re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze RTLBench failure rows")
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--category", default="code_extraction_failure")
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in (args.run_dir / "results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    failures = [row for row in rows if row["failure_category"] == args.category]
    report = render_report(args.run_dir, args.category, failures)
    output = args.run_dir / "logs" / f"{args.category}_analysis.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(output)


def render_report(run_dir: Path, category: str, failures: list[dict]) -> str:
    lines = [
        f"# {category} Analysis",
        "",
        f"- Run directory: `{run_dir}`",
        f"- Failure count: {len(failures)}",
        "",
    ]
    if not failures:
        lines.append("No matching failures found.")
        return "\n".join(lines) + "\n"

    analyzed = [analyze_row(run_dir, row, category) for row in failures]
    diagnosis = Counter(item["reason"] for item in analyzed)
    lines.extend(
        [
            "## Summary",
            "",
            "- Diagnosis counts: " + json.dumps(dict(diagnosis), sort_keys=True),
        ]
    )

    if category == "code_extraction_failure" and diagnosis.get("truncated_reasoning_comments") == len(failures):
        lines.extend(
            [
                "- All failures started a module but never reached `endmodule`.",
                "- All failures consumed the full completion budget, so the extractor could not recover valid RTL.",
                "- The model wrote long derivations inside Verilog comments after the module header.",
                "",
                "## Recommended Mitigation",
                "",
                "- Keep the baseline unchanged.",
                "- Treat a stricter no-derivation prompt as a separate benchmark condition.",
            ]
        )

    if category == "compile_failure":
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                "- `procedural_assignment_to_wire_output`: model assigned an implicit wire output in procedural logic instead of declaring it `reg`/`logic`.",
                "- `undefined_submodule_or_wrong_top`: model instantiated unavailable helper modules or emitted the wrong top module.",
                "- `benchmark_artifact_port_mismatch`: official prompt/reference/test files disagree; keep the baseline unchanged but flag this task when interpreting results.",
                "- `procedural_code_outside_always`: model emitted procedural statements at module scope.",
            ]
        )

    if category == "simulation_failure":
        total_mismatches = sum(item["mismatches"] for item in analyzed if item["mismatches"] is not None)
        total_samples = sum(item["sim_samples"] for item in analyzed if item["sim_samples"] is not None)
        lines.extend(
            [
                "",
                "## Interpretation",
                "",
                f"- Total mismatches across failed simulations: {total_mismatches} / {total_samples}",
                "- Classifications are heuristic and based on task names, simulator hints, and mismatch behavior.",
                "- These failures compiled successfully, so they represent functionally wrong RTL unless a task-specific benchmark artifact is later found.",
            ]
        )

    lines.extend(["", "## Failure Details", ""])
    for item in analyzed:
        row = item["row"]
        tail = item["raw"][-700:].replace("```", "'''")
        lines.extend(
            [
                f"### {row['task_id']}",
                "",
                f"- Diagnosis: `{item['reason']}`",
                f"- Completion tokens: {item['completion_tokens']} / {row.get('max_tokens')}",
                f"- Raw bytes: {len(item['raw'])}",
                f"- `module` count: {item['module_count']}",
                f"- `endmodule` count: {item['endmodule_count']}",
                f"- Raw response: `{row['raw_response_path']}`",
            ]
        )
        if row.get("extracted_rtl_path"):
            lines.append(f"- Extracted RTL: `{row['extracted_rtl_path']}`")
        if row.get("error_log_path"):
            lines.append(f"- Error log: `{row['error_log_path']}`")
        if item["errors"]:
            lines.extend(["", "Compiler error summary:", "", "```text"])
            lines.extend(item["errors"][:12])
            lines.append("```")
        if item["hints"]:
            lines.extend(["", "Simulation hints:", "", "```text"])
            lines.extend(item["hints"][-14:])
            lines.append("```")
        lines.extend(["", "Tail excerpt:", "", "```text", tail, "```", ""])
    return "\n".join(lines)


def analyze_row(run_dir: Path, row: dict, category: str) -> dict:
    raw = (run_dir / row["raw_response_path"]).read_text(encoding="utf-8", errors="replace")
    log = ""
    if row.get("error_log_path"):
        log = (run_dir / row["error_log_path"]).read_text(encoding="utf-8", errors="replace")
    errors = [
        line
        for line in log.splitlines()
        if any(marker in line.lower() for marker in ("error:", "syntax error", "unknown module type", "warning:"))
    ]
    hints = [
        line
        for line in log.splitlines()
        if any(marker in line for marker in ("Hint:", "Mismatches:", "TIMEOUT"))
    ]
    mismatch_match = MISMATCH_RE.search(log)
    mismatches = int(mismatch_match.group(1)) if mismatch_match else None
    sim_samples = int(mismatch_match.group(2)) if mismatch_match else None
    completion_tokens = (row.get("token_usage") or {}).get("completion_tokens")
    module_count = raw.lower().count("module")
    endmodule_count = raw.lower().count("endmodule")
    return {
        "row": row,
        "raw": raw,
        "log": log,
        "errors": errors,
        "hints": hints,
        "mismatches": mismatches,
        "sim_samples": sim_samples,
        "completion_tokens": completion_tokens,
        "module_count": module_count,
        "endmodule_count": endmodule_count,
        "reason": classify(
            category,
            row,
            raw,
            log,
            completion_tokens,
            module_count,
            endmodule_count,
            mismatches,
            sim_samples,
        ),
    }


def classify(
    category: str,
    row: dict,
    raw: str,
    log: str,
    completion_tokens: int | None,
    module_count: int,
    endmodule_count: int,
    mismatches: int | None = None,
    sim_samples: int | None = None,
) -> str:
    lower_log = log.lower()
    lower_raw = raw.lower()
    if category == "code_extraction_failure":
        if module_count > 0 and endmodule_count == 0 and completion_tokens == row.get("max_tokens"):
            return "truncated_reasoning_comments"
        if module_count > 0 and endmodule_count == 0:
            return "incomplete_module"
        if module_count == 0:
            return "no_module_found"
        return "extractor_pattern_gap"

    if category == "compile_failure":
        if "not a valid l-value" in lower_log:
            return "procedural_assignment_to_wire_output"
        if "is not a port of good1" in lower_log and "is not a port of top_module1" in lower_log:
            return "benchmark_artifact_port_mismatch"
        if "unknown module type" in lower_log:
            return "undefined_submodule_or_wrong_top"
        if "syntax error" in lower_log and ("if (" in lower_raw or "for (" in lower_raw):
            return "procedural_code_outside_always"
        if "syntax error" in lower_log:
            return "syntax_error"
        return "compile_error_other"

    if category == "simulation_failure":
        task_id = row["task_id"].lower()
        lower_log = log.lower()
        mismatch_rate = (mismatches / sim_samples) if mismatches is not None and sim_samples else None
        is_sequential = bool(
            re.search(r"\b(clk|clock|reset|areset|resetn)\b", raw, re.IGNORECASE)
            or re.search(r"always\s*@\s*\(\s*posedge", raw, re.IGNORECASE)
            or re.search(r"\balways_ff\b", raw, re.IGNORECASE)
        )
        if "timeout" in lower_log:
            return "timeout_or_nonterminating_behavior"
        if "reset doesn't seem to be working" in lower_log:
            return "reset_behavior_error"
        if any(token in task_id for token in ("fsm", "lemmings", "ps2", "serial", "hdlc")):
            return "fsm_or_protocol_logic_error"
        if is_sequential or any(token in task_id for token in ("dff", "edge", "shift", "lfsr", "count", "timer", "clock")):
            if mismatch_rate is not None and mismatch_rate < 0.03:
                return "initial_reset_or_one_cycle_timing_error"
            return "sequential_timing_or_state_error"
        if any(token in task_id for token in ("mux", "kmap", "gate", "circuit", "q4", "q5", "q6")):
            return "combinational_logic_error"
        return "functional_logic_error"

    return category


if __name__ == "__main__":
    main()
