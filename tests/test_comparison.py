from pathlib import Path

from rtlbench.comparison import build_comparison, render_csv, render_markdown
from rtlbench.registry import load_registry
from test_registry import run_record, write_registry


def test_comparison_separates_evaluation_kinds_and_renders_csv(tmp_path: Path) -> None:
    runs = [
        run_record(id="ve", benchmark="verilogeval", mode="pass1", manual_summary={"functional_pass_rate": 0.5, "syntax_pass_rate": 0.75}),
        run_record(id="rt", benchmark="rtllm2", mode="pass1", manual_summary={"functional_pass_rate": 0.4, "syntax_pass_rate": 0.6}),
        run_record(id="proto", benchmark="protocollm", mode="lint", evaluation_kind="lint_only", evaluator_type="verilator_lint", max_tokens=4096, manual_summary={"syntax_pass_rate": 0.8}),
        run_record(id="synth", benchmark="rtlopt", mode="synthesis", evaluation_kind="synthesis_only", evaluator_type="yosys_generic", max_tokens=4096, manual_summary={"functional_pass_rate": 0.9}),
        run_record(id="equiv", benchmark="rtlopt", mode="equivalence", evaluation_kind="equivalence", evaluator_type="yosys_equivalence", max_tokens=4096, manual_summary={"functional_pass_rate": 0.7}, rtlopt_metrics={"equivalence_pass_rate": 0.7}),
    ]
    baseline = load_registry(write_registry(tmp_path, runs, benchmarks=["verilogeval", "rtllm2", "protocollm", "rtlopt"]), "baseline_v0_1")
    data = build_comparison(baseline)
    assert data["tables"]["functional_rtl_generation"][0]["values"]["model-a"] == 0.5
    assert data["tables"]["protocollm_lint_only"][0]["values"]["model-a"] == 0.8
    assert data["tables"]["rtlopt_synthesis_only"][0]["values"]["model-a"] == 0.9
    assert data["tables"]["rtlopt_behavior_preserving_optimization"][0]["values"]["model-a"] == 0.7
    csv_text = render_csv(data)
    assert "baseline,benchmark,mode,evaluation_kind,metric,model,value,source" in csv_text
    assert "manual_summary" in csv_text
    markdown = render_markdown(data)
    assert "0.5000" in markdown
    assert "N/A" in markdown
    assert "lint-only" in markdown.lower()
