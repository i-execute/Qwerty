# OBHOD Bot Development Patterns (from i-execute/OBHOD Session)

## Project Context

**Repository:** https://github.com/i-execute/OBHOD
**Branch:** `agent-fix` merged to `main`
**Purpose:** Telegram bot for WireGuard + VK Turn proxy management

## Key Fixes Applied

### 1. VK OAuth Redirect URI Fix

**Error:** `{"error":"invalid_request","error_description":"redirect_uri is incorrect, check application redirect uri in the settings page"}`

**Root Cause:** Using unofficial VK app ID `2685278` with `https://oauth.vk.com/blank.html` redirect URI not configured in VK app settings.

**Solution:** Use official VK Standalone App ID `3697615` (official VK mobile app) which allows `https://oauth.vk.com/blank.html` by default.

```python
# BOT/Modules/VKTurn.py
VK_DEFAULT_APP_ID = 3697615  # Official VK app - no redirect URI config needed
VK_REDIRECT = "https://oauth.vk.com/blank.html"
VK_DEFAULT_SCOPE = "offline"
VK_API_VERSION = "5.199"
```

### 2. Text-based VK Token Capture (Reverted from Inline)

**Problem:** Inline "Enter Token via Inline" button didn't work - user couldn't properly submit token through inline query.

**Solution:** Reverted to text-based capture using regex in `_on_text` handler (matching commit `75f8aba` which worked):

```python
# In VKTurn.py - _on_text handler
async def _on_text(self, event):
    # ...
    if pending["stage"] == "vk_auth":
        token = extract_vk_token(text)  # Regex: access_token=([A-Za-z0-9._-]+)
        if not token:
            return
        client = VKClient(token)
        uid = await client.whoami()
        if not uid:
            return
        # Save token, start call, show profiles...
```

### 3. Inline Query Title Fix

**Problem:** Inline query result showed the actual token/key in the title instead of "Tap for transfer value".

**Solution:** Always return fixed title in inline handler:

```python
# BOT/core.py - inline_handler
_pending_inline = {}

@bot.on(events.InlineQuery())
async def inline_handler(event):
    # ...
    _pending_inline[event.sender_id] = (prefix, method)
    builder = event.builder
    result = builder.article(
        title="Tap for transfer value",  # FIXED TITLE - never shows actual value
        text=value or " "
    )
    await event.answer([result])
    return

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.message.via_bot_id))
async def inline_result_handler(event):
    pending = _pending_inline.pop(event.sender_id, None)
    if not pending:
        return
    prefix, method = pending
    value = (event.raw_text or "").strip()  # Get actual value from message
    await method(event, value)
    try:
        await event.delete()  # Clean up via-bot message
    except Exception:
        pass
```

### 4. Ubuntu 24.04 ufw Conflict with iptables-persistent

**Error:** `ufw : Breaks: iptables-persistent but 1.0.20 is to be installed`

**Solution:** Remove ufw entirely, use iptables directly:

```bash
# Storage/VKTurn/setup_root.sh
apt update -qq && apt install -y wireguard wireguard-tools qrencode iptables-persistent jq python3
# NO ufw package

# Open WireGuard port via iptables (persisted by netfilter-persistent)
iptables -C INPUT -p udp --dport 51820 -j ACCEPT 2>/dev/null || \
    iptables -A INPUT -p udp --dport 51820 -j ACCEPT
netfilter-persistent save
```

**In ensure_profile.sh:** Remove `ufw allow "$PORT"/tcp` and `ufw allow "$PORT"/udp` lines.

### 5. OWNER_ID Setup Timing Fix

**Problem:** OWNER_ID not requested during first-run setup, causing bot to fail.

**Solution:** Move OWNER_ID prompt inside the `if [ ! -f "$ENV_FILE" ]` block, immediately after bot token validation:

```bash
# Storage/Installation/Setuper.sh
if [ ! -f "$ENV_FILE" ]; then
    read -rp "BOT_TOKEN: " BOT_TOKEN < /dev/tty
    # ... validate token, check inline mode ...

    echo "BOT_TOKEN=$BOT_TOKEN" > "$ENV_FILE"
    chown "$OBHOD_USER:$OBHOD_USER" "$ENV_FILE"
    chmod 600 "$ENV_FILE"

    echo "connected to @$USERNAME successfully"
    echo "message it now in DM with anything to learn your id"

    # Request OWNER_ID IMMEDIATELY after bot connection
    read -rp "Enter your id (from the bot's reply): " OWNER_ID < /dev/tty
    if ! [[ "$OWNER_ID" =~ ^[0-9]+$ ]]; then
        echo "invalid id"
        exit 1
    fi
    echo "OWNER_ID=$OWNER_ID" >> "$ENV_FILE"
    chown "$OBHOD_USER:$OBHOD_USER" "$ENV_FILE"
fi

# THEN set up systemd service
UNIT_DIR="/home/$OBHOD_USER/.config/systemd/user"
# ... create service, enable, start
```

### 6. WireGuard Wrap Key Path Centralization

**Problem:** `wrapKeyHex` empty in iOS links due to hardcoded path `/etc/wireguard/wrap.key` that might not exist.

**Solution:** Centralized constant and read function:

```python
# BOT/Modules/VKTurn.py
WRAP_KEY_FILE = "/etc/wireguard/wrap.key"

def _read_wrap_key(self) -> str:
    try:
        with open(WRAP_KEY_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

# In peer creation:
obf_key = self._read_wrap_key()
if is_android:
    link = build_android_link(tag, peer, SERVER_HOST, port, profile, obf_key, call_id)
else:
    link = build_ios_link(peer, join_link, obf_key)  # wrapKeyHex now populated
```

### 7. Systemd Unit Fix in ensure_profile.sh

**Problem:** Missing `WantedBy=multi-user.target` in systemd unit.

**Fix:**
```bash
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=VK Turn Proxy (profile $PROFILE)
After=network.target wg-quick@wg0.service

[Service]
Type=simple
User=OBHOD
WorkingDirectory=$VKTURN_HOME
ExecStart=$VKTURN_HOME/server -listen 0.0.0.0:$PORT -connect 127.0.0.1:51820 $EXEC_FLAGS
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 8. Echo-ID Mode Robustness (Bot Not Replying After Token Setup)

**Problem:** After entering BOT_TOKEN in `Setuper.sh`, the bot would not reply with the user's ID. Old `run_echo_id_mode` had no timeout, no error handling, and would consume stale queued updates as if they were the installer's `/start`.

**Solution (in `BOT/core.py`):**

```python
async def run_echo_id_mode(token):
    api = BotAPI(token)
    await api.start()

    # Flush stale getUpdates so only replies to THIS /start are seen
    stale = await api.call("getUpdates", offset=-1, timeout=0)
    if stale.get("result"):
        api.offset = stale["result"][-1]["update_id"] + 1

    while True:
        try:
            updates = await api.get_updates()
        except Exception as e:
            await asyncio.sleep(3)
            continue
        for u in updates:
            msg = u.get("message")
            if not msg:
                continue
            chat_id = msg.get("chat", {}).get("id")
            sender = msg.get("from") or msg.get("sender_chat") or {}
            sender_id = sender.get("id")
            if chat_id is None or sender_id is None:
                continue
            await api.send_message(chat_id, str(sender_id), parse_mode=None)
```

Also: `BotAPI.start()` must use `aiohttp.ClientTimeout(total=60, connect=10)` to prevent hangs.

### 9. Android freeturn:// Link — Full Spec + Common Bugs

**See:** `references/obhod-android-freeturn-uri.md` for the complete authoritative spec
(reverse-engineered from `FreeturnLink.kt` parser + `docs/uri.md`).

**Critical bugs fixed this session:**
- `cid` was generated but **never registered** in `clients.json` → Android clients
  silently failed authentication. Fix: new `add_client.sh` script called via sudo.
- `peer` fell back to `127.0.0.1:9000` when server IP detection failed → Android
  clients connected to themselves. Fix: emit empty `peer` (parser rejects visibly).
- WireGuard config was sent as **separate text** instead of embedded in `wg` field.
  The Android app's `FreeturnLink.kt` parser reads `wg` directly from payload —
  embedding it lets the app import atomically, no WG app step.
- Added `name` field (peer tag) for client identification in the allowlist.

### 10. Duplicate Peer-Created Message Dedup

**Problem:** Bot sent the peer-created link message twice to the owner: once via
`event.reply(message)` and again via `notify_admins(self.bot, message)` (which
loops over `[owner_id] + admins`).

**Fix:** `notify_admins` now accepts `exclude=` param to skip the sender:
```python
async def notify_admins(self, bot, message, exclude=None):
    for user_id in [self.owner_id] + self.get_admins():
        if exclude is not None and user_id == exclude:
            continue
        await bot.send_message(user_id, message, parse_mode="html")
```
Caller: `await self.data_manager.notify_admins(self.bot, message, exclude=sender_id)`.

### 11. Rich HTML Formatting for Bot Messages (Telethon)

**Pattern** for `event.reply` with HTML parse_mode in Telethon (non-rich-message bots):

```python
import html as _html_mod

esc_tag = _html_mod.escape(tag)
esc_link = _html_mod.escape(link_line)

message = (
    f"<b>✅ {self.strings['peer_created']}</b>\n\n"
    f"<blockquote><b>Tag</b>: <code>{esc_tag}</code>\n"
    f"<b>IP</b>: <code>{peer['IP']}</code>\n"
    f"<b>Profile</b>: <code>{profile}</code>\n"
    f"<b>Platform</b>: <code>{platform}</code></blockquote>\n\n"
    f"<blockquote>{esc_link}</blockquote>"
)
await event.reply(message, parse_mode="html")
```

**Pitfalls:**
- Always `html.escape()` dynamic values (tags, IPs, link strings) — the
  freeturn:// link contains `://` and base64 which are safe but `join_link`
  contains `&` and `=` which break HTML.
- `<blockquote>` renders as a Telegram native quote block — works in Telethon
  with `parse_mode="html"` (not just in Bot API 10.1 Rich Messages).
- `<code>` renders as monospace inline — good for IPs, tags, short values.
- Use `<pre><code>` for multi-line blocks (WireGuard configs, freeturn links).

## Related Files

| File | Changes |
|------|---------|
| `BOT/Modules/VKTurn.py` | VK app ID, token capture, wrap key, Android link fix, HTML formatting, dedup |
| `BOT/core.py` | Inline query title, echo-id robustness, `notify_admins(exclude=)`, `aiohttp.ClientTimeout` |
| `Storage/Installation/Setuper.sh` | OWNER_ID timing, ufw removed, sudo-rs one-per-line fallback for `add_client.sh`, log hint |
| `Storage/VKTurn/setup_root.sh` | No ufw, iptables for WG port, copies `add_client.sh` to `/opt/vkturn/`, sudoers updated |
| `Storage/VKTurn/ensure_profile.sh` | No ufw, fixed systemd unit, iptables for proxy port |
| `Storage/VKTurn/add_peer_*.sh` | Peer management scripts (iOS + Android) |
| `Storage/VKTurn/add_client.sh` | **NEW** — registers `cid` in `clients.json` allowlist |
| `Storage/VKTurn/revoke_peer.sh` | Also removes matching `cid` from `clients.json` by `comment==tag` |

## See Also

- `references/obhod-android-freeturn-uri.md` — complete freeturn:// URI spec + Android parser reference

---

*Updated 2026-07-24: added echo-id robustness, Android freeturn:// link repair, dedup, HTML formatting.*

---

### 12. `parse_mode=None` Causes 400 Error (Session 2026-07-27)

**Problem:** `BotAPI.send_message(chat_id, text, parse_mode=None)` sends
`"parse_mode": null` in JSON → Telegram returns `400: unsupported parse_mode`.

**Root cause:** `aiohttp` serializes Python `None` to JSON `null`. Telegram Bot API
rejects `null` for `parse_mode` — it expects either a valid mode string or the
field to be absent entirely.

**Fix:** Only include `parse_mode` in params if it's truthy:

```python
async def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML"):
    params = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_markup:
        params["reply_markup"] = reply_markup
    return await self.call("sendMessage", **params)
```

Same fix for `edit_message`.

**Testing method:** `curl` with `"parse_mode": null` → works (curl sends raw string).
`aiohttp` with `parse_mode: None` → 400. The difference is JSON serialization.
Verified: omitting `parse_mode` entirely or using `""` (empty string) both work.

### 13. Inline Mode Check After API_ID, Not in Setuper.sh (Session 2026-07-27)

**Problem:** Setuper.sh checked `supports_inline_queries` via `getMe` during
installation and did `exit 1` if inline was off. This blocked ALL bot
functionality (including echo-id mode which doesn't need inline) when the user
hadn't enabled inline mode in BotFather yet.

**Fix:** Move the inline check to AFTER API_ID is entered in `run_setup_wizard`
(core.py), and make Setuper.sh only warn:

```bash
# Setuper.sh — warn only, don't exit
if [ "$INLINE_SUPPORTED" != "true" ]; then
    echo "⚠️  Inline mode is OFF for @$USERNAME"
    echo "   Enable it later via @BotFather -> /setinline"
    # NO exit 1 — bot can still run echo-id and setup wizard
fi
```

```python
# core.py run_setup_wizard — after API_ID is saved
if state["stage"] == "api_id" and API_ID_RE.match(text):
    state["api_id"] = text
    state["stage"] = "api_hash"
    me = await get_bot_username(token)
    inline_ok = me.get("supports_inline_queries", False) if me else False
    if not inline_ok:
        # Send warning with retry button
        kb = {"inline_keyboard": [[
            {"text": "I enabled it, check again",
             "callback_data": "retry_inline_check",
             "style": "primary"}
        ]]}
        await api.send_message(owner_id,
            "⚠️ <b>Inline mode is OFF</b>\n\n"
            "Go to <b>@BotFather</b> → /setinline → @"
            f"{me.get('username','')} to enable.\n\n"
            "When done, tap the button below 👇",
            parse_mode="HTML", reply_markup=kb)
        state["stage"] = "wait_inline"
    else:
        # Proceed normally with API_HASH inline button
        ...
```

The `retry_inline_check` callback re-checks `getMe.supports_inline_queries`.
If enabled, it swaps the message to the API_HASH inline input button.

### 14. ALL Buttons Must Have `style=` Attribute (Session 2026-07-27)

**User requirement:** Every button in the bot must be colored — no plain
grey/default buttons anywhere.

**Telethon** supports `style` on all button types:
- `Button.inline(text, data, style="primary")`
- `Button.url(text, url, style="primary")`
- `Button.switch_inline(text, query=..., style="primary")`

**Raw Bot API** `inline_keyboard` also accepts `"style"` field in button dicts:
- `{"text":..., "callback_data":..., "style":"primary"}`
- `{"text":..., "switch_inline_query_current_chat":..., "style":"primary"}`

**Convention:**
- `primary` (blue) — action buttons, URL links, inline inputs
- `danger` (red) — back, cancel, revoke, delete
- `success` (green) — toggle on, active state (not used in OBHOD currently)

**The `_btn()` helper in VKTurn.py** already has `style` as a parameter
(default `"primary"`). `Updater.py` and `core.py` (raw API) were missing styles
on many buttons — patched in this session.

*Updated 2026-07-27: added parse_mode=None fix, inline check after API_ID, button styling.*