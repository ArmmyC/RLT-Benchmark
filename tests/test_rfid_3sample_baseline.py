from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_rfid_apbench_3sample_baseline.py"
SPEC = importlib.util.spec_from_file_location("run_rfid_apbench_3sample_baseline", SCRIPT_PATH)
assert SPEC is not None
baseline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = baseline
SPEC.loader.exec_module(baseline)

from rtlbench.adapters.rfid_apbench import RFIDAPBenchAdapter  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPO_ROOT / "benchmarks" / "rfid_apbench"


def tasks():
    return list(RFIDAPBenchAdapter(BENCHMARK_ROOT).load_task_infos())


def row(**overrides):
    values = {
        "benchmark": "rfid_apbench",
        "task_id": "ap_001_idle_counter",
        "sample_id": 1,
        "model": "qwen36-27b",
        "prompt_profile": "neutral_baseline",
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 4096,
        "endpoint_status": "available",
        "generation_status": "completed",
        "extraction_status": "failed",
        "candidate_file_available": False,
        "compile_pass": False,
        "correctness_pass": False,
        "synth_pass": False,
        "timing_status": "not_required",
        "area_metric_available": False,
        "activity_metric_available": False,
        "reference_area": 15.0,
        "generated_area": None,
        "area_unit": "generic_cells",
        "reference_activity": 34.0,
        "generated_activity": None,
        "activity_metric": "total_signal_toggles",
        "area_score": None,
        "activity_score": None,
        "score": None,
        "score_status": "invalid",
        "failure_category": "extraction_failure",
        "toolchain_id": "iverilog-vcd-yosys-generic",
        "workload_id": "ap_001_idle_counter_default",
        "notes": "no complete required top rtl_unit extracted",
    }
    values.update(overrides)
    return baseline.BaselineRow(**values)


def test_runner_loads_current_ten_task_benchmark() -> None:
    loaded = baseline.load_tasks(BENCHMARK_ROOT)

    assert len(loaded) == 10
    assert [task.task_id for task in loaded] == [task.task_id for task in tasks()]


def test_runner_loads_only_selected_manifest_tasks() -> None:
    loaded = baseline.load_tasks(
        BENCHMARK_ROOT,
        ["ap_010_retry_timeout_fsm", "ap_001_idle_counter"],
    )

    assert [task.task_id for task in loaded] == [
        "ap_001_idle_counter",
        "ap_010_retry_timeout_fsm",
    ]


@pytest.mark.parametrize(
    "task_ids",
    [
        ["ap_001_idle_counter", "ap_001_idle_counter"],
        ["ap_999_unknown"],
    ],
)
def test_runner_rejects_invalid_task_selection(task_ids: list[str]) -> None:
    with pytest.raises(ValueError):
        baseline.load_tasks(BENCHMARK_ROOT, task_ids)


def test_blocker_rows_cover_ten_tasks_and_three_samples() -> None:
    config = baseline.EndpointConfig(
        base_url=None,
        credential=None,
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = baseline.make_blocker_rows(
        tasks=tasks(),
        endpoint=config,
        tools=baseline.ToolAvailability(iverilog=None, vvp=None, yosys=None),
        samples=3,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
    )

    assert len(rows) == 30
    assert {item.task_id for item in rows} == {task.task_id for task in tasks()}
    assert {item.sample_id for item in rows} == {1, 2, 3}
    assert {item.failure_category for item in rows} == {"endpoint_unavailable"}
    assert {item.request_outcome for item in rows} == {"endpoint_unavailable"}
    assert {item.request_attempt_count for item in rows} == {0}
    for item in rows:
        item.sanitized_dict()


def test_missing_tools_create_tool_blocker_rows() -> None:
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = baseline.make_blocker_rows(
        tasks=tasks(),
        endpoint=config,
        tools=baseline.ToolAvailability(iverilog=None, vvp="vvp", yosys="yosys"),
        samples=3,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
    )

    assert len(rows) == 30
    assert {item.failure_category for item in rows} == {"tool_unavailable"}
    assert {item.endpoint_status for item in rows} == {"available"}
    assert {item.request_outcome for item in rows} == {"tool_health_blocker"}


def test_unhealthy_tools_create_health_blocker_rows() -> None:
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    tools = baseline.ToolAvailability(
        iverilog="iverilog",
        vvp="vvp",
        yosys="yosys",
        iverilog_healthy=False,
    )
    rows = baseline.make_blocker_rows(
        tasks=tasks(),
        endpoint=config,
        tools=tools,
        samples=3,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
    )

    assert baseline.tools_available(tools) is False
    assert len(rows) == 30
    assert {item.failure_category for item in rows} == {"tool_health_failed"}
    assert all("health check" in item.notes for item in rows)


def test_aggregate_score_value_zero_fills_invalid_rows() -> None:
    assert baseline.aggregate_score_value(row()) == 0.0
    assert baseline.aggregate_score_value(row(score_status="valid", score=1.25)) == 1.25


def test_request_failures_are_sanitized_rows() -> None:
    task = tasks()[0]
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    generation = baseline.GenerationRecord(
        task_id=task.task_id,
        sample_id=1,
        generation_status="request_failed",
        extraction_status="not_run",
        candidate_file_available=False,
        failure_category="request_failed",
        notes="generation request failed: connection reset",
        request_outcome="transport_error",
        request_attempt_count=3,
        latency_seconds=0.5,
        response_parse_status="not_attempted",
    )
    evaluation = baseline.CandidateEvaluationRow(
        task_id=task.task_id,
        candidate_id="sample_01",
        final_pass=False,
        candidate_file_available=False,
        compile_pass=False,
        correctness_pass=False,
        synth_pass=False,
        timing_status="not_required",
        reference_area=15.0,
        generated_area=None,
        area_unit="generic_cells",
        reference_activity=34.0,
        generated_activity=None,
        activity_metric="total_signal_toggles",
        area_score=None,
        activity_score=None,
        score=None,
        score_status="invalid",
        failure_category="candidate_missing",
        toolchain_id="iverilog-vcd-yosys-generic",
        workload_id="ap_001_idle_counter_default",
        notes="candidate file missing",
    )

    rows = baseline.merge_rows(
        tasks=[task],
        endpoint=config,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
        samples=1,
        generation_records={(task.task_id, 1): generation},
        evaluation_rows={(task.task_id, 1): evaluation},
    )

    assert rows[0].failure_category == "request_failed"
    assert rows[0].generation_status == "request_failed"
    assert rows[0].endpoint_status == "available"
    assert rows[0].request_outcome == "transport_error"
    assert rows[0].request_attempt_count == 3
    assert rows[0].latency_seconds == 0.5
    rows[0].sanitized_dict()


def test_generate_samples_propagates_empty_success_metadata(monkeypatch, tmp_path: Path) -> None:
    task = tasks()[0]
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )

    monkeypatch.setattr(
        baseline.OpenAICompatibleClient,
        "generate",
        lambda self, **kwargs: baseline.GenerationResult(
            text="",
            latency_seconds=0.25,
            usage={"prompt_tokens": 12, "completion_tokens": 0, "total_tokens": 12},
            request_outcome="success_empty",
            request_attempt_count=2,
            response_choice_count=1,
            response_content_present=True,
            response_character_count=0,
            finish_reason="stop",
            http_status_class="2xx",
            response_parse_status="parsed",
        ),
    )

    record = baseline.generate_samples(
        tasks=[task],
        endpoint=config,
        run_root=tmp_path / "run",
        candidate_root=tmp_path / "candidates",
        samples=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
        system_prompt="test system prompt",
        extra_body={},
    )[(task.task_id, 1)]

    assert record.failure_category == "empty_response"
    assert record.request_outcome == "success_empty"
    assert record.request_attempt_count == 2
    assert record.latency_seconds == 0.25
    assert record.response_character_count == 0
    assert record.completion_tokens == 0
    assert record.total_tokens == 12


def test_generate_samples_propagates_structured_request_failure(monkeypatch, tmp_path: Path) -> None:
    task = tasks()[0]
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )

    def fail(self, **kwargs):
        raise baseline.GenerationRequestError(
            request_outcome="timeout",
            request_attempt_count=3,
            latency_seconds=3.0,
            response_parse_status="not_attempted",
        )

    monkeypatch.setattr(baseline.OpenAICompatibleClient, "generate", fail)

    record = baseline.generate_samples(
        tasks=[task],
        endpoint=config,
        run_root=tmp_path / "run",
        candidate_root=tmp_path / "candidates",
        samples=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
        system_prompt="test system prompt",
        extra_body={},
    )[(task.task_id, 1)]

    assert record.failure_category == "request_failed"
    assert record.request_outcome == "timeout"
    assert record.request_attempt_count == 3
    assert record.latency_seconds == 3.0
    assert record.response_parse_status == "not_attempted"


def test_missing_current_candidate_cannot_inherit_stale_metrics() -> None:
    task = tasks()[0]
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    generation = baseline.GenerationRecord(
        task_id=task.task_id,
        sample_id=1,
        generation_status="completed",
        extraction_status="failed",
        candidate_file_available=False,
        failure_category="empty_response",
        notes="empty response",
    )
    stale_evaluation = baseline.CandidateEvaluationRow(
        task_id=task.task_id,
        candidate_id="sample_01",
        final_pass=True,
        candidate_file_available=True,
        compile_pass=True,
        correctness_pass=True,
        synth_pass=True,
        timing_status="not_required",
        reference_area=15.0,
        generated_area=12.0,
        area_unit="generic_cells",
        reference_activity=34.0,
        generated_activity=30.0,
        activity_metric="total_signal_toggles",
        area_score=1.25,
        activity_score=1.13,
        score=1.19,
        score_status="valid",
        failure_category="passed",
        toolchain_id="iverilog-vcd-yosys-generic",
        workload_id="ap_001_idle_counter_default",
        notes="candidate validated",
    )

    result = baseline.merge_rows(
        tasks=[task],
        endpoint=config,
        prompt_profile="neutral_baseline",
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
        samples=1,
        generation_records={(task.task_id, 1): generation},
        evaluation_rows={(task.task_id, 1): stale_evaluation},
    )[0]

    assert result.candidate_file_available is False
    assert result.area_metric_available is False
    assert result.activity_metric_available is False
    assert result.generated_area is None
    assert result.generated_activity is None
    assert result.score is None
    assert result.failure_category == "empty_response"


def test_models_preflight_is_not_required_by_default(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["run_rfid_apbench_3sample_baseline.py"])

    args = baseline.parse_args()

    assert args.require_models_preflight is False


def test_task_id_filters_are_repeatable(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_rfid_apbench_3sample_baseline.py",
            "--task-id",
            "ap_001_idle_counter",
            "--task-id",
            "ap_010_retry_timeout_fsm",
        ],
    )

    args = baseline.parse_args()

    assert args.task_ids == ["ap_001_idle_counter", "ap_010_retry_timeout_fsm"]


def test_completion_reliability_profile_is_resolved() -> None:
    prompt = baseline.resolve_system_prompt("completion_reliability")

    assert "complete" in prompt
    assert "endmodule" in prompt
    assert "Markdown fences" in prompt


def test_qwen_model_preset_disables_thinking() -> None:
    extra_body = baseline.resolve_model_extra_body("qwen36-27b")

    assert extra_body == {"chat_template_kwargs": {"enable_thinking": False}}


def test_unknown_or_missing_model_preset_has_empty_extra_body(tmp_path: Path) -> None:
    assert baseline.resolve_model_extra_body("unknown-model") == {}
    assert baseline.resolve_model_extra_body("qwen36-27b", tmp_path / "missing.yaml") == {}


def test_generate_samples_propagates_resolved_system_prompt(monkeypatch, tmp_path: Path) -> None:
    task = tasks()[0]
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    observed: dict[str, object] = {}

    def generate(self, **kwargs):
        observed.update(kwargs)
        return baseline.GenerationResult(text="")

    monkeypatch.setattr(baseline.OpenAICompatibleClient, "generate", generate)
    expected_prompt = baseline.resolve_system_prompt("completion_reliability")
    expected_extra_body = {"chat_template_kwargs": {"enable_thinking": False}}

    baseline.generate_samples(
        tasks=[task],
        endpoint=config,
        run_root=tmp_path / "run",
        candidate_root=tmp_path / "candidates",
        samples=1,
        temperature=0.0,
        top_p=1.0,
        max_tokens=4096,
        system_prompt=expected_prompt,
        extra_body=expected_extra_body,
    )

    assert observed["system_prompt"] == expected_prompt
    assert observed["extra_body"] == expected_extra_body


def test_main_rejects_samples_per_task_other_than_three(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_rfid_apbench_3sample_baseline.py", "--samples-per-task", "2"],
    )

    with pytest.raises(ValueError, match="exactly 3 samples per task"):
        baseline.main()


def test_report_writers_emit_sanitized_baseline(tmp_path: Path) -> None:
    config = baseline.EndpointConfig(
        base_url="http://127.0.0.1:8000/v1",
        credential="local-vllm-no-auth",
        model="qwen36-27b",
        timeout_seconds=1.0,
    )
    rows = [
        row(task_id=task.task_id, sample_id=sample_id)
        for sample_id in range(1, 4)
        for task in tasks()
    ]
    output_md = tmp_path / "baseline.md"
    output_csv = tmp_path / "baseline.csv"
    output_jsonl = tmp_path / "baseline.jsonl"

    baseline.write_markdown_report(
        rows,
        output_md,
        endpoint=config,
        tools=baseline.ToolAvailability(iverilog="iverilog", vvp="vvp", yosys="yosys"),
        run_id="test_run",
    )
    baseline.write_csv_report(rows, output_csv)
    baseline.write_jsonl_report(rows, output_jsonl)

    markdown = output_md.read_text(encoding="utf-8")
    csv_text = output_csv.read_text(encoding="utf-8")
    json_rows = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]
    assert "Mean all-sample score" in markdown
    assert "- Task count: 10" in markdown
    assert "- Samples per task: 3" in markdown
    assert "- Total sample count: 30" in markdown
    assert "## Comparison Against Five-Task Post-Tool-Health Baseline" in markdown
    assert "| attempted samples | 15 | 30 |" in markdown
    assert "## Request And Response Observability" in markdown
    assert "raw response fixture" not in markdown
    assert "raw_model_response" not in csv_text
    assert json_rows[0]["benchmark"] == "rfid_apbench"
    assert set(baseline.OBSERVABILITY_FIELDS) <= set(json_rows[0])
    assert all(field in csv_text.splitlines()[0] for field in baseline.OBSERVABILITY_FIELDS)
    assert len(json_rows) == 30
