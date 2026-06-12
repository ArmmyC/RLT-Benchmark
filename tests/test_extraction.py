from rtlbench.extraction import extract_all_rtl_modules, extract_rtl


def test_extracts_tagged_fence() -> None:
    response = "Explanation\n```systemverilog\nmodule top(input logic a, output logic y); assign y=a; endmodule\n```"
    assert extract_rtl(response) == "module top(input logic a, output logic y); assign y=a; endmodule\n"


def test_extracts_unfenced_module() -> None:
    response = "Here is the answer:\nmodule top; // keep this comment\nendmodule\nDone."
    assert extract_rtl(response) == "module top; // keep this comment\nendmodule\n"


def test_returns_none_without_complete_module() -> None:
    assert extract_rtl("assign y = a;") is None


def test_extracts_all_modules_when_required_top_exists() -> None:
    response = """
```verilog
module helper(input a, output y); assign y = a; endmodule
module top(input a, output y); helper h(a, y); endmodule
```
"""
    assert extract_all_rtl_modules(response, "top").count("endmodule") == 2


def test_extract_all_modules_requires_top_when_requested() -> None:
    response = "module helper; endmodule"
    assert extract_all_rtl_modules(response, "top") is None
