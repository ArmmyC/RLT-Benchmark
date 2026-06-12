from pathlib import Path

from rtlbench.adapters.rtlopt import RTLOPTAdapter


def test_rtlopt_loads_design_pairs(tmp_path: Path):
    root = tmp_path / "RTL-OPT"
    design = root / "benchmark" / "adder"
    ref = root / "benchmark" / "adder_ref"
    design.mkdir(parents=True)
    ref.mkdir()
    design.joinpath("adder.v").write_text(
        "module adder(input a, input b, output y); assign y = a ^ b; endmodule\n",
        encoding="utf-8",
    )
    ref.joinpath("adder_ref.v").write_text(
        "module adder_ref(input a, input b, output y); assign y = a ^ b; endmodule\n",
        encoding="utf-8",
    )

    tasks = list(RTLOPTAdapter(root).load_tasks())

    assert len(tasks) == 1
    assert tasks[0].task_id == "adder"
    assert tasks[0].module_name == "adder"
    assert tasks[0].metadata["has_reference"] is True


def test_rtlopt_prompt_preserves_interface_instruction(tmp_path: Path):
    root = tmp_path / "benchmark"
    design = root / "mux"
    design.mkdir(parents=True)
    design.joinpath("mux.sv").write_text(
        "module mux(input sel, input a, input b, output y); assign y = sel ? a : b; endmodule\n",
        encoding="utf-8",
    )
    adapter = RTLOPTAdapter(root)
    task = next(adapter.load_tasks())

    prompt = adapter.build_prompt(task)

    assert "Optimize the following RTL" in prompt
    assert "Keep the module name and ports unchanged" in prompt
    assert "module mux" in prompt
