import pytest

from rtlbench.evaluator import FAIL_RE, MISMATCH_RE, _rename_first_module, parse_yosys_stat


def test_recognizes_nonzero_mismatches() -> None:
    assert [int(value) for value in MISMATCH_RE.findall("Mismatches: 3 in 100 samples")] == [3]


def test_does_not_treat_zero_mismatches_as_failure() -> None:
    output = "Mismatches: 0 in 100 samples"
    assert all(int(value) == 0 for value in MISMATCH_RE.findall(output))
    assert FAIL_RE.search(output) is None


def test_parse_yosys_stat_metrics() -> None:
    text = """
   Number of wires:                501
   Number of wire bits:            842
   Number of cells:                323
   Chip area for module '\\adder': 456.190000
"""
    assert parse_yosys_stat(text) == {
        "wires": 501,
        "wire_bits": 842,
        "cells": 323,
        "area": 456.19,
    }


def test_rename_first_module() -> None:
    assert _rename_first_module("module old; endmodule", "gold") == "module gold; endmodule"


def test_rename_first_module_requires_module() -> None:
    with pytest.raises(ValueError):
        _rename_first_module("assign x = y;", "gold")
