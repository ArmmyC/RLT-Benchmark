from rtlbench.adapters.rtllm2 import RTLLM2Adapter


def test_loads_rtllm2_task_and_support_data(tmp_path) -> None:
    task_dir = tmp_path / "Memory" / "FIFO" / "toy_fifo"
    task_dir.mkdir(parents=True)
    (task_dir / "design_description.txt").write_text(
        "Module name:\n    toy_fifo\n\nInput ports:\n clk: clock\n", encoding="utf-8"
    )
    (task_dir / "testbench.v").write_text("module tb; toy_fifo dut(); endmodule", encoding="utf-8")
    (task_dir / "verified_toy_fifo.v").write_text("module toy_fifo; endmodule", encoding="utf-8")
    (task_dir / "vectors.txt").write_text("deadbeef\n", encoding="utf-8")

    task = list(RTLLM2Adapter(tmp_path).load_tasks())[0]
    assert task.task_id == "Memory__FIFO__toy_fifo"
    assert task.module_name == "toy_fifo"
    assert task.support_files["vectors.txt"] == "deadbeef\n"
    assert task.compile_support_files == []
    assert "Do not change" in RTLLM2Adapter(tmp_path).build_prompt(task)
