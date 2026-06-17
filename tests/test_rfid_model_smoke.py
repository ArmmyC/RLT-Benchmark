from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_rfid_apbench_model_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_rfid_apbench_model_smoke", SCRIPT_PATH)
assert SPEC is not None
model_smoke = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = model_smoke
SPEC.loader.exec_module(model_smoke)

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"


def tasks():
    return list(RFIDAPBenchAdapter(BENCHMARK_ROOT).load_task_infos())


def test_endpoint_config_defaults_to_no_secret_payload() -> None:
    config = model_smoke.load_endpoint_config({"QWEN_BASE_URL": "https://user:pass@example.test/v1?x=1"})

    assert config.available is False
    assert config.model == "qwen36-27b"
    assert config.sanitized_endpoint == "https://example.test/v1"
    assert config.missing_labels == ("credential",)


def test_candidate_id_is_filesystem_safe() -> None:
    assert model_smoke.make_candidate_id("qwen/36 27b:a3b") == "qwen_36_27b_a3b"


def test_no_endpoint_rows_are_sanitized() -> None:
    config = model_smoke.EndpointConfig(
        base_url=None,
        credential=None,
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = model_smoke.make_no_endpoint_rows(tasks(), config, "neutral_baseline")

    assert len(rows) == 5
    assert {row.failure_category for row in rows} == {"endpoint_unavailable"}
    assert all(row.score_status == "invalid" for row in rows)
    for row in rows:
        row.sanitized_dict()


def test_report_writers_emit_sanitized_blocker(tmp_path: Path) -> None:
    config = model_smoke.EndpointConfig(
        base_url=None,
        credential=None,
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = model_smoke.make_no_endpoint_rows(tasks(), config, "neutral_baseline")
    output_md = tmp_path / "smoke.md"
    output_csv = tmp_path / "smoke.csv"
    output_jsonl = tmp_path / "smoke.jsonl"

    model_smoke.write_markdown_report(
        rows,
        output_md,
        endpoint=config,
        tools=model_smoke.ToolAvailability(iverilog=None, vvp=None, yosys=None),
        run_id="test_run",
    )
    model_smoke.write_csv_report(rows, output_csv)
    model_smoke.write_jsonl_report(rows, output_jsonl)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    json_rows = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert "endpoint_unavailable" in markdown
    assert "raw_model_response" not in markdown
    assert "generated RTL" in markdown
    assert "endpoint_unavailable" in csv_text
    assert json_rows[0]["benchmark"] == "rfid_apbench"


def test_missing_evaluation_row_sanitizes_generation_notes() -> None:
    config = model_smoke.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    task = tasks()[0]
    generation = model_smoke.GenerationRecord(
        task_id=task.task_id,
        generation_status="request_failed",
        extraction_status="not_run",
        candidate_file_available=False,
        latency_seconds=None,
        notes="raw_response saved under outputs/run; module candidate failed",
    )

    row = model_smoke._missing_evaluation_row(task, config, "neutral_baseline", generation)

    sanitized = row.sanitized_dict()
    assert "raw_response" not in sanitized["notes"]
    assert "outputs/" not in sanitized["notes"]
