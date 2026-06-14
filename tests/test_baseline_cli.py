import json
import os
import subprocess
import sys
from pathlib import Path

from test_registry import run_record, write_registry


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cli(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script), *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_baseline_cli_pipeline(tmp_path: Path) -> None:
    results = tmp_path / "results.jsonl"
    results.write_text(json.dumps({"task_id": "task-a", "sample_id": 0, "final_pass": True, "compile_pass": True, "sim_pass": True, "failure_category": "passed"}) + "\n", encoding="utf-8")
    runs = [
        run_record(id="ve1", benchmark="verilogeval", mode="pass1", results_path=str(results), manual_summary={"functional_pass_rate": 0.5, "syntax_pass_rate": 0.8}),
        run_record(id="ve5", benchmark="verilogeval", mode="pass5", samples_per_task=5, temperature=0.6, results_path=str(results), manual_summary={"functional_pass_rate": 0.6, "syntax_pass_rate": 0.8, "pass_at_k": {"pass@5": 0.7}}),
        run_record(id="rt", benchmark="rtllm2", mode="pass1", max_tokens=4096, results_path=str(results), manual_summary={"functional_pass_rate": 0.4, "syntax_pass_rate": 0.6}),
        run_record(id="proto", benchmark="protocollm", mode="lint", evaluation_kind="lint_only", evaluator_type="verilator_lint", max_tokens=4096, results_path=str(results), manual_summary={"syntax_pass_rate": 0.8}),
        run_record(id="equiv", benchmark="rtlopt", mode="equivalence", evaluation_kind="equivalence", evaluator_type="yosys_equivalence", max_tokens=4096, results_path=str(results), manual_summary={"functional_pass_rate": 0.6}, rtlopt_metrics={"equivalence_pass_rate": 0.6}),
    ]
    registry = write_registry(tmp_path, runs, benchmarks=["verilogeval", "rtllm2", "protocollm", "rtlopt"])
    md, js, csv = tmp_path / "comparison.md", tmp_path / "comparison.json", tmp_path / "comparison.csv"
    failure_md, failure_csv = tmp_path / "failure.md", tmp_path / "failure.csv"
    dashboard = tmp_path / "dashboard" / "index.html"

    result = run_cli("generate_comparison_report.py", "--registry", str(registry), "--baseline", "baseline_v0_1", "--output-md", str(md), "--output-json", str(js), "--output-csv", str(csv))
    assert result.returncode == 0, result.stderr
    result = run_cli("analyze_cross_model_failures.py", "--registry", str(registry), "--baseline", "baseline_v0_1", "--output-md", str(failure_md), "--output-csv", str(failure_csv))
    assert result.returncode == 0, result.stderr
    result = run_cli("build_dashboard.py", "--registry", str(registry), "--baseline", "baseline_v0_1", "--comparison-json", str(js), "--failure-csv", str(failure_csv), "--output", str(dashboard))
    assert result.returncode == 0, result.stderr

    for path in (md, js, csv, failure_md, failure_csv, dashboard, dashboard.parent / "data" / "baseline_v0.1.json", dashboard.parent / "data" / "failure_matrix.csv"):
        assert path.is_file()
    assert "model-a" in dashboard.read_text(encoding="utf-8")
