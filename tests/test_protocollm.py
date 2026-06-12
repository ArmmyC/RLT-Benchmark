from rtlbench.adapters.protocollm import ProtocolLLMAdapter


def test_loads_protocollm_prompts(tmp_path) -> None:
    config_dir = tmp_path / "src" / "configs"
    config_dir.mkdir(parents=True)
    (config_dir / "base.yaml").write_text(
        """
spi:
  easy1: |
    Generate SPI.
    module SPI_driver(input logic clk, output logic done);
i2c:
  hard1: |
    Generate I2C.
    module I2C_driver(input logic clk, output logic done);
""",
        encoding="utf-8",
    )

    tasks = list(ProtocolLLMAdapter(tmp_path).load_tasks())
    assert [task.task_id for task in tasks] == ["spi__easy1", "i2c__hard1"]
    assert tasks[0].module_name == "SPI_driver"
    assert tasks[0].testbench == ""
    assert ProtocolLLMAdapter(tmp_path).evaluator_name == "verilator_lint"
