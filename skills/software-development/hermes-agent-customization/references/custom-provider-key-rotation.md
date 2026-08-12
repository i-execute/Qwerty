# Custom OpenAI-Compatible Provider: API-Key Rotation

Use this when a Hermes `custom_providers` endpoint needs a primary API key plus backup keys that rotate after quota/auth/provider failures.

## Expected live shape

- Custom provider has a stable name, URL, and primary key in `config.yaml`.
- The active model resolves to the same endpoint with `model.provider: custom`.
- Credential pool key is `custom:<normalized-provider-name>`.
- Exactly one pool entry represents the primary key (`source: config:<name>`); backups are `source: manual`.
- Count *unique secret values*, not only rows. A duplicated primary key creates a false backup slot and repeats a failed request.

## Verification sequence

1. Read the custom provider and active model configuration without printing secrets.
2. Load the exact custom pool using `get_custom_provider_pool_key(base_url, provider_name=name)` and `load_pool(pool_key)`.
3. Report entries with label, source, priority, status, availability, and a non-reversible fingerprint only.
4. Confirm that every entry has a runtime key and that all secret fingerprints are unique.
5. Test `mark_exhausted_and_rotate()` on an in-memory two-entry pool with persistence disabled; assert a simulated 429 moves from primary to backup and marks the issuing key exhausted.
6. Run focused regression tests for custom-pool matching and credential rotation.
7. Inspect the live gateway unit/process and logs. A running gateway needs a restart after Python source changes; do not claim runtime validation until it has actually restarted.

## Important implementation rule

`model.api_key` often mirrors `custom_providers[].api_key`. During custom-pool seeding, do **not** add a separate `model_config` entry when its secret equals the named provider's primary key. Preserve a `model_config` entry only when it is genuinely different.

## Test runner pitfall

The project virtualenv may include pytest but not xdist. Use the focused command without `-n` unless xdist is confirmed:

```bash
./venv/bin/python -m pytest -q tests/agent/test_custom_pool_mismatch_guard.py tests/run_agent/test_credential_pool_interrupt.py
```

Do not expose raw API keys in commands, logs, reports, or commits.
