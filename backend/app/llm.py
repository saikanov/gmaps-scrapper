"""OpenAI-compatible LLM client (targets a vLLM endpoint).

The repo uses a self-hosted model (e.g. qwen3.5) exposed via an OpenAI-compatible
API. Two practical concerns are handled here:

1. Reasoning models emit `<think>...</think>` blocks — we strip them.
2. Tool-calling support is uneven across vLLM builds, so instead of relying on
   function-calling we ask for strict JSON and parse robustly (fenced block,
   first balanced object/array). This keeps both AI touchpoints (§7 keyword-gen
   and §9 scoring) working on any OpenAI-compatible backend.
"""
from __future__ import annotations

import json
import re
from typing import Any

from openai import AsyncOpenAI

from .config import settings

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
# An unclosed/truncated <think> (model spent its whole budget reasoning).
_OPEN_THINK_RE = re.compile(r"<think>.*\Z", re.DOTALL | re.IGNORECASE)


class LLMNotConfigured(RuntimeError):
    pass


def _client() -> AsyncOpenAI:
    if not settings.llm_host or not settings.llm_model:
        raise LLMNotConfigured("LLM_HOST / LLM_MODEL not set in environment")
    return AsyncOpenAI(
        base_url=settings.llm_host,
        api_key=settings.llm_api_key or "not-needed",
        timeout=settings.llm_timeout,
    )


# Disable qwen "thinking" mode on the orion gateway: pass enable_thinking=False
# as a top-level chat_template_kwargs param, which requires opting in to extra
# param pass-through via this header. Reasoning off => no empty completions,
# faster responses, and far smaller token budgets.
_THINK_OFF_HEADERS = {"x-bf-passthrough-extra-params": "true"}
_THINK_OFF_BODY = {"chat_template_kwargs": {"enable_thinking": False}}


def is_configured() -> bool:
    return bool(settings.llm_host and settings.llm_model)


def _strip_think(text: str) -> str:
    text = _THINK_RE.sub("", text or "")
    text = _OPEN_THINK_RE.sub("", text)  # drop a dangling unclosed block
    return text.strip()


def _extract_json(text: str) -> Any:
    """Best-effort: parse a JSON object/array out of a model response."""
    text = _strip_think(text)
    # 1) fenced ```json ... ``` block
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # 2) direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 3) first balanced { } or [ ] span
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = text.find(open_ch)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_ch:
                depth += 1
            elif text[i] == close_ch:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
    raise ValueError(f"Could not extract JSON from model output: {text[:300]}")


async def chat_json(
    system: str,
    user: str,
    *,
    temperature: float | None = None,
    max_tokens: int = 8000,
) -> Any:
    """Run one chat completion and return parsed JSON.

    The target vLLM model (qwen3.5) is a reasoning model that emits <think>
    blocks; it needs generous max_tokens so the answer survives after reasoning,
    and it returns empty completions if a /no_think directive is added. So we
    give room, strip <think>, ask for JSON via response_format, and retry.
    """
    client = _client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    temp = settings.llm_temperature if temperature is None else temperature

    kwargs: dict[str, Any] = dict(
        model=settings.llm_model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens,
        extra_headers=_THINK_OFF_HEADERS,
    )

    last_err: Exception | None = None
    for attempt in range(3):
        try:
            try:
                resp = await client.chat.completions.create(
                    response_format={"type": "json_object"},
                    extra_body=_THINK_OFF_BODY,
                    **kwargs,
                )
            except Exception:
                # backend may not support response_format — retry without it.
                resp = await client.chat.completions.create(
                    extra_body=_THINK_OFF_BODY, **kwargs
                )
            content = resp.choices[0].message.content or ""
            if content.strip():
                return _extract_json(content)
            last_err = ValueError("empty model response")
        except Exception as exc:  # noqa: BLE001 — retry transient/parse failures
            last_err = exc
    raise last_err or ValueError("LLM call failed")


async def chat_text(system: str, user: str, *, max_tokens: int = 1024) -> str:
    client = _client()
    resp = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=settings.llm_temperature,
        max_tokens=max_tokens,
        extra_headers=_THINK_OFF_HEADERS,
        extra_body=_THINK_OFF_BODY,
    )
    return _strip_think(resp.choices[0].message.content or "")
