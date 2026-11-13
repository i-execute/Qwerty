# LMArena Internal Protocol — Reference Details

Extracted from CloudWaddie/LMArenaBridge source (auth.py, recaptcha.py, transport.py, main.py, constants.py, browser_utils.py) and user's Hikka module LMArena.py.

---

## SSE chunk format (complete)

Each line from `/nextjs-api/stream/create-evaluation` (and followup/retry variants) is an SSE line. Strip `data:` prefix if present, then classify by 3-char prefix:

| Prefix | Decode | Semantics |
|---|---|---|
| `a0:` | `json.loads(line[3:])` → `str` | Text content delta. Append to accumulating response text. |
| `ag:` | `json.loads(line[3:])` → `str` | Reasoning/thinking delta. Append to reasoning buffer. |
| `ac:` | `json.loads(line[3:])` → `dict` | Citation/tool-call. Key `argsTextDelta` contains a JSON-encoded string with `source` (dict or list of dicts). Collect into citations list. |
| `ad:` | `json.loads(line[3:])` → `dict` | Metadata. Key `finishReason` (usually `"stop"`) signals end of stream. |
| `a2:` | `json.loads(line[3:])` → `list` | Image generation result. `[{type:"image", image:"<url>"}]`. Format as markdown `![Generated Image](url)`. |
| `a3:` | `json.loads(line[3:])` → `str` | Error message. Surface to user. |
| `{...}` | `json.loads(line)` → `dict` | Standard OpenAI-style chunk (some transports). `choices[0].delta.content` or `.reasoning_content`. |

If **none** of these prefixes match, the line is "unhandled". If the first few unhandled lines parse as JSON with an `error` key, that's the upstream error body (e.g., `{"error":"recaptcha validation failed"}`).

---

## Auth token decode

### base64 session format

```python
def decode_arena_auth_session_token(token: str) -> dict | None:
    if not token.startswith("base64-"):
        return None
    b64 = token[len("base64-"):]
    b64 += "=" * ((4 - len(b64) % 4) % 4)  # pad
    raw = base64.b64decode(b64.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))  # {access_token, refresh_token, expires_at, ...}
```

### Split cookie combine

```python
def combine_split_cookies(cookies: list[dict]) -> str | None:
    parts = {}
    for c in cookies:
        name = c.get("name", "")
        if name == "arena-auth-prod-v1.0":
            parts[0] = c.get("value", "")
        elif name == "arena-auth-prod-v1.1":
            parts[1] = c.get("value", "")
    if 0 in parts and 1 in parts:
        return (parts[0] + parts[1]).strip()
    return parts.get(0)
```

### Expiry check

```python
def get_token_expiry(token: str) -> int | None:
    session = decode_arena_auth_session_token(token)
    if session and session.get("expires_at"):
        return int(session["expires_at"])
    # Fallback: decode JWT access_token exp claim
    access = session.get("access_token", "") if session else token
    if access.count(".") >= 2:
        payload_b64 = access.split(".")[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return int(payload.get("exp")) if payload.get("exp") else None
    return None

def is_expired(token: str, skew: int = 30) -> bool:
    exp = get_token_expiry(token)
    if exp is None:
        return False  # unknown format → don't assume expired
    return time.time() >= (exp - skew)
```

### Supabase anon key extraction

From JS bundles, find JWT-like strings and check payload for `{"role":"anon"}`:

```python
SUPABASE_JWT_RE = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")

def extract_supabase_anon_key(text: str) -> str | None:
    for cand in SUPABASE_JWT_RE.findall(text):
        payload = json.loads(base64.urlsafe_b64decode(cand.split(".")[1] + "=="))
        if payload.get("role") == "anon":
            return cand
    return None
```

### Refresh via LMArena HTTP

```python
async def refresh_via_lmarena(old_token: str, cookies: dict, ua: str) -> str | None:
    cookies["arena-auth-prod-v1"] = old_token
    resp = await asyncio.to_thread(lambda: cloudscraper.create_scraper().get(
        "https://arena.ai/", cookies=cookies, timeout=30))
    for sc in resp.headers.get_list("set-cookie"):
        if sc.lower().startswith("arena-auth-prod-v1="):
            new_value = sc.split(";")[0].split("=", 1)[1].strip()
            if new_value and not is_expired(new_value, skew=0):
                return new_value
    return None
```

### Refresh via Supabase

```python
async def refresh_via_supabase(old_token: str, anon_key: str) -> str | None:
    session = decode_arena_auth_session_token(old_token)
    refresh_token = session.get("refresh_token")
    # Derive auth base URL from JWT iss claim
    payload = json.loads(base64.urlsafe_b64decode(
        session["access_token"].split(".")[1] + "=="))
    auth_base = payload["iss"].split("/auth/v1")[0] + "/auth/v1"

    resp = await httpx.AsyncClient().post(
        f"{auth_base}/token?grant_type=refresh_token",
        headers={"apikey": anon_key, "Authorization": f"Bearer {anon_key}"},
        json={"refresh_token": refresh_token}
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    # Merge new tokens into existing session, re-encode as base64-
    updated = {**session, **{k: data[k] for k in
        ("access_token","refresh_token","expires_in","expires_at") if k in data}}
    raw = json.dumps(updated, separators=(",",":")).encode()
    return "base64-" + base64.b64encode(raw).decode().rstrip("=")
```

---

## Request headers

```python
def get_headers(token: str, recaptcha_token: str = "", config: dict = None) -> dict:
    cookies = {
        "arena-auth-prod-v1": token,
        "cf_clearance": config.get("cf_clearance", ""),
        "__cf_bm": config.get("cf_bm", ""),
        "_cfuvid": config.get("cfuvid", ""),
        "provisional_user_id": config.get("provisional_user_id", ""),
    }
    headers = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items() if v),
        "Origin": "https://arena.ai",
        "Referer": "https://arena.ai/?mode=direct",
    }
    if config.get("user_agent"):
        headers["User-Agent"] = config["user_agent"]
    if recaptcha_token:
        headers["X-Recaptcha-Token"] = recaptcha_token
        headers["X-Recaptcha-Action"] = "chat_submit"  # or "sign_up" for anon
    return headers
```

Note: LMArena uses `text/plain;charset=UTF-8` for the Content-Type, NOT `application/json`. The body is still JSON-encoded.

---

## reCAPTCHA mint — full JS (Camoufox/Chrome)

```javascript
async () => {
    const w = window.wrappedJSObject || window;
    const sleep = (ms) => new Promise(r => setTimeout(r, ms));
    const pickG = () => {
        const ent = w?.grecaptcha?.enterprise;
        if (ent && typeof ent.execute === 'function') return ent;
        const g = w?.grecaptcha;
        if (g && typeof g.execute === 'function') return g;
        return null;
    };
    const g = pickG();
    if (!g) throw new Error('No grecaptcha found');
    // Wait for ready (with timeout)
    await Promise.race([
        new Promise(resolve => { try { g.ready(resolve); } catch(e) { resolve(true); } }),
        sleep(5000)
    ]);
    // Firefox Xray: build params in page compartment
    const params = new w.Object();
    params.action = '{recaptcha_action}';
    const token = await g.execute('{recaptcha_sitekey}', params);
    return String(token || '');
}
```

For **Chrome** (no Xray wrapper issue), simpler version works:
```javascript
({sitekey, action}) => new Promise((resolve, reject) => {
    const g = window.grecaptcha?.enterprise || window.grecaptcha;
    if (!g || typeof g.execute !== 'function') return reject('NO_GRECAPTCHA');
    g.execute(sitekey, { action }).then(resolve).catch(e => reject(String(e)));
})
```

### Stealth tweaks for Chrome
```javascript
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
```
Added via `context.add_init_script(...)`.

### Humanize (warm-up for better score)
```python
await page.mouse.move(100, 100)
await page.mouse.wheel(0, 200)
await asyncio.sleep(1)
await page.mouse.move(200, 300)
await page.mouse.wheel(0, 300)
await asyncio.sleep(3)
```

### reCAPTCHA script injection (if missing from page)
```javascript
const urls = [
    'https://www.google.com/recaptcha/enterprise.js?render=' + encodeURIComponent(sitekey),
    'https://www.google.com/recaptcha/api.js?render=' + encodeURIComponent(sitekey),
];
urls.forEach(u => {
    const s = document.createElement('script');
    s.src = u; s.async = true; s.defer = true;
    document.head.appendChild(s);
});
```

---

## Turnstile click (CloudWaddie's click_turnstile)

Selectors in order:
```
#lm-bridge-turnstile
#lm-bridge-turnstile iframe
#cf-turnstile
iframe[src*="challenges.cloudflare.com"]
[style*="display: grid"] iframe
```

For each element:
1. Try `element.content_frame()`. If frame exists, look inside for `input[type='checkbox']`, `div[role='checkbox']`, `label` → click with `force=True`.
2. If no frame, try `element.click(force=True)`.
3. If click fails, get `bounding_box()`, compute center, `page.mouse.click(x, y)`.

After any successful click: `await asyncio.sleep(2)`.

---

## Chrome fetch transport (in-page fetch via Playwright)

```javascript
async ({url, method, body, extraHeaders, timeoutMs}) => {
    const controller = new AbortController();
    setTimeout(() => controller.abort('timeout'), timeoutMs);
    const res = await fetch(url, {
        method, headers: {'content-type': 'text/plain;charset=UTF-8', ...extraHeaders},
        body, credentials: 'include', signal: controller.signal,
    });
    // Report status + headers via exposed binding
    await window.reportChunk(JSON.stringify({__type: 'meta', status: res.status, headers: {...}}));
    // Stream body lines
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
        const {value, done} = await reader.read();
        if (value) buffer += decoder.decode(value, {stream: true});
        if (done) buffer += decoder.decode();
        const parts = buffer.split(/\r?\n/);
        buffer = parts.pop() || '';
        for (const line of parts) {
            if (line.trim()) await window.reportChunk(line);
        }
        if (done) break;
    }
    return {__streaming: true};
}
```

Python side: `await page.expose_binding("reportChunk", callback)` where callback puts lines into an `asyncio.Queue`. Read meta first (status+headers), then content lines for SSE parsing.

---

## Constants

| Name | Value |
|---|---|
| `RECAPTCHA_SITEKEY` | `6Led_uYrAAAAAKjPDIF58fgFtX3t8loNAK85bW9I` |
| `RECAPTCHA_ACTION` (authed) | `chat_submit` |
| `RECAPTCHA_ACTION` (anon) | `sign_up` |
| `RECAPTCHA_V2_SITEKEY` | `6Ld7ePYrAAAAAB34ovoFoDau1fqCJ6IyOjFEQaMn` |
| `TURNSTILE_SITEKEY` | `0x4AAAAAAA65vWDmG-O_lPtT` |
| `ARENA_ORIGIN` | `https://arena.ai` |
| `LMARENA_ORIGIN` | `https://lmarena.ai` |
| `STREAM_PATH` | `/nextjs-api/stream/create-evaluation` |
| `SIGNUP_PATH` | `/nextjs-api/sign-up` |
| `RECAPTCHA_TOKEN_LIFETIME` | 115 seconds |
| `PERIODIC_REFRESH_INTERVAL` | 1800 seconds (30 min) |
| `TURNSTILE_MAX_ATTEMPTS` | 15 |
| `GRECAPTCHA_TIMEOUT_MS` | 60000 |
| `CLOUDFLARE_CHALLENGE_TITLE` | `Just a moment` |
| `STRICT_BROWSER_FETCH_MODELS` | `gemini-3-pro-grounding`, `gemini-exp-1206` |

---

## Dependencies (CloudWaddie's stack)

```
fastapi
uvicorn
camoufox        # Firefox anti-fingerprint browser
playwright      # Chrome automation
httpx           # async HTTP client
cloudscraper    # Cloudflare bypass for direct HTTP
python-multipart
```

For Hikka module (userbot), slim down to: `aiohttp` (or `httpx`) for direct HTTP, optional `playwright` for reCAPTCHA mint, optional subprocess to run LMArenaBridge as a separate service.
