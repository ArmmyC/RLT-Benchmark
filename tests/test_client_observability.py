from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest

import rtlbench.client as client_module
from rtlbench.client import GenerationRequestError, OpenAICompatibleClient
from rtlbench.types import GenerationResult


def make_client(
    handler: Callable[[httpx.Request], httpx.Response], *, retries: int = 0
) -> OpenAICompatibleClient:
    client = OpenAICompatibleClient(
        base_url="http://test.local/v1",
        api_key="test-key",
        timeout=1.0,
        retries=retries,
    )
    client.client.close()
    client.client = httpx.Client(transport=httpx.MockTransport(handler))
    return client


def generate(client: OpenAICompatibleClient) -> GenerationResult:
    return client.generate(
        model="test-model",
        system_prompt="system",
        user_prompt="prompt",
        temperature=0.0,
        top_p=1.0,
        max_tokens=32,
    )


def test_nonempty_success_metadata() -> None:
    client = make_client(
        lambda request: httpx.Response(
            200,
            request=request,
            json={
                "choices": [
                    {
                        "message": {"content": "module top; endmodule"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )
    )
    try:
        result = generate(client)
    finally:
        client.close()

    assert result.request_outcome == "success_nonempty"
    assert result.request_attempt_count == 1
    assert result.response_choice_count == 1
    assert result.response_content_present is True
    assert result.response_character_count == 21
    assert result.finish_reason == "stop"
    assert result.http_status_class == "2xx"
    assert result.response_parse_status == "parsed"
    assert result.usage == {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}


def test_empty_success_metadata() -> None:
    client = make_client(
        lambda request: httpx.Response(
            200,
            request=request,
            json={
                "choices": [{"message": {"content": ""}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
            },
        )
    )
    try:
        result = generate(client)
    finally:
        client.close()

    assert result.text == ""
    assert result.request_outcome == "success_empty"
    assert result.response_content_present is True
    assert result.response_character_count == 0
    assert result.usage is not None
    assert result.usage["completion_tokens"] == 0


def test_whitespace_success_is_empty_outcome() -> None:
    client = make_client(
        lambda request: httpx.Response(
            200,
            request=request,
            json={"choices": [{"message": {"content": "  \n"}, "finish_reason": "stop"}]},
        )
    )
    try:
        result = generate(client)
    finally:
        client.close()

    assert result.request_outcome == "success_empty"
    assert result.response_content_present is True
    assert result.response_character_count == 3


def test_timeout_metadata_includes_retry_count(monkeypatch) -> None:
    attempts = 0

    def timeout(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("timed out", request=request)

    monkeypatch.setattr(client_module.time, "sleep", lambda seconds: None)
    client = make_client(timeout, retries=1)
    try:
        with pytest.raises(GenerationRequestError) as captured:
            generate(client)
    finally:
        client.close()

    assert attempts == 2
    assert captured.value.request_outcome == "timeout"
    assert captured.value.request_attempt_count == 2
    assert captured.value.response_parse_status == "not_attempted"


def test_http_error_metadata_is_sanitized() -> None:
    client = make_client(
        lambda request: httpx.Response(503, request=request, text="raw secret response body")
    )
    try:
        with pytest.raises(GenerationRequestError) as captured:
            generate(client)
    finally:
        client.close()

    assert captured.value.request_outcome == "http_error"
    assert captured.value.http_status_class == "5xx"
    assert "raw secret response body" not in str(captured.value)


def test_transport_error_metadata() -> None:
    def disconnect(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    client = make_client(disconnect)
    try:
        with pytest.raises(GenerationRequestError) as captured:
            generate(client)
    finally:
        client.close()

    assert captured.value.request_outcome == "transport_error"
    assert captured.value.http_status_class is None


@pytest.mark.parametrize(
    ("response", "outcome", "parse_status", "choice_count"),
    [
        (
            lambda request: httpx.Response(200, request=request, content=b"not json"),
            "response_parse_failure",
            "json_error",
            None,
        ),
        (
            lambda request: httpx.Response(
                200,
                request=request,
                json={
                    "choices": [],
                    "usage": {"prompt_tokens": 4, "completion_tokens": 0, "total_tokens": 4},
                },
            ),
            "response_schema_failure",
            "schema_error",
            0,
        ),
    ],
)
def test_response_parse_and_schema_failure_metadata(
    response: Callable[[httpx.Request], httpx.Response],
    outcome: str,
    parse_status: str,
    choice_count: int | None,
) -> None:
    client = make_client(response)
    try:
        with pytest.raises(GenerationRequestError) as captured:
            generate(client)
    finally:
        client.close()

    assert captured.value.request_outcome == outcome
    assert captured.value.response_parse_status == parse_status
    assert captured.value.response_choice_count == choice_count
    assert captured.value.http_status_class == "2xx"
    if outcome == "response_schema_failure":
        assert captured.value.prompt_tokens == 4
        assert captured.value.completion_tokens == 0
        assert captured.value.total_tokens == 4


def test_non_object_json_is_schema_failure() -> None:
    client = make_client(
        lambda request: httpx.Response(200, request=request, json=[])
    )
    try:
        with pytest.raises(GenerationRequestError) as captured:
            generate(client)
    finally:
        client.close()

    assert captured.value.request_outcome == "response_schema_failure"
    assert captured.value.response_parse_status == "schema_error"
    assert captured.value.prompt_tokens is None
