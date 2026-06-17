from __future__ import annotations

from pathlib import Path

import pytest

from rtlbench.vcd_activity import VCDActivityError, count_vcd_file, count_vcd_toggles


TINY_VCD = """
$date
  public synthetic fixture
$end
$version
  rtlbench test
$end
$timescale 1ns $end
$scope module testbench $end
$var wire 1 ! clk $end
$var wire 1 " active $end
$var wire 4 # count $end
$upscope $end
$enddefinitions $end
#0
0!
0"
b0000 #
#5
1!
#10
0!
1"
b0001 #
#15
1!
b0010 #
#20
0!
0"
b0010 #
"""


def test_vcd_toggle_count_basic_case() -> None:
    result = count_vcd_toggles(TINY_VCD)

    assert result.total_toggles == 8
    assert result.signal_toggles["clk"] == 4
    assert result.signal_toggles["active"] == 2
    assert result.signal_toggles["count"] == 2


def test_vcd_signal_exclusion() -> None:
    result = count_vcd_toggles(TINY_VCD, exclude_signals={"clk"})

    assert result.total_toggles == 4
    assert "clk" not in result.signal_toggles
    assert result.excluded_signals == ("clk",)


def test_vcd_alias_identifiers_are_counted_once() -> None:
    vcd = """
$timescale 1ns $end
$scope module top $end
$var wire 1 ! ready $end
$scope module child $end
$var wire 1 ! ready $end
$upscope $end
$upscope $end
$enddefinitions $end
#0
0!
#1
1!
#2
0!
"""

    result = count_vcd_toggles(vcd)

    assert result.total_toggles == 2
    assert result.signal_toggles == {"ready": 2}


def test_vcd_time_window_counts_only_inside_window() -> None:
    result = count_vcd_toggles(TINY_VCD, exclude_signals={"clk"}, start_time=11, end_time=20)

    assert result.total_toggles == 2
    assert result.signal_toggles["active"] == 1
    assert result.signal_toggles["count"] == 1


def test_count_vcd_file(tmp_path: Path) -> None:
    path = tmp_path / "tiny.vcd"
    path.write_text(TINY_VCD, encoding="utf-8")

    result = count_vcd_file(path, exclude_signals={"clk"})

    assert result.total_toggles == 4


@pytest.mark.parametrize(
    ("vcd_text", "message"),
    [
        ("", "empty"),
        ("#0\n0!\n", "no signal definitions"),
        ("$var wire 1 ! clk $end\n0!\n", "no timestamps"),
        ("$var wire 1 ! clk $end\n#0\n0x\n", "unknown VCD identifier"),
        ("$var wire nope ! clk $end\n#0\n0!\n", "invalid VCD signal width"),
        ("$var wire 1 ! clk $end\n#0\nr1.0 !\n", "unsupported VCD value change"),
    ],
)
def test_malformed_vcd_errors(vcd_text: str, message: str) -> None:
    with pytest.raises(VCDActivityError, match=message):
        count_vcd_toggles(vcd_text)


def test_missing_vcd_file_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        count_vcd_file(tmp_path / "missing.vcd")
