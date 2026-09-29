# Langfuse Observability Plugin

This plugin ships bundled with Qwerty but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

Pick one:

```bash
# Interactive: walks you through credentials + SDK install + enable
qwerty tools  # → Langfuse Observability

# Manual
pip install langfuse
qwerty plugins enable observability/langfuse
```

## Required credentials

Set these in `~/.qwerty/.env` (or via `qwerty tools`):

```bash
QWERTY_LANGFUSE_PUBLIC_KEY=pk-lf-...
QWERTY_LANGFUSE_SECRET_KEY=sk-lf-...
QWERTY_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
qwerty plugins list                 # observability/langfuse should show "enabled"
qwerty chat -q "hello"              # then check Langfuse for a "Qwerty turn" trace
```

## Optional tuning

```bash
QWERTY_LANGFUSE_ENV=production       # environment tag
QWERTY_LANGFUSE_RELEASE=v1.0.0       # release tag
QWERTY_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
QWERTY_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
QWERTY_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
qwerty plugins disable observability/langfuse
```
