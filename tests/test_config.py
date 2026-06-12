from pathlib import Path

from rtlbench.config import load_config


def test_loads_model_preset(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    models = tmp_path / "models.yaml"
    config.write_text(
        """
benchmark:
  name: verilogeval
  root: tasks.jsonl
model:
  preset: test-model
generation: {}
evaluation: {}
run: {}
""",
        encoding="utf-8",
    )
    models.write_text(
        """
models:
  test-model:
    name: served-test
    base_url: http://example/v1
    api_key: EMPTY
""",
        encoding="utf-8",
    )

    loaded = load_config(config)

    assert loaded.model_preset == "test-model"
    assert loaded.model == "served-test"
    assert loaded.base_url == "http://example/v1"
