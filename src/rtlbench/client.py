from __future__ import annotations

import time
from typing import Any

import httpx

from rtlbench.types import GenerationResult


class GenerationRequestError(RuntimeError):
    def __init__(
        self,
        *,
        request_outcome: str,
        request_attempt_count: int,
        latency_seconds: float,
        http_status_class: str | None = None,
        response_parse_status: str = "unavailable",
        response_choice_count: int | None = None,
        response_content_present: bool | None = None,
        response_character_count: int | None = None,
        finish_reason: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
    ) -> None:
        super().__init__(
            f"model request failed after {request_attempt_count} attempt(s): {request_outcome}"
        )
        self.request_outcome = request_outcome
        self.request_attempt_count = request_attempt_count
        self.latency_seconds = latency_seconds
        self.http_status_class = http_status_class
        self.response_parse_status = response_parse_status
        self.response_choice_count = response_choice_count
        self.response_content_present = response_content_present
        self.response_character_count = response_character_count
        self.finish_reason = finish_reason
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, timeout: float, retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self.client = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def close(self) -> None:
        self.client.close()

    def generate(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        extra_body: dict[str, Any] | None = None,
    ) -> GenerationResult:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        if extra_body:
            payload.update(extra_body)
        started = time.monotonic()
        last_metadata: dict[str, Any] = {
            "request_outcome": "request_failure",
            "http_status_class": None,
            "response_parse_status": "unavailable",
        }
        for attempt in range(self.retries + 1):
            try:
                response = self.client.post(f"{self.base_url}/chat/completions", json=payload)
                response.raise_for_status()
            except httpx.TimeoutException:
                last_metadata = {
                    "request_outcome": "timeout",
                    "http_status_class": None,
                    "response_parse_status": "not_attempted",
                }
            except httpx.HTTPStatusError as exc:
                last_metadata = {
                    "request_outcome": "http_error",
                    "http_status_class": _http_status_class(exc.response.status_code),
                    "response_parse_status": "not_attempted",
                }
            except httpx.RequestError:
                last_metadata = {
                    "request_outcome": "transport_error",
                    "http_status_class": None,
                    "response_parse_status": "not_attempted",
                }
            else:
                http_status_class = _http_status_class(response.status_code)
                try:
                    body = response.json()
                except (TypeError, ValueError):
                    last_metadata = {
                        "request_outcome": "response_parse_failure",
                        "http_status_class": http_status_class,
                        "response_parse_status": "json_error",
                    }
                else:
                    parsed = _parse_response_metadata(body)
                    if parsed["response_parse_status"] != "parsed":
                        last_metadata = {
                            "request_outcome": "response_schema_failure",
                            "http_status_class": http_status_class,
                            **parsed,
                            **_usage_metadata(body),
                        }
                    else:
                        text = parsed.pop("text")
                        request_outcome = "success_nonempty" if text.strip() else "success_empty"
                        usage = body.get("usage") if isinstance(body, dict) else None
                        if not isinstance(usage, dict):
                            usage = None
                        return GenerationResult(
                            text=text,
                            latency_seconds=time.monotonic() - started,
                            usage=usage,
                            request_outcome=request_outcome,
                            request_attempt_count=attempt + 1,
                            http_status_class=http_status_class,
                            **parsed,
                        )

            if attempt < self.retries:
                time.sleep(2**attempt)
                continue
            raise GenerationRequestError(
                request_attempt_count=attempt + 1,
                latency_seconds=time.monotonic() - started,
                **last_metadata,
            )

        raise AssertionError("request loop exited unexpectedly")


def _http_status_class(status_code: int) -> str:
    return f"{status_code // 100}xx"


def _parse_response_metadata(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        return {
            "response_parse_status": "schema_error",
            "response_choice_count": None,
            "response_content_present": None,
            "response_character_count": None,
            "finish_reason": None,
        }
    choices = body.get("choices")
    if not isinstance(choices, list):
        return {
            "response_parse_status": "schema_error",
            "response_choice_count": None,
            "response_content_present": None,
            "response_character_count": None,
            "finish_reason": None,
        }
    choice_count = len(choices)
    if not choices or not isinstance(choices[0], dict):
        return {
            "response_parse_status": "schema_error",
            "response_choice_count": choice_count,
            "response_content_present": None,
            "response_character_count": None,
            "finish_reason": None,
        }
    choice = choices[0]
    finish_reason = choice.get("finish_reason")
    if not isinstance(finish_reason, str):
        finish_reason = None
    message = choice.get("message")
    if not isinstance(message, dict) or "content" not in message:
        return {
            "response_parse_status": "schema_error",
            "response_choice_count": choice_count,
            "response_content_present": None,
            "response_character_count": None,
            "finish_reason": finish_reason,
        }
    content = message["content"]
    if content is not None and not isinstance(content, str):
        return {
            "response_parse_status": "schema_error",
            "response_choice_count": choice_count,
            "response_content_present": True,
            "response_character_count": None,
            "finish_reason": finish_reason,
        }
    text = content or ""
    return {
        "text": text,
        "response_parse_status": "parsed",
        "response_choice_count": choice_count,
        "response_content_present": content is not None,
        "response_character_count": len(text),
        "finish_reason": finish_reason,
    }


def _usage_metadata(body: Any) -> dict[str, int | None]:
    usage = body.get("usage") if isinstance(body, dict) else None
    if not isinstance(usage, dict):
        usage = {}
    return {
        "prompt_tokens": _usage_count(usage.get("prompt_tokens")),
        "completion_tokens": _usage_count(usage.get("completion_tokens")),
        "total_tokens": _usage_count(usage.get("total_tokens")),
    }


def _usage_count(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None
