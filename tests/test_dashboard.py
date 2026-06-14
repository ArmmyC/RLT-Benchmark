from pathlib import Path

from rtlbench.comparison import build_comparison
from rtlbench.dashboard import render_dashboard
from rtlbench.failure_matrix import build_failure_matrix
from rtlbench.registry import load_registry
from test_registry import run_record, write_registry


def test_dashboard_html_contains_required_sections_and_no_secrets(tmp_path: Path) -> None:
    runs = [
        run_record(id="ve", benchmark="verilogeval", mode="pass1", manual_summary={"functional_pass_rate": 0.5}),
        run_record(id="ve5", benchmark="verilogeval", mode="pass5", samples_per_task=5, temperature=0.6, manual_summary={"pass_at_k": {"pass@5": 0.7}}),
        run_record(id="rt", benchmark="rtllm2", mode="pass1", max_tokens=4096, manual_summary={"functional_pass_rate": 0.4}),
        run_record(id="equiv", benchmark="rtlopt", mode="equivalence", evaluation_kind="equivalence", max_tokens=4096, evaluator_type="yosys_equivalence", manual_summary={"functional_pass_rate": 0.6}, rtlopt_metrics={"equivalence_pass_rate": 0.6}),
    ]
    baseline = load_registry(write_registry(tmp_path, runs, benchmarks=["verilogeval", "rtllm2", "rtlopt"]), "baseline_v0_1")
    output = render_dashboard(build_comparison(baseline), build_failure_matrix(baseline))
    assert "RTLBench Baseline v0.1" in output
    assert "model-a" in output
    assert "Functional RTL Generation" in output
    assert "RTL-OPT Behavior-Preserving Optimization" in output
    assert "Per-task failure data is not available" in output
    assert "api_key" not in output.lower()
