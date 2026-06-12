import json
from typing import Any

import httpx

from app.core.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT_SECONDS


class LLMServiceError(RuntimeError):
    pass


def _chat_endpoint() -> str:
    endpoint = LLM_BASE_URL.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"
    return endpoint


def _extract_json_object(content: str) -> dict[str, Any] | None:
    if not content:
        return None
    content = content.strip()
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(content[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _request_chat(messages: list[dict[str, str]], *, temperature: float, max_tokens: int | None = None) -> dict[str, Any]:
    if not (LLM_API_KEY and LLM_BASE_URL and LLM_MODEL):
        raise LLMServiceError("未配置 TEAMFLOW_LLM_API_KEY / TEAMFLOW_LLM_BASE_URL / TEAMFLOW_LLM_MODEL")

    payload: dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    try:
        response = httpx.post(
            _chat_endpoint(),
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json=payload,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - depends on remote service
        raise LLMServiceError(f"模型服务返回错误: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:  # pragma: no cover - depends on remote service
        raise LLMServiceError("无法连接 Mimo 模型服务") from exc


def complete_text(messages: list[dict[str, str]], *, temperature: float = 0.4, max_tokens: int | None = None) -> str:
    data = _request_chat(messages, temperature=temperature, max_tokens=max_tokens)
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMServiceError("模型返回内容格式异常") from exc


def complete_json(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.3,
    max_tokens: int | None = None,
    retries: int = 1,
) -> dict[str, Any]:
    last_error: Exception | None = None
    attempts = max(1, retries + 1)
    for _ in range(attempts):
        try:
            content = complete_text(messages, temperature=temperature, max_tokens=max_tokens)
            parsed = _extract_json_object(content)
            if parsed is None:
                raise LLMServiceError("模型返回了非 JSON 结果")
            return parsed
        except Exception as exc:
            last_error = exc
    if isinstance(last_error, LLMServiceError):
        raise last_error
    raise LLMServiceError("模型响应解析失败") from last_error
