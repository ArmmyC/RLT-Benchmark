from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

from scripts.v0_3_prompt_smoke_lib import (
    BENCHMARKS,
    PROFILES,
    build_smoke_commands,
    parse_selection,
)

SUMMARY_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_v0.3_prompt_smoke.py"
_summary_spec = importlib.util.spec_from_file_location("summarize_v0_3_prompt_smoke", SUMMARY_SCRIPT)
assert _summary_spec and _summary_spec.loader
summary_module = importlib.util.module_from_spec(_summary_spec)
sys.modules[_summary_spec.name] = summary_module
_summary_spec.loader.exec_module(summary_module)
collect_smoke_summaries = summary_module.collect_smoke_summaries
render_csv = summary_module.render_csv
render_markdown = summary_module.render_markdown


def test_dry_run_generates_every_benchmark_profile_command() -> None:
    commands = build_smoke_commands(base_url="http://127.0.0.1:8000/v1", python="python")

    assert len(commands) == len(BENCHMARKS) * len(PROFILES)
    assert all("--model-preset qwen36-27b" in command.display() for command in commands)
    assert all("--execute" not in command.argv for command in commands)


def test_filters_profiles_and_benchmarks() -> None:
    benchmarks = parse_selection("verilogeval", BENCHMARKS, "benchmark")
    profiles = parse_selection("strict_rtl_only,no_explanation_code_only", PROFILES, "prompt profile")

    commands = build_smoke_commands(
        base_url="http://example/v1",
        benchmarks=benchmarks,
        profiles=profiles,
        workers=2,
        limit=2,
        python="python",
    )

    assert [(command.benchmark, command.profile) for command in commands] == [
        ("verilogeval", "strict_rtl_only"),
        ("verilogeval", "no_explanation_code_only"),
    ]
    assert all(command.argv[command.argv.index("--workers") + 1] == "2" for command in commands)
    assert all(command.argv[command.argv.index("--limit") + 1] == "2" for command in commands)


def test_output_directory_naming() -> None:
    command = build_smoke_commands(
        base_url="http://example/v1",
        benchmarks=("rtlopt",),
        profiles=("low_area_low_power",),
        python="python",
    )[0]

    assert command.output_dir.as_posix() == "outputs/experiments/v0.3_prompt_profiles/rtlopt/low_area_low_power"
    assert command.argv[command.argv.index("--output-dir") + 1] == str(command.output_dir)


def test_summary_parser_reads_only_metadata_and_summary(tmp_path: Path, monkeypatch) -> None:
    run_dir = _write_finished_run(tmp_path, "verilogeval", "strict_rtl_only")
    (run_dir / "raw_responses").mkdir()
    (run_dir / "raw_responses" / "do-not-read.txt").write_text("private model response", encoding="utf-8")
    original_read_text = Path.read_text
    read_names: list[str] = []

    def guarded_read_text(path: Path, *args, **kwargs):
        read_names.append(path.name)
        assert path.name in {"summary.json", "run_metadata.json"}
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read_text)
    rows = collect_smoke_summaries(tmp_path, ("verilogeval",), ("strict_rtl_only",))

    assert read_names == ["run_metadata.json", "summary.json"]
    assert rows[0].status == "finished"
    assert rows[0].samples == 3
    assert rows[0].pass_count == 2
    assert rows[0].syntax_pass_count == 3
    assert rows[0].functional_pass_count == 2
    assert rows[0].failure_categories == {"passed": 2, "simulation_failure": 1}
    assert rows[0].output_path == str(run_dir)


def test_missing_run_is_reported_without_fabrication(tmp_path: Path) -> None:
    rows = collect_smoke_summaries(tmp_path, ("rtllm2",), ("neutral_baseline",))

    assert rows[0].status == "missing"
    assert rows[0].samples is None
    assert rows[0].failure_categories == {}
    assert "missing" in render_markdown(rows)
    assert "rtllm2,neutral_baseline,missing" in render_csv(rows)


def _write_finished_run(root: Path, benchmark: str, profile: str) -> Path:
    run_dir = root / benchmark / profile / benchmark / "qwen36-27b" / "20260615T000000Z"
    run_dir.mkdir(parents=True)
    (run_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "status": "finished",
                "finished_utc": "2026-06-15T00:01:00+00:00",
                "config": {
                    "benchmark_name": benchmark,
                    "model": "qwen36-27b",
                    "prompt_profile": profile,
                },
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "samples": 3,
                "tasks": 3,
                "syntax_pass_rate": 1.0,
                "functional_pass_rate": 2 / 3,
                "failure_categories": {"passed": 2, "simulation_failure": 1},
            }
        ),
        encoding="utf-8",
    )
    return run_dir
