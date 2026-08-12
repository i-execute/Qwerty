---
name: obhod-vkturn
description: "OBHOD: Telegram bot for WireGuard + VK Calls proxy management. Architecture, installer flow, freeturn:// URI scheme, WireGuard peer management, and VK API integration."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Telegram, WireGuard, VK, proxy, bash, python, telethon]
    related_skills: []
---

# OBHOD — VK Turn Proxy Bot

OBHOD is a self-hosted Telegram bot that manages WireGuard peers and VK Call-based TURN proxies. Users interact with the bot in Telegram to create VPN peers (iOS or Android), authenticate with VK to generate call links, and receive `vkturnproxy://` (iOS) or `freeturn://` (Android) share links.

## Repo

- **GitHub**: `github.com/i-execute/OBHOD`
- **Local path**: `/home/forget/OBHOD`
- **Working branch**: `main` (user pushes fixes directly to main)
- **Push auth**: GitHub PAT in memory (user profile)

## Architecture

```
BOT/
  core.py          — Main entry point, bot lifecycle, bootstrap/installer modes
  installer.py     — Module loader framework (BaseModule, decorators)
  Modules/
    VKTurn.py       — VK TURN proxy peer management (iOS + Android)
    Updater.py      — Server binary updater (GitHub releases)
  Strings/
    English.yml / Russian.yml / Chinese.yml — i18n strings
Storage/
  Installation/
    Setuper.sh      — Root installer (apt deps, systemd service, BOT_TOKEN, OWNER_ID)
  VKTurn/
    setup_root.sh   — WireGuard infra setup, sudoers, server binary download
    add_peer_ios.sh     — Add WG peer (iOS/standalone)
    add_peer_android.sh — Add WG peer (Android/WireGuard app)
    add_client.sh       — Register freeturn cid in clients.json allowlist
    ensure_profile.sh   — Start/manage obfuscation profile proxy service
    revoke_peer.sh      — Remove WG peer + freeturn cid
    update_core.sh      — Replace server binary
```

### Bot Lifecycle (core.py)

1. **No BOT_TOKEN** → error, exit
2. **BOT_TOKEN but no OWNER_ID** → `run_echo_id_mode`: bot replies to any DM with the sender's numeric user ID (installer copies this into Setuper.sh)
3. **BOT_TOKEN + OWNER_ID but no API_ID/API_HASH** → `run_setup_wizard`: interactive inline-keyboard flow to collect Telegram API credentials
4. **All set** → `run_full_bot`: Telethon-based full bot with module loading

### Shell Scripts → /opt/vkturn/

`setup_root.sh` copies all scripts to `/opt/vkturn/` and sets up sudoers for the `OBHOD` system user. Scripts output `KEY=VALUE` lines parsed by Python `subprocess`.

### Sudoers

The OBHOD user runs scripts via `sudo -n /opt/vkturn/<script>`. Two formats are supported:
- **Comma-separated** (classic sudo): one line with all commands
- **One-per-line** (sudo-rs compatible): written when sudo-rs is detected

## freeturn:// URI Scheme (Android)

See `references/freeturn-uri-spec.md` for the full spec from the upstream repo.

Key points:
- Format: `freeturn://<base64url(json)>` (no padding, like Go `base64.RawURLEncoding`)
- `v` field = 1 (version)
- Required: `provider`, `peer` (server `ip:port`)
- `wg` field embeds full WireGuard config so Android app imports it atomically
- `cid` must be registered in `/etc/wireguard/clients.json` allowlist before the client connects
- `-link` (VK call URL) is NEVER embedded — it's client-unique, supplied separately

## vkturnproxy:// URI Scheme (iOS)

Base64url-encoded JSON with `settings` object containing WireGuard peer keys, obfuscation profile, VK join link, and server endpoint. Uses WRAP-A obfuscation.

## Key Patterns

### Stale Update Flushing (echo-id mode)

When the bot starts in echo-id mode, flush stale `getUpdates` first:
```python
stale = await api.call("getUpdates", offset=-1, timeout=0)
api.offset = stale["result"][-1]["update_id"] + 1
```
This prevents backlog from consuming the installer's `/start` message.

### Peer Creation Flow

1. User picks call source (new/existing VK call)
2. User picks obfuscation profile (`rtpopus`, `rtpopus2`, `rtpopus3`)
3. User picks platform (iOS/Android)
4. User sends a tag name
5. Bot runs `add_peer_*.sh` → gets WG keys
6. Bot runs `ensure_profile.sh` → gets proxy port + wrap key
7. For Android: bot runs `add_client.sh` → registers cid in allowlist
8. Bot builds share link + sends to user

## Button Styling

ALL buttons in the bot must have a `style` attribute — user explicitly requires colored buttons everywhere.

| Button type | Telethon | Raw Bot API inline_keyboard | Style convention |
|---|---|---|---|
| Action / primary | `Button.inline(text, data, style="primary")` | `{"text":..., "callback_data":..., "style":"primary"}` | Blue — default action |
| URL button | `Button.url(text, url, style="primary")` | `{"text":..., "url":..., "style":"primary"}` | Blue — external links |
| Inline input | `Button.switch_inline(text, query=..., style="primary")` | `{"text":..., "switch_inline_query_current_chat":..., "style":"primary"}` | Blue — data entry |
| Back / cancel | `style="danger"` | `"style":"danger"` | Red — navigation back, cancel |
| Revoke / delete | `style="danger"` | `"style":"danger"` | Red — destructive actions |

**Telethon supports `style=` on all button types**: `Button.inline`, `Button.url`, `Button.switch_inline` — all accept `style` parameter.

**Raw Bot API `inline_keyboard` ALSO accepts `"style"` field** — verified working with Telegram servers. Add it to every `callback_data` and `switch_inline_query_current_chat` button dict.

The `_btn()` helper in VKTurn.py already has `style` as a parameter (default `"primary"`).

## Echo-ID Mode Message Format

The echo-id reply should be a single HTML blockquote — no Code/Result/Execution time wrapper:

```python
text = f"<blockquote><b>This is your id</b> – <code>{sender_id}</code></blockquote>"
await api.send_message(chat_id, text, parse_mode="HTML")
```

## Peer-Created Message Format

Uses HTML with blockquotes for structured data:

```python
message = (
    f"<b>✅ {self.strings['peer_created']}</b>\n\n"
    f"<blockquote><b>Tag</b>: <code>{esc_tag}</code>\n"
    f"<b>IP</b>: <code>{esc_ip}</code>\n"
    f"<b>Profile</b>: <code>{esc_profile}</code>\n"
    f"<b>Platform</b>: <code>{esc_platform}</code></blockquote>\n\n"
    f"<blockquote>{esc_link}</blockquote>"
)
```

All dynamic values must be `html.escape()`-d before insertion.

## Pitfalls

- **`parse_mode=None` causes 400 error** — Telegram Bot API rejects `"parse_mode": null` in JSON. In `BotAPI.send_message`, only include `parse_mode` if it's truthy. Same for `edit_message`.
- **Never use `127.0.0.1:9000` as peer fallback** — Android clients will try to connect to their own localhost. If server IP detection fails, leave peer empty (Android will reject, which is correct — server is misconfigured).
- **VK token capture uses text message regex** (`access_token=...`), NOT inline buttons — user explicitly rejected inline flow.
- **VK OAuth** uses `app_id 3697615` with redirect to `oauth.vk.com/blank.html`.
- **ufw removed** — conflicts with `iptables-persistent` on Ubuntu 24.04. All firewall rules use raw `iptables` + `netfilter-persistent save`.
- **`OWNER_ID` requested immediately** after bot connection in Setuper.sh (right after `echo-id` mode teaches the user their ID).
- **Inline title is always "Tap for transfer value"** — not localized.
- **`CLIENTS_DB` cleanup**: `revoke_peer.sh` removes cid entries by `comment == tag` matching.
- **`add_client.sh`**: must exist and be in sudoers, otherwise Android peers get created but the client can't authenticate.
- **Inline mode check timing**: Check `supports_inline_queries` AFTER API_ID is entered (in `run_setup_wizard`), NOT in Setuper.sh. If inline is off, send a warning message with a retry button instead of blocking installation. Setuper.sh should only warn, not `exit 1`.
- **Duplicate messages**: `notify_admins` must accept `exclude=sender_id` — the user who triggered the action already received `event.reply`, so `notify_admins` should skip them. Without this, the owner gets two copies of every peer-created message.
- **`freeturn://` link must embed `wg` field** — the Android app (FreeturnLink.kt parser) reads `wg` from the JSON payload and imports WireGuard config atomically. Don't hand WG config as separate text.
- **`cid` must be registered in `clients.json`** via `add_client.sh` BEFORE sending the freeturn:// link to the user. Without this, the Android client cannot authenticate to the TURN proxy.
