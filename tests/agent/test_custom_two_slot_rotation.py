"""Regression coverage for custom-provider two-slot 429 key rotation."""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock

from agent.agent_runtime_helpers import recover_with_credential_pool
from agent.credential_pool import (
    CUSTOM_429_COOLDOWN_SECONDS,
    STATUS_COOLDOWN,
    STATUS_EXHAUSTED,
    CredentialPool,
    PooledCredential,
)
from agent.error_classifier import FailoverReason


def _entry(n: int) -> PooledCredential:
    return PooledCredential(
        provider="custom:pool",
        id=f"key-{n}",
        label=f"key-{n}",
        auth_type="api_key",
        priority=n - 1,
        source="manual",
        access_token=f"secret-{n}",
        base_url="https://api.example.test/v1",
    )


def test_custom_429_cools_key_and_immediately_uses_second(monkeypatch):
    pool = CredentialPool("custom:pool", [_entry(1), _entry(2), _entry(3)])
    monkeypatch.setattr(pool, "_persist", lambda **_kwargs: None)
    assert pool.select().id == "key-1"

    next_entry, wrapped = pool.mark_custom_429_and_rotate(api_key_hint="secret-1")

    assert next_entry.id == "key-2"
    assert wrapped is False
    first = pool.entries()[0]
    assert first.last_status == STATUS_COOLDOWN
    assert first.last_error_code == 429


def test_custom_key_second_429_after_cooldown_becomes_exhausted(monkeypatch):
    first = _entry(1)
    first.last_status = STATUS_COOLDOWN
    first.last_error_code = 429
    first.last_status_at = time.time() - CUSTOM_429_COOLDOWN_SECONDS - 1
    pool = CredentialPool("custom:pool", [first, _entry(2)])
    monkeypatch.setattr(pool, "_persist", lambda **_kwargs: None)
    pool.mark_custom_429_and_rotate(api_key_hint="secret-1")

    assert pool.entries()[0].last_status == STATUS_EXHAUSTED


def test_wraparound_probes_all_keys_and_uses_live_key(monkeypatch):
    pool = MagicMock()
    pool.provider = "custom:pool"
    pool.entries.return_value = [MagicMock(runtime_base_url="https://api.example.test/v1")]
    pool.mark_custom_429_and_rotate.return_value = (MagicMock(id="key-1"), True)
    live = MagicMock(id="key-2")
    pool.probe_custom_keys.return_value = (live, 2, 1)
    agent = SimpleNamespace(
        _credential_pool=pool,
        provider="custom",
        base_url="https://api.example.test/v1",
        api_key="secret-3",
        model="selected-model",
        _custom_quota_check_announced=False,
        _custom_credential_pool_exhausted=False,
        _emit_status=MagicMock(),
        _swap_credential=MagicMock(),
    )

    monkeypatch.setattr(
        "agent.credential_pool.get_custom_provider_pool_key", lambda _url: "custom:pool"
    )
    recovered, _ = recover_with_credential_pool(
        agent,
        status_code=429,
        has_retried_429=False,
        classified_reason=FailoverReason.rate_limit,
        error_context={"message": "rate limit"},
    )

    assert recovered is True
    pool.probe_custom_keys.assert_called_once_with("selected-model")
    agent._swap_credential.assert_called_once_with(live)
    messages = [call.args[0] for call in agent._emit_status.call_args_list]
    assert any("2 живых, 1 мёртвых, всего 3" in message for message in messages)


def test_all_dead_after_probe_emits_final_quota_message(monkeypatch):
    pool = MagicMock()
    pool.provider = "custom:pool"
    pool.entries.return_value = [MagicMock(runtime_base_url="https://api.example.test/v1")]
    pool.mark_custom_429_and_rotate.return_value = (None, False)
    pool.probe_custom_keys.return_value = (None, 0, 2)
    agent = SimpleNamespace(
        _credential_pool=pool,
        provider="custom",
        base_url="https://api.example.test/v1",
        api_key="secret-2",
        model="selected-model",
        _custom_quota_check_announced=False,
        _custom_credential_pool_exhausted=False,
        _emit_status=MagicMock(),
        _swap_credential=MagicMock(),
    )
    monkeypatch.setattr(
        "agent.credential_pool.get_custom_provider_pool_key", lambda _url: "custom:pool"
    )

    recovered, _ = recover_with_credential_pool(
        agent,
        status_code=429,
        has_retried_429=False,
        classified_reason=FailoverReason.rate_limit,
    )

    assert recovered is False
    assert agent._custom_credential_pool_exhausted is True
    messages = [call.args[0] for call in agent._emit_status.call_args_list]
    assert any("0 живых, 2 мёртвых, всего 2" in message for message in messages)
    assert any("возвращайтесь завтра" in message for message in messages)
