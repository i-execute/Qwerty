# Custom-provider 429 rotation reference

## Behavioral contract

- `hermes model` asks `Use API-key rotation? [y/N]` immediately after the custom endpoint URL.
- `N` keeps one primary key in normal config.
- `Y` collects the primary plus all additional keys in one setup pass; an empty additional key ends collection.
- The primary config key must not become a second pool candidate when `model.api_key` mirrors `custom_providers[].api_key`.
- A custom-pool key receiving HTTP 429 enters a 65-second cooldown and the gateway immediately selects the next key.
- Once the cooled key is retried and returns 429 again, it is treated as quota-exhausted for the current rotation cycle.
- When rotation wraps, probe every key against the selected model with a minimal `hi` chat completion. Emit live/dead/total counts; only after the complete probe reports no live keys emit the final return-tomorrow message.

## Verification recipe

From a clean checkout with dependencies available:

```bash
uv run --extra dev pytest -q \
  tests/agent/test_custom_two_slot_rotation.py \
  tests/agent/test_custom_pool_mismatch_guard.py \
  tests/hermes_cli/test_custom_provider_model_switch.py
python -m compileall -q agent/credential_pool.py agent/agent_runtime_helpers.py hermes_cli/model_setup_flows.py
git diff --check
```

The focused regression suite should cover wizard input ordering, duplicate-key suppression, cooldown/exhaustion transitions, ring wrap-around, probe counts, and user-visible quota messages.

## Push recovery

If the original checkout is shallow or GitHub rejects the push with `remote unpack failed` / `did not receive expected object`, create a fresh clone of the target fork in `/home/forget/QwertyWork`, copy only verified source and tests, rerun the focused suite, commit, force-push, and verify `origin/beta` resolves to the new commit SHA. Do not repeatedly retry the broken object graph.
