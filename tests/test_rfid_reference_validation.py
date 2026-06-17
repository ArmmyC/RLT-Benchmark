from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_rfid_apbench_references.py"
SPEC = importlib.util.spec_from_file_location("validate_rfid_apbench_references", SCRIPT_PATH)
assert SPEC is not None
validation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validation
SPEC.loader.exec_module(validation)


def row(**overrides):
    values = {
        "task_id": "ap_001_idle_counter",
        "compile_status": "pass",
        "simulation_status": "pass",
        "activity_status": "pass",
        "synthesis_status": "pass",
        "area_status": "pass",
        "timing_status": "not_required",
        "reference_area": 12.0,
        "area_unit": "generic_cells",
        "reference_activity": 34,
        "activity_metric": "total_signal_toggles",
        "failure_category": "passed",
        "notes": "reference validated",
    }
    values.update(overrides)
    return validation.ReferenceValidationRow(**values)


def test_report_row_sanitized_dict_has_required_fields() -> None:
    data = row().sanitized_dict()

    assert list(data) == validation.REPORT_FIELDS
    assert data["task_id"] == "ap_001_idle_counter"
    assert data["reference_area"] == "12.0"
    assert data["reference_activity"] == "34"


def test_report_row_rejects_raw_payload() -> None:
    with pytest.raises(ValueError, match="forbidden report payload"):
        row(notes="raw_response payload marker").sanitized_dict()


def test_yosys_cell_count_parser_uses_last_stat_block() -> None:
    stdout = """
Number of cells: 2
  $and 1
Number of cells: 17
  $_AND_ 3
"""

    assert validation.parse_yosys_generic_cell_count(stdout) == 17


def test_yosys_cell_count_parser_accepts_stat_cell_summary() -> None:
    stdout = """
=== ap_001_idle_counter ===

       19 wires
       54 wire bits
       15 cells
        1   $add
"""

    assert validation.parse_yosys_generic_cell_count(stdout) == 15


def test_unavailable_tools_produce_graceful_rows(tmp_path: Path) -> None:
    benchmark_root = Path(__file__).resolve().parents[1] / "benchmarks" / "rfid_apbench"
    tools = validation.ToolAvailability(iverilog=None, vvp=None, yosys=None)

    rows = validation.validate_references(benchmark_root, tmp_path, tools)

    assert len(rows) == 5
    assert all(item.compile_status == "unavailable" for item in rows)
    assert all(item.simulation_status == "unavailable" for item in rows)
    assert all(item.activity_status == "unavailable" for item in rows)
    assert all(item.synthesis_status == "unavailable" for item in rows)
    assert all(item.area_status == "unavailable" for item in rows)
    assert all(item.failure_category == "tool_unavailable" for item in rows)


def test_markdown_and_csv_reports_are_sanitized(tmp_path: Path) -> None:
    rows = [row(), row(task_id="ap_002_command_decoder", failure_category="area_unavailable", reference_area=None, area_unit=None)]
    tools = validation.ToolAvailability(iverilog=None, vvp=None, yosys=None)
    output_md = tmp_path / "report.md"
    output_csv = tmp_path / "report.csv"

    validation.write_markdown_report(rows, output_md, tools)
    validation.write_csv_report(rows, output_csv)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    assert "VCD toggle-count proxy" in markdown
    assert "reference-only validation" in markdown
    assert "ap_001_idle_counter" in csv_text
    assert "$dumpvars" not in markdown
    assert "raw_response" not in csv_text
