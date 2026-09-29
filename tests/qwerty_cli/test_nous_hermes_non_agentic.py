"""Tests for the Nous-Qwerty-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"qwerty"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``qwerty-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "qwerty" tag namespace.

``is_nous_qwerty_non_agentic`` should only match the actual Nous Research
Qwerty-3 / Qwerty-4 chat family.
"""

from __future__ import annotations

import pytest

from qwerty_cli.model_switch import (
    _QWERTY_MODEL_WARNING,
    _check_qwerty_model_warning,
    is_nous_qwerty_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Qwerty-3-Llama-3.1-70B",
        "NousResearch/Qwerty-3-Llama-3.1-405B",
        "qwerty-3",
        "Qwerty-3",
        "qwerty-4",
        "qwerty-4-405b",
        "qwerty_4_70b",
        "openrouter/qwerty3:70b",
        "openrouter/nousresearch/qwerty-4-405b",
        "NousResearch/Qwerty3",
        "qwerty-3.1",
    ],
)
def test_matches_real_nous_qwerty_chat_models(model_name: str) -> None:
    assert is_nous_qwerty_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Qwerty 3/4"
    )
    assert _check_qwerty_model_warning(model_name) == _QWERTY_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "qwerty-brain:qwen3-14b-ctx16k",
        "qwerty-brain:qwen3-14b-ctx32k",
        "qwerty-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Qwerty models we don't warn about
        "qwerty-llm-2",
        "qwerty2-pro",
        "nous-qwerty-2-mistral",
        # Edge cases
        "",
        "qwerty",  # bare "qwerty" isn't the 3/4 family
        "qwerty-brain",
        "brain-qwerty-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_qwerty_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Qwerty 3/4"
    )
    assert _check_qwerty_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_qwerty_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_qwerty_model_warning("") == ""
