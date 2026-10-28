"""Regression tests for the credential-pool provider-mismatch guard with
custom providers (Bernard's Fireworks report, June 2026).

Custom endpoints carry two naming conventions for the same provider: the
agent's ``provider`` attribute is the generic ``"custom"`` label while the
pool is keyed ``custom:<normalized-name>`` (``CUSTOM_POOL_PREFIX``).  The
defensive guard in ``recover_with_credential_pool`` compared the two
literally, logged "Credential pool provider mismatch: pool=custom:<name>,
agent=custom", and skipped recovery — so 401/429 recovery (refresh,
rotation) never ran for ANY custom-provider user.

The fix accepts the pair only when the agent's current base_url resolves to
the same pool key, preserving the guard's original purpose (#33088/#33163:
never mutate the primary's pool while a fallback provider is active).
"""
from unittest.mock import MagicMock, patch

import pytest

from agent.agent_runtime_helpers import recover_with_credential_pool
from agent.error_classifier import FailoverReason


FIREWORKS_URL = "https://api.fireworks.ai/inference/v1"


def _agent(provider, base_url, pool_provider):
    agent = MagicMock()
    agent.provider = provider
    agent.base_url = base_url
    pool = MagicMock()
    pool.provider = pool_provider
    agent._credential_pool = pool
    return agent, pool


class TestCustomPoolMismatchGuard:
    def test_custom_pool_rotates_on_unknown_provider_failure(self):
        """Every failed custom-endpoint request consumes the issuing key."""
        agent, pool = _agent("custom", "https://odirouter.example/v1", "custom:odirouter")
        next_entry = MagicMock()
        pool.mark_exhausted_and_rotate.return_value = next_entry
        pool.entries.return_value = [
            MagicMock(runtime_base_url="https://odirouter.example/v1")
        ]

        recovered, retried = recover_with_credential_pool(
            agent,
            status_code=None,
            has_retried_429=False,
            classified_reason=FailoverReason.unknown,
            error_context={"message": "provider returned an invalid response"},
        )

        assert recovered is True
        assert retried is False
        pool.mark_exhausted_and_rotate.assert_called_once_with(
            status_code=520,
            error_context={"message": "provider returned an invalid response"},
            api_key_hint=agent.api_key,
        )
        agent._swap_credential.assert_called_once_with(next_entry)

    def test_custom_pool_marks_exhausted_when_no_next_key_exists(self):
        """Gateway can render a clear retry-later notice once the pool is empty."""
        agent, pool = _agent("custom", "https://odirouter.example/v1", "custom:odirouter")
        pool.entries.return_value = [
            MagicMock(runtime_base_url="https://odirouter.example/v1")
        ]
        pool.mark_custom_429_and_rotate.return_value = (None, False)
        pool.probe_custom_keys.return_value = (None, 0, 1)

        recovered, _ = recover_with_credential_pool(
            agent,
            status_code=429,
            has_retried_429=False,
            classified_reason=FailoverReason.rate_limit,
        )

        assert recovered is False
        assert agent._custom_credential_pool_exhausted is True

    def test_matching_custom_pool_reaches_recovery(self):
        """agent=custom + pool=custom:<name> whose base_url matches must NOT
        be treated as a cross-provider mismatch."""
        agent, pool = _agent("custom", FIREWORKS_URL, "custom:fireworks")
        # Rate-limit path deterministically calls pool.current() once past
        # the guard (the auth path consults agent._is_entitlement_failure,
        # which a MagicMock would answer truthily).
        pool.current.return_value = None
        pool.mark_custom_429_and_rotate.return_value = (None, False)
        pool.probe_custom_keys.return_value = (None, 0, 0)
        with patch(
            "agent.credential_pool.get_custom_provider_pool_key",
            return_value="custom:fireworks",
        ):
            recover_with_credential_pool(
                agent,
                status_code=429,
                has_retried_429=False,
                classified_reason=FailoverReason.rate_limit,
            )
        assert pool.mark_custom_429_and_rotate.called, (
            "guard short-circuited: pool never touched despite matching "
            "custom base_url"
        )

    def test_matching_custom_pool_uses_pool_entry_when_config_lookup_fails(self):
        """A cached gateway agent must rotate even if config lookup is unavailable."""
        agent, pool = _agent("custom", FIREWORKS_URL, "custom:fireworks")
        pool.entries.return_value = [
            MagicMock(runtime_base_url=FIREWORKS_URL, base_url=FIREWORKS_URL)
        ]
        pool.current.return_value = None
        pool.mark_custom_429_and_rotate.return_value = (None, False)
        pool.probe_custom_keys.return_value = (None, 0, 0)
        with patch(
            "agent.credential_pool.get_custom_provider_pool_key",
            return_value=None,
        ):
            recover_with_credential_pool(
                agent,
                status_code=429,
                has_retried_429=False,
                classified_reason=FailoverReason.rate_limit,
            )
        assert pool.mark_custom_429_and_rotate.called

    def test_custom_pool_does_not_seed_model_config_duplicate_of_primary_key(self, monkeypatch):
        """The model config mirrors the selected custom provider's primary key.

        It must not occupy a rotation slot: after the primary fails, the next
        selected credential has to be a user-supplied backup, not the same key.
        """
        from agent import credential_pool as pool_module
        from agent.credential_pool import PooledCredential

        primary_key = "primary-key"
        monkeypatch.setattr(
            pool_module,
            "_get_custom_provider_config",
            lambda _pool_key: {
                "name": "Qwerty-9",
                "base_url": "https://api.example.test/v1",
                "api_key": primary_key,
            },
        )
        monkeypatch.setattr(
            pool_module,
            "_load_config_safe",
            lambda: {
                "model": {
                    "provider": "custom",
                    "base_url": "https://api.example.test/v1",
                    "api_key": primary_key,
                }
            },
        )
        monkeypatch.setattr(
            pool_module,
            "get_custom_provider_pool_key",
            lambda *_args, **_kwargs: "custom:qwerty-9",
        )
        entries = [
            PooledCredential.from_dict(
                "custom:qwerty-9",
                {
                    "id": "backup",
                    "source": "manual",
                    "auth_type": "api_key",
                    "access_token": "backup-key",
                    "base_url": "https://api.example.test/v1",
                },
            )
        ]

        pool_module._seed_custom_pool("custom:qwerty-9", entries)

        assert [entry.source for entry in entries] == ["manual", "config:Qwerty-9"]

    def test_unrelated_custom_pool_still_guarded(self):
        """agent=custom pointed at a DIFFERENT endpoint than the pool's
        custom provider must still skip pool mutation."""
        agent, pool = _agent(
            "custom", "https://other-endpoint.example/v1", "custom:fireworks"
        )
        with patch(
            "agent.credential_pool.get_custom_provider_pool_key",
            return_value="custom:other",
        ):
            recovered, _ = recover_with_credential_pool(
                agent,
                status_code=401,
                has_retried_429=False,
                classified_reason=FailoverReason.auth,
            )
        assert recovered is False
        assert not pool.method_calls

    def test_fallback_provider_still_guarded(self):
        """Original #33088/#33163 contract: when a fallback provider is
        active (agent.provider != pool.provider, non-custom), the pool is
        never mutated."""
        agent, pool = _agent("openai-codex", "https://chatgpt.com/backend-api", "custom:fireworks")
        recovered, _ = recover_with_credential_pool(
            agent,
            status_code=401,
            has_retried_429=False,
            classified_reason=FailoverReason.auth,
        )
        assert recovered is False
        assert not pool.method_calls

    def test_plain_provider_mismatch_still_guarded(self):
        agent, pool = _agent("openrouter", "https://openrouter.ai/api/v1", "anthropic")
        recovered, _ = recover_with_credential_pool(
            agent,
            status_code=429,
            has_retried_429=False,
            classified_reason=FailoverReason.rate_limit,
        )
        assert recovered is False
        assert not pool.method_calls
