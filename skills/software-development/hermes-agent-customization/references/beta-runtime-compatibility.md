# Beta Runtime Compatibility

Use this reference when a Hermes beta branch produces a generic gateway error after a commit touching credential pools, agent initialization, or recovery.

## Diagnostic sequence

1. Inspect the live logs before changing code:
   ```bash
   journalctl --user -u hermes-gateway.service --since '2 hours ago' --no-pager
   grep -n -E '(Traceback|ImportError|ERROR|RateLimit|credential pool|rotat)' \
     "${HERMES_HOME:-$HOME/.hermes}"/logs/{errors,agent,gateway}.log
   ```
2. Confirm the running source checkout and branch:
   ```bash
   systemctl --user show hermes-gateway.service -p MainPID -p ExecStart -p WorkingDirectory
   readlink -f /proc/$(systemctl --user show -p MainPID --value hermes-gateway.service)/cwd
   git -C <checkout> status --short --branch
   ```
3. Compare the beta commit against its parent/main and search all references before removing a symbol:
   ```bash
   git grep -n 'symbol_name'
   git log -S'symbol_name' --all --oneline -- <relevant-files>
   ```

## Compatibility invariant

A commit that removes a helper or method is incomplete if the same branch still imports or calls it. This can evade static checks when the import occurs only during dynamic gateway agent construction. For every moved/removed symbol:

- search the whole tree for imports and calls;
- either migrate every caller in the same commit or restore a compatibility implementation;
- add a minimal import smoke test or real initialization test;
- run `python -m py_compile` and focused tests.

For credential attribution, keep both sides of the contract aligned:

- `agent.agent_runtime_helpers.sync_credential_pool_entry_id(agent)`;
- `CredentialPool.entry_id_for_api_key(api_key_hint)`.

The helper should tolerate an absent pool and clear the agent field on lookup failure rather than preventing agent construction.

## Interpreting a 429 with a key pool

A rotating pool can successfully select another key while the upstream service still returns HTTP 429. Check the provider's quota scope: a free-account or endpoint-wide limit may apply across all keys. Treat the log as evidence of both events separately:

- `marking <key> exhausted` / `rotated to API key <n>` proves local rotation;
- a repeated provider 429 proves the upstream quota is broader than one key, or the provider rejected the request for another shared limit.

Do not claim that a pool bypasses a provider-wide quota without a live provider-specific test.

## Push verification

Never report a push as successful from the local commit alone. After pushing, fetch the target branch and compare SHAs:

```bash
git fetch origin beta
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/beta)"
```

If HTTPS authentication is unavailable, report the exact blocker and leave the verified local commit intact. Do not put tokens into remote URLs or logs.
