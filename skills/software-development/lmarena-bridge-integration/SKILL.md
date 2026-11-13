---
name: lmarena-bridge-integration
description: >
  Reverse-engineer LMArena (arena.ai) internal API and build bridges/wrappers
  around it — Hikka userbot modules, OpenAI-compatible proxies, Telegram bots.
  Covers the SSE streaming protocol, auth-token lifecycle, reCAPTCHA v3 minting,
  Cloudflare/Turnstile pass, transport fallback chain, and conversation
  retry/followup endpoints. Load when working with LMArena internals or porting
  CloudWaddie/LMArenaBridge functionality into a new front-end.
tags:
  - lmarena
  - arena.ai
  - reverse-engineering
  - sse
  - recaptcha
  - cloudflare
  - turnstile
  - hikka
  - userbot
  - openai-compatible
---

# LMArena Bridge Integration

## When to load

- User asks to wrap/bridge LMArena (`arena.ai`) models into a Telegram bot, Hikka module, CLI, or OpenAI-compatible API.
- User references `LMArenaBridge` (CloudWaddie's project) or wants to port its features elsewhere.
- User wants to understand or reimplement LMArena's internal streaming protocol.
- Debugging `mint_service`, reCAPTCHA token minting, or Cloudflare/Turnstile issues with arena.ai.

## Architecture overview

LMArena (`arena.ai`) is a Next.js app behind Cloudflare with reCAPTCHA Enterprise v3 protection. The internal API speaks Server-Sent Events (SSE) with a custom chunk-prefix protocol. A bridge/wrapper must handle four independent challenges:

1. **Auth** — `arena-auth-prod-v1` cookie (base64-encoded Supabase session JSON), plus Cloudflare cookies (`cf_clearance`, `__cf_bm`, `_cfuvid`).
2. **reCAPTCHA v3** — each request payload carries a `recaptchaV3Token` field. Tokens expire in ~110–120 seconds. Mint via browser automation (Playwright Chrome or Camoufox) executing `grecaptcha.enterprise.execute(sitekey, {action})` in-page.
3. **Cloudflare/Turnstile** — the homepage may show a "Just a moment…" interstitial with a Turnstile widget. Must click it before grecaptcha loads.
4. **SSE parsing** — the `/nextjs-api/stream/create-evaluation` endpoint emits chunked lines prefixed with `a0:`, `ag:`, `ac:`, `ad:`, `a2:`, `a3:` (see Protocol section below).

## Key endpoints

| Purpose | Method | URL |
|---|---|---|
| New conversation | POST | `https://arena.ai/nextjs-api/stream/create-evaluation` |
| Follow-up message in existing conversation | POST | `https://arena.ai/nextjs-api/stream/post-to-evaluation/{conversation_id}` |
| Retry a specific message | PUT | `https://arena.ai/nextjs-api/stream/retry-evaluation-session-message/{sessionId}/messages/{messageId}` |
| Anonymous signup | POST | `https://arena.ai/nextjs-api/sign-up` |
| Scrape page for models + sitekey | GET | `https://arena.ai/` |

## Auth token lifecycle

- The `arena-auth-prod-v1` cookie is typically `base64-<json>` containing `{access_token, refresh_token, expires_at, ...}` — a Supabase session payload.
- Google OAuth sessions may split the cookie into `arena-auth-prod-v1.0` and `arena-auth-prod-v1.1` due to size limits. **Combine** them: `value = .0 + .1`.
- **Round-robin** across multiple tokens for rate-limit distribution.
- **Refresh strategies** (in order):
  1. LMArena HTTP Set-Cookie: GET `https://arena.ai/` with the expired `arena-auth-prod-v1` cookie; the server may return a fresh one via `Set-Cookie`.
  2. Supabase `/token?grant_type=refresh_token` using the `refresh_token` embedded in the session JSON and the Supabase anon key (discovered from page JS bundles — look for JWTs with `{"role":"anon"}` in the payload).
- Token validity check: decode the base64 session, check `expires_at`; fall back to decoding the JWT `access_token`'s `exp` claim.

## reCAPTCHA v3 minting

- Default sitekey: `6Led_uYrAAAAAKjPDIF58fgFtX3t8loNAK85bW9I` (may change — scrape from page JS or HTML via regex `recaptcha/(?:enterprise|api)\.js\?render=([0-9A-Za-z_-]{8,200})`).
- Default action: `chat_submit` (when authed) or `sign_up` (anonymous).
- **Mint process** (Playwright):
  1. Launch Chrome (headful for better score) or Camoufox (Firefox anti-fingerprint, `main_world_eval=True`).
  2. Navigate to `https://arena.ai/?mode=direct`, wait for `domcontentloaded`.
  3. If page title contains "Just a moment" → click Turnstile (see next section).
  4. Humanize the page: `page.mouse.move(100, 100)`, `page.mouse.wheel(0, 200)`, sleep ~2s.
  5. Wait for `window.grecaptcha` to be available (inject reCAPTCHA Enterprise script if missing).
  6. Execute: `grecaptcha.enterprise.execute(sitekey, {action})` → returns token string.
- **Firefox/Camoufox Xray-wrapper workaround**: use `window.wrappedJSObject || window` to access the real `grecaptcha` in the main world. Build params with `new w.Object()` in the page compartment.
- Token cache TTL: ~110 seconds (reCAPTCHA v3 tokens last ~120s, refresh 10s before expiry).
- For **strict Chrome-fetch models** (e.g., `gemini-3-pro-grounding`, `gemini-exp-1206`), mint the token inside the in-page fetch transport rather than using a cached token — cached tokens cause 403s.

## Cloudflare/Turnstile pass

- Detection: `page.title()` contains `"Just a moment"`.
- Selectors to try (in order):
  ```
  #lm-bridge-turnstile
  #lm-bridge-turnstile iframe
  #cf-turnstile
  iframe[src*="challenges.cloudflare.com"]
  [style*="display: grid"] iframe
  ```
- For iframe elements: get `content_frame()`, then look for `input[type='checkbox']`, `div[role='checkbox']`, `label` inside the frame.
- Click with `force=True` (the bounding box may return 0,0 when the window is hidden/minimized).
- After clicking, sleep 2s and re-check the title.
- Max ~15 attempts (30s total budget).

## SSE protocol (the critical part)

The `/nextjs-api/stream/*` endpoints emit SSE lines. After stripping any `data:` prefix, lines are classified by their 3-char prefix:

| Prefix | Meaning | Payload format | Stream-action |
|---|---|---|---|
| `a0:` | Text content chunk | JSON string (e.g., `a0:"Hello "`) | append to response text |
| `ag:` | Reasoning/thinking chunk | JSON string | append to reasoning text |
| `ac:` | Citation/tool-call chunk | JSON object, may contain `argsTextDelta` with `source` | collect citations |
| `ad:` | Metadata (finish) | JSON object with `finishReason` | end of stream |
| `a2:` | Image generation result | JSON array `[{type:"image", image:"url"}]` | format as markdown `![](url)` |
| `a3:` | Error message | JSON string | surface the error |
| `{...}` | OpenAI-style JSON chunk (some transports) | JSON object with `choices[0].delta` | extract delta content |

Parsing each chunk: `json.loads(line[3:])` for prefixed lines. The payload is a JSON-encoded string, so the result is a Python `str`.

If the stream produces **no `a0:` content deltas** at all (empty `response_text`), treat it as an upstream failure — retry with a fresh reCAPTCHA token or different transport.

## Transport fallback chain

1. **Direct httpx** — `httpx.AsyncClient` with headers from `get_request_headers_with_token()`. Default for most models.
2. **Chrome fetch** (Playwright real Chrome/Edge) — for `STRICT_BROWSER_FETCH_MODELS` and when reCAPTCHA v3 is needed in-page. Uses `page.expose_binding("reportChunk", ...)` to stream SSE lines back to Python.
3. **Camoufox fetch** (Firefox anti-fingerprint) — fallback when Chrome is blocked or fails 2+ times. Uses `main_world_eval=True`.
4. **Userscript proxy** — long-poll mechanism where a browser userscript does the actual fetch. Used when no auth token is configured.

Fallback logic: after 2+ consecutive Chrome reCAPTCHA failures → switch to Camoufox. After 2+ Camoufox failures → switch back to Chrome.

## UUIDv7 generation

LMArena uses UUIDv7 for session/message IDs. Implementation (Unix epoch milliseconds):

```python
def uuid7():
    timestamp_ms = int(time.time() * 1000)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    uuid_int = timestamp_ms << 80
    uuid_int |= (0x7000 | rand_a) << 64
    uuid_int |= (0x8000000000000000 | rand_b)
    hex_str = f"{uuid_int:032x}"
    return f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
```

## Request payload structure

### New conversation (create-evaluation)
```json
{
  "id": "<uuid7 session_id>",
  "mode": "direct",
  "modelAId": "<model_id>",
  "userMessageId": "<uuid7>",
  "modelAMessageId": "<uuid7>",
  "modelBMessageId": "<uuid7>",
  "userMessage": {
    "content": "<prompt text>",
    "experimental_attachments": [],
    "metadata": {}
  },
  "modality": "chat|search|image",
  "recaptchaV3Token": "<token>"
}
```

### Follow-up (post-to-evaluation)
Same structure, but:
- `id` is the **existing** `conversation_id`
- No `mode` field
- URL: `https://arena.ai/nextjs-api/stream/post-to-evaluation/{conversation_id}`

### Retry
- `PUT` to `https://arena.ai/nextjs-api/stream/retry-evaluation-session-message/{sessionId}/messages/{messageId}`
- Empty payload `{}`

## Modality selection

Based on model capabilities:
- `outputCapabilities.image` → `"image"`
- `outputCapabilities.search` → `"search"`
- else → `"chat"`

## Model discovery

Scrape `https://arena.ai/` HTML. Regex:
```python
re.search(r'\\"initialModels\\":(\[.*?\]),\\"initialModel[A-Z]Id', body, re.DOTALL)
```
Then `json.loads(match.group(1).encode().decode("unicode_escape"))`.

Each model has: `id`, `publicName`, `organization`, `capabilities`, `rankByModality`, `userSelectable`.

**Stealth models** (no `organization`) are not accessible via the public API.

## Pitfalls

- **Split cookies**: `arena-auth-prod-v1.0` + `arena-auth-prod-v1.1` must be concatenated. If you only read `arena-auth-prod-v1`, you'll miss Google OAuth sessions.
- **Cached reCAPTCHA tokens cause 403s** for strict Chrome-fetch models. Pass empty string and let the in-page transport mint fresh.
- **Execution context destroyed**: SPA navigation can destroy the page's JS context mid-evaluate. Use `safe_page_evaluate()` with retries — wait for `domcontentloaded` between attempts.
- **`networkidle` wait hangs** behind Cloudflare. Use `domcontentloaded` as the primary wait state, `networkidle` only as a secondary best-effort.
- **Cloudflare `cf_clearance` expires** (~30 min). If requests start returning 403 with `cf-chl-bypass` errors, re-scrape the page for fresh cookies.
- **Cookie domain scoping**: use `.arena.ai` for domain-level cookies (Cloudflare), but the auth cookie may be set on `arena.ai` (host-only). Set both variants to be safe.
- **Systemd mint_service memory**: cap at ~350 MB with `MemoryMax=350M`. Chromium + Playwright leaks over time; use `Restart=always`.
- **SSE keep-alives**: when streaming to a client (e.g., Telegram), send periodic `": keep-alive\n\n"` or equivalent to prevent connection timeouts while waiting for upstream tokens.

## References

See `references/lmarena-protocol-details.md` for the full protocol reference extracted from CloudWaddie/LMArenaBridge source code — SSE chunk formats, auth decode functions, reCAPTCHA mint JS, Turnstile selectors, and transport internals.
