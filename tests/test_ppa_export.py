from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest

from rtlbench.ppa_export import export_ppa_records, render_ppa_jsonl, result_row_to_ppa_record
from rtlbench.ppa_reporting import load_sanitized_jsonl, summarize_records


def _load_script_main(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace(".", "_"), path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


REPO_ROOT = Path(__file__).resolve().parents[1]
export_main = _load_script_main(REPO_ROOT / "scripts" / "export_v0.4_ppa_results.py")
summarize_main = _load_script_main(REPO_ROOT / "scripts" / "summarize_v0.4_ppa_results.py")


def rtlopt_row(**overrides):
    row = {
        "benchmark": "rtlopt",
        "task_id": "adder",
        "sample_id": 0,
        "model": "qwen36-27b",
        "compile_pass": True,
        "final_pass": True,
        "failure_category": "passed",
        "raw_response_path": "raw_responses/private.txt",
        "extracted_rtl_path": "extracted_rtl/private.sv",
        "error_log_path": "error_logs/private.log",
        "evaluation_metrics": {
            "reference_area": 100.0,
            "generated_area": 80.0,
            "equivalence_proven": 1,
        },
    }
    row.update(overrides)
    return row


def test_valid_mapped_area_row_exports_area_only_score() -> None:
    record = result_row_to_ppa_record(rtlopt_row(), prompt_profile="neutral_baseline")

    assert record.benchmark == "rtlopt"
    assert record.task_id == "adder#sample-0"
    assert record.scoring_mode == "area_only"
    assert record.power_status == "power_unavailable"
    assert record.score_status == "valid"
    assert record.area_unit == "mapped_area"
    assert record.optimization_score == pytest.approx(1.25)


def test_mapped_reference_area_has_highest_priority_over_generic_cells() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "reference_area": 100.0,
            "baseline_area": 120.0,
            "generated_area": 80.0,
            "generic_baseline_cells": 50,
            "generated_cells": 25,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.area_unit == "mapped_area"
    assert record.toolchain_id == "yosys-mapped-area"
    assert record.reference_area == 100.0
    assert record.generated_area == 80.0
    assert record.optimization_score == pytest.approx(1.25)


def test_mapped_baseline_area_has_second_priority_over_generic_cells() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "baseline_area": 120.0,
            "generated_area": 80.0,
            "generic_baseline_cells": 50,
            "generated_cells": 25,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.area_unit == "mapped_area"
    assert record.toolchain_id == "yosys-mapped-area"
    assert record.reference_area == 120.0
    assert record.generated_area == 80.0
    assert record.optimization_score == pytest.approx(1.5)


def test_valid_generic_cell_row_exports_generic_proxy() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "generated_cells": 40,
            "generic_baseline_cells": 50,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.area_unit == "generic_cells"
    assert record.toolchain_id == "yosys-generic-cell-count-proxy"
    assert record.optimization_score == pytest.approx(1.25)


def test_incomplete_reference_mapped_area_falls_through_to_generic_cells() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "reference_area": 100.0,
            "generated_cells": 40,
            "generic_baseline_cells": 50,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.area_unit == "generic_cells"
    assert record.toolchain_id == "yosys-generic-cell-count-proxy"
    assert record.reference_area == 50
    assert record.generated_area == 40
    assert record.optimization_score == pytest.approx(1.25)


def test_incomplete_baseline_mapped_area_falls_through_to_generic_cells() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "baseline_area": 120.0,
            "generated_cells": 40,
            "generic_baseline_cells": 50,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.area_unit == "generic_cells"
    assert record.toolchain_id == "yosys-generic-cell-count-proxy"
    assert record.reference_area == 50
    assert record.generated_area == 40
    assert record.optimization_score == pytest.approx(1.25)


def test_baseline_area_is_used_when_reference_area_is_absent() -> None:
    row = rtlopt_row(evaluation_metrics={"baseline_area": 120.0, "generated_area": 80.0})

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "valid"
    assert record.reference_area == 120.0
    assert record.generated_area == 80.0
    assert record.optimization_score == pytest.approx(1.5)


def test_compile_failure_becomes_invalid() -> None:
    row = rtlopt_row(compile_pass=False, final_pass=False, failure_category="compile_failure")

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "invalid"
    assert record.compile_pass is False
    assert record.synth_pass is False
    assert record.failure_category == "compile_failure"
    assert record.optimization_score is None


def test_equivalence_failure_becomes_invalid() -> None:
    row = rtlopt_row(
        final_pass=False,
        failure_category="equiv_failure",
        evaluation_metrics={"reference_area": 100.0, "generated_area": 80.0, "equivalence_proven": 0},
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "invalid"
    assert record.equiv_pass is False
    assert record.failure_category == "equiv_failure"


def test_missing_metric_becomes_invalid() -> None:
    row = rtlopt_row(evaluation_metrics={"generated_area": 80.0, "equivalence_proven": 1})

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "invalid"
    assert record.synth_pass is True
    assert record.failure_category == "invalid_area_metric"


def test_missing_generated_metrics_remain_invalid() -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "reference_area": 100.0,
            "generic_baseline_cells": 50,
            "equivalence_proven": 1,
        }
    )

    record = result_row_to_ppa_record(row, prompt_profile="neutral_baseline")

    assert record.score_status == "invalid"
    assert record.synth_pass is False
    assert record.failure_category == "synthesis_failure"
    assert record.optimization_score is None


def test_unsupported_benchmark_is_rejected() -> None:
    row = rtlopt_row(benchmark="verilogeval")

    with pytest.raises(ValueError, match="unsupported benchmark"):
        result_row_to_ppa_record(row, prompt_profile="neutral_baseline")


def test_raw_private_path_fields_are_not_copied() -> None:
    record = result_row_to_ppa_record(rtlopt_row(), prompt_profile="neutral_baseline")
    exported = record.sanitized_dict()

    assert "raw_response_path" not in exported
    assert "extracted_rtl_path" not in exported
    assert "error_log_path" not in exported
    assert set(exported) == {
        "schema_version",
        "benchmark",
        "task_id",
        "model",
        "prompt_profile",
        "source_run_id",
        "toolchain_id",
        "final_pass",
        "extraction_pass",
        "compile_pass",
        "synth_pass",
        "equiv_pass",
        "timing_status",
        "timing_pass",
        "timing_constraint",
        "timing_slack",
        "reference_area",
        "generated_area",
        "area_unit",
        "reference_power",
        "generated_power",
        "power_unit",
        "power_status",
        "area_score",
        "power_score",
        "optimization_score",
        "scoring_mode",
        "score_status",
        "failure_category",
    }


def test_export_script_reads_synthetic_results_and_writes_sanitized_jsonl(tmp_path) -> None:
    input_path = tmp_path / "results.jsonl"
    output_path = tmp_path / "ppa.jsonl"
    input_path.write_text(json.dumps(rtlopt_row()) + "\n", encoding="utf-8")

    status = export_main(
        [
            str(input_path),
            str(output_path),
            "--prompt-profile",
            "neutral_baseline",
            "--source-run-id",
            "synthetic-run",
        ]
    )

    assert status == 0
    records = load_sanitized_jsonl(output_path)
    assert len(records) == 1
    assert records[0].source_run_id == "synthetic-run"
    assert records[0].prompt_profile == "neutral_baseline"


def test_exported_jsonl_can_be_summarized_by_v0_4_script(tmp_path) -> None:
    records = export_ppa_records(
        [rtlopt_row(), rtlopt_row(task_id="subtractor", evaluation_metrics={"generated_cells": 40, "generic_baseline_cells": 50})],
        prompt_profile="neutral_baseline",
        source_run_id="synthetic-run",
    )
    ppa_path = tmp_path / "ppa.jsonl"
    md_path = tmp_path / "summary.md"
    csv_path = tmp_path / "summary.csv"
    ppa_path.write_text(render_ppa_jsonl(records), encoding="utf-8")

    loaded = load_sanitized_jsonl(ppa_path)
    summaries = summarize_records(loaded)
    status = summarize_main([str(ppa_path), "--output-md", str(md_path), "--output-csv", str(csv_path)])

    assert len(summaries) == 1
    assert summaries[0].samples == 2
    assert status == 0
    assert "v0.4 Sanitized PPA Summary" in md_path.read_text(encoding="utf-8")
    assert "neutral_baseline" in csv_path.read_text(encoding="utf-8")


def test_stage_h_like_generic_cells_row_summarizes_as_valid_area_only(tmp_path) -> None:
    row = rtlopt_row(
        evaluation_metrics={
            "reference_area": 202.692,
            "baseline_area": 257.0,
            "generated_cells": 230,
            "generic_baseline_cells": 230,
            "generic_reference_cells": 267,
            "equivalence_proven": 1,
        }
    )
    records = export_ppa_records([row], prompt_profile="neutral_baseline", source_run_id="stage-h-like")
    ppa_path = tmp_path / "ppa.jsonl"
    ppa_path.write_text(render_ppa_jsonl(records), encoding="utf-8")

    loaded = load_sanitized_jsonl(ppa_path)
    summaries = summarize_records(loaded)

    assert loaded[0].score_status == "valid"
    assert loaded[0].area_unit == "generic_cells"
    assert loaded[0].toolchain_id == "yosys-generic-cell-count-proxy"
    assert summaries[0].valid_scores == 1
    assert summaries[0].mean_valid_score == pytest.approx(1.0)
