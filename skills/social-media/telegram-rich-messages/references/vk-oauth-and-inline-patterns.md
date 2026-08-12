# VK OAuth & Inline Query Patterns (from OBHOD Session)

## VK OAuth Redirect URI Fix

**Problem:** `{"error":"invalid_request","error_description":"redirect_uri is incorrect, check application redirect uri in the settings page"}`

**Root Cause:** Using unofficial app ID `2685278` with `https://oauth.vk.com/blank.html` redirect URI that wasn't configured in VK app settings.

**Solution:** Use official VK Standalone App ID `3697615` (official VK mobile app) which allows `https://oauth.vk.com/blank.html` by default.

```python
VK_DEFAULT_APP_ID = 3697615  # Official VK app - no redirect URI config needed
VK_REDIRECT = "https://oauth.vk.com/blank.html"
VK_DEFAULT_SCOPE = "offline"
VK_API_VERSION = "5.199"

def build_vk_auth_url():
    return (
        "https://oauth.vk.com/authorize"
        f"?client_id={VK_DEFAULT_APP_ID}"
        f"&display=page"
        f"&redirect_uri={VK_REDIRECT}"
        f"&scope={VK_DEFAULT_SCOPE}"
        f"&response_type=token"
        f"&v={VK_API_VERSION}"
    )
```

**Token Extraction:**
```python
VK_TOKEN_RE = re.compile(r"access_token=([A-Za-z0-9._-]+)")

def extract_vk_token(text: str) -> str | None:
    if not text:
        return None
    m = VK_TOKEN_RE.search(text)
    return m.group(1) if m else None
```

## Inline Query Handler Pattern

**Problem:** User wanted inline query results to show "Tap for transfer value" title instead of the actual token/key content.

**Solution:** Store the value in pending dict, always return fixed title:

```python
_pending_inline = {}

@bot.on(events.InlineQuery())
async def inline_handler(event):
    if not data_manager.is_privileged(event.sender_id):
        return
    query = event.text
    for prefix, (method, validator) in installer.get_inline_inputs().items():
        if query.startswith(prefix):
            value = query[len(prefix):].strip()
            valid = validator(value) if validator else bool(value)
            _pending_inline[event.sender_id] = (prefix, method)
            builder = event.builder
            result = builder.article(
                title="Tap for transfer value",  # FIXED TITLE
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
    value = (event.raw_text or "").strip()
    await method(event, value)
    try:
        await event.delete()
    except Exception:
        pass
```

**Key Points:**
- Always use `"Tap for transfer value"` as article title
- Store `(prefix, method)` in pending, not the value
- Value comes from `event.raw_text` after user selects inline result
- Delete the via-bot message to keep chat clean

## Ubuntu 24.04 iptables-persistent vs ufw Conflict

**Problem:** `ufw : Breaks: iptables-persistent but 1.0.20 is to be installed`

**Solution:** Remove ufw entirely, use iptables directly:

```bash
# Install iptables-persistent (not ufw)
apt update -qq && apt install -y wireguard wireguard-tools qrencode iptables-persistent jq python3

# Open WireGuard port via iptables (persisted by netfilter-persistent)
iptables -C INPUT -p udp --dport 51820 -j ACCEPT 2>/dev/null || \
    iptables -A INPUT -p udp --dport 51820 -j ACCEPT
netfilter-persistent save
```

**In ensure_profile.sh:** Remove `ufw allow "$PORT"/tcp` and `ufw allow "$PORT"/udp` lines.

## OWNER_ID Setup Timing

**Problem:** OWNER_ID not requested during first-run setup.

**Solution:** Move OWNER_ID prompt inside the `if [ ! -f "$ENV_FILE" ]` block, before systemd setup:

```bash
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

# THEN set up systemd service (which needs OWNER_ID in .env)
UNIT_DIR="/home/$OBHOD_USER/.config/systemd/user"
# ... create service, enable, start
```

## WireGuard Wrap Key Path

**Problem:** `wrapKeyHex` empty in iOS links.

**Solution:** Centralized read function with constant path:

```python
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
    link = build_ios_link(peer, join_link, obf_key)  # wrapKeyHex populated
```

## Related Files (OBHOD Repo)

| File | Purpose |
|------|---------|
| `BOT/Modules/VKTurn.py` | VK Turn module with text-based token capture |
| `BOT/core.py` | Inline query handler with fixed title |
| `Storage/Installation/Setuper.sh` | Installation script with OWNER_ID timing fix |
| `Storage/VKTurn/setup_root.sh` | Root setup without ufw |
| `Storage/VKTurn/ensure_profile.sh` | Profile setup without ufw |

---

*Generated from session fixing OBHOD (i-execute/OBHOD) - Telegram bot for WireGuard + VK Turn proxy management*