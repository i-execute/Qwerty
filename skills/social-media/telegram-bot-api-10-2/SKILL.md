---
name: telegram-bot-api-10-2
description: "Complete reference for Telegram Bot API 10.2 (July 14, 2026) — Ephemeral Messages, Rich Messages enhancements (InputRichMessageMedia, InputMediaVoiceNote), Communities, Mini App security hardening"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, bot-api, bot-api-10.2, ephemeral-messages, communities, rich-messages, mini-apps]
    related_skills: [telegram-bot-api-10-rich-messages, telegram-rich-messages, xurl, github-issues]
---

# Telegram Bot API 10.2 Skill

## Overview

**Bot API 10.2 (July 14, 2026)** builds on 10.1's Rich Messages foundation with three major features:

| Feature | Description |
|---------|-------------|
| **Ephemeral Messages** | Group messages visible only to specific user + bot |
| **Rich Messages v2** | Structured `InputRichBlock` entities + explicit `InputRichMessageMedia` |
| **Communities** | Linked groups/channels/bots around shared topic |
| **Mini App Security** | External link isolation (opt-out via @BotFather) |

---

## Ephemeral Messages

### Concept

Ephemeral messages are **group messages visible only to one specific user and the bot** — perfect for:
- Welcome/onboarding messages
- Private summaries in groups
- Whisper/secret replies
- Bot command results in groups
- Personalized notifications

### Key Properties

| Property | Description |
|----------|-------------|
| **Visibility** | Only sender, target user, and bot can see |
| **Expiration** | Auto-delete after configurable time (default: 24h) |
| **Media Support** | Photos, videos, animations, audio, documents, stickers, voice, video notes, contacts, locations, venues, polls |
| **Replies** | Can reply to ephemeral messages |
| **Deletion** | Bot can delete before expiry via `deleteEphemeralMessage` |
| **Commands** | Bot commands can be marked `ephemeral: true` |

### BotCommand — Ephemeral Field

```json
{
  "command": "start",
  "description": "Start the bot",
  "ephemeral": true
}
```

When user invokes `/start` in group → bot's reply is ephemeral (visible only to that user).

### Methods

#### sendMessage (and all send* methods)
```json
{
  "chat_id": -1001234567890,
  "text": "Welcome! This is private to you.",
  "ephemeral": true,
  "ephemeral_user_id": 123456789,
  "ephemeral_expiration_date": 1700000000  // Unix timestamp, optional
}
```
- `ephemeral`: `true` to send as ephemeral
- `ephemeral_user_id`: Target user who can see it (required if `ephemeral: true`)
- `ephemeral_expiration_date`: When message auto-deletes (default: 24 hours)

#### editEphemeralMessageText
```json
{
  "chat_id": -1001234567890,
  "message_id": 42,
  "text": "Updated private message",
  "ephemeral_user_id": 123456789
}
```

#### editEphemeralMessageMedia
```json
{
  "chat_id": -1001234567890,
  "message_id": 42,
  "media": { "type": "photo", "media": "file_id" },
  "ephemeral_user_id": 123456789
}
```

#### editEphemeralMessageCaption
```json
{
  "chat_id": -1001234567890,
  "message_id": 42,
  "caption": "New caption",
  "ephemeral_user_id": 123456789
}
```

#### editEphemeralMessageReplyMarkup
```json
{
  "chat_id": -1001234567890,
  "message_id": 42,
  "reply_markup": { "inline_keyboard": [...] },
  "ephemeral_user_id": 123456789
}
```

#### deleteEphemeralMessage
```json
{
  "chat_id": -1001234567890,
  "message_id": 42,
  "ephemeral_user_id": 123456789
}
```

#### ReplyParameters — Ephemeral Support
```json
{
  "message_id": 42,
  "chat_id": -1001234567890,
  "ephemeral_user_id": 123456789  // Required when replying to ephemeral
}
```

### Message Object — New Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_ephemeral` | `Boolean` | True if message is ephemeral |
| `ephemeral_user_id` | `Integer` | User ID who can see this message |
| `ephemeral_expiration_date` | `Integer` | Unix timestamp when message expires |
| `ephemeral_chat_id` | `Integer` | Original chat where message was sent |

### Ephemeral Message Flow

```
Group Chat (-1001234567890)
├── User A (123456789) sends /start
├── Bot replies with ephemeral: true, ephemeral_user_id: 123456789
├── User A sees: "Welcome! [private]"
├── User B sees: [nothing]
├── User C sees: [nothing]
└── After 24h (or ephemeral_expiration_date): Auto-deleted
```

---

## Rich Messages Enhancements (v2)

### InputRichMessageMedia (NEW in 10.2)

Explicitly attach media to rich messages sent via Markdown/HTML **or** structured blocks.

```json
{
  "chat_id": 123456789,
  "text": "**Report** with chart",
  "parse_mode": "MarkdownV2",
  "rich_message_media": {
    "type": "photo",
    "media": "AgACAgIAAxkBA...",  // file_id or attach://
    "caption": { "type": "caption", "content": [...] },
    "credit": { "type": "caption", "content": [...] }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"photo" \| "video" \| "animation" \| "audio" \| "voice_note"` | Yes | Media type |
| `media` | `String` | Yes | file_id, HTTP URL, or `attach://<name>` |
| `caption` | `InputRichBlockCaption` | No | Rich caption |
| `credit` | `InputRichBlockCaption` | No | Attribution/credit |

### InputMediaVoiceNote (NEW in 10.2)

Send voice messages as media.

```json
{
  "type": "voice_note",
  "media": "file_id_or_attach",
  "duration": 30,
  "caption": "Voice note caption",
  "parse_mode": "MarkdownV2"
}
```

| Field | Type | Required |
|-------|------|----------|
| `type` | `"voice_note"` | Yes |
| `media` | `String` | Yes |
| `duration` | `Integer` | No |
| `caption` | `String` | No |
| `parse_mode` | `String` | No |
| `caption_entities` | `MessageEntity[]` | No |

### InputRichBlockListItem (NEW in 10.2)

Input variant for list items when building structured rich messages.

```json
{
  "type": "list",
  "items": [
    {
      "type": "list_item",
      "prefix": [{ "type": "plain", "text": "☐ " }],
      "content": [
        { "type": "paragraph", "content": [{ "type": "plain", "text": "Task 1" }] }
      ]
    }
  ],
  "ordered": false,
  "numeral": "task"
}
```

### sendRichMessage / sendRichMessageDraft — Media Field

`InputRichMessage` now accepts optional `media` field:

```json
{
  "blocks": [...],
  "media": {
    "type": "photo",
    "media": "file_id",
    "caption": { "type": "caption", "content": [...] },
    "credit": { "type": "caption", "content": [...] }
  }
}
```

---

## Communities (Initial Support)

### Concept

**Community** = Multiple supergroups, channels, and bots linked around a shared topic/audience.

### Community Object

```json
{
  "id": "123456789",
  "title": "Tech Community",
  "description": "All about technology",
  "icon": { "file_id": "...", "file_unique_id": "..." },
  "member_count": 15000,
  "chat_ids": [-100111, -100222, -100333],
  "bot_ids": [987654321, 123456789]
}
```

### ChatFullInfo — New Field

```json
{
  "community": {
    "id": "123456789",
    "title": "Tech Community"
  }
}
```

### Service Messages

| Update | Description |
|--------|-------------|
| `community_chat_added` | Chat joined community |
| `community_chat_removed` | Chat left community |

```json
{
  "update_id": 12345,
  "community_chat_added": {
    "community": { "id": "123", "title": "Tech Community" },
    "chat": { "id": -100999, "title": "New Channel" }
  }
}
```

### Community Methods (Future)

> **Note**: Full Community management API coming in later versions. Currently read-only detection.

---

## Mini App Security Hardening

### Change (Effective July 20, 2026)

**External websites opened from Mini App links can no longer use Mini App methods by default.**

### What's Blocked

- `web_app.openLink` from external domains
- `web_app.openTelegramLink` from external domains
- `web_app.requestWriteAccess` from external domains
- `web_app.requestContact` from external domains
- `web_app.showPopup` from external domains
- `web_app.showScanQrPopup` from external domains
- `web_app.close` from external domains
- `web_app.expand` / `web_app.collapse` from external domains
- `web_app.enableVerticalSwipes` / `web_app.disableVerticalSwipes` from external domains
- `web_app.setHeaderColor` / `web_app.setBackgroundColor` from external domains
- `web_app.onThemeChanged` from external domains
- `web_app.onViewportChanged` from external domains
- `web_app.onSafeAreaChanged` from external domains
- `web_app.addToHomeScreen` from external domains
- `web_app.checkVersion` from external domains
- `web_app.setSafeAreaInsets` from external domains
- All `web_app.*` methods from non-Mini-App origins

### Opt-Out (via @BotFather)

1. Open @BotFather
2. `/mybots` → Select bot → `Mini Apps` → Select Mini App
3. `Security Settings` → `Disable External Origin Protection`

### If You Opt Out

> **You acknowledge responsibility** for ensuring external sites are trusted and have no malicious links.

### Migration Checklist

- [ ] Audit all external links in Mini App
- [ ] Move critical flows to Mini App domain
- [ ] Test with protection enabled (pre-July 20)
- [ ] Decide: keep protection OR opt-out with security review

---

## Complete Changelog: July 14, 2026 (Bot API 10.2)

### Rich Messages
- Added `InputRichMessageMedia` class + `media` field to `InputRichMessage`
- Added `InputMediaVoiceNote` class
- Added `InputRichBlockListItem` class
- Added `InputRichBlockParagraph`, `InputRichBlockSectionHeading`, `InputRichBlockPreformatted`, `InputRichBlockFooter`, `InputRichBlockDivider`, `InputRichBlockMathematicalExpression`, `InputRichBlockAnchor`, `InputRichBlockList`, `InputRichBlockBlockQuotation`, `InputRichBlockPullQuotation`, `InputRichBlockCollage`, `InputRichBlockSlideshow`, `InputRichBlockTable`, `InputRichBlockDetails`, `InputRichBlockMap`, `InputRichBlockAnimation`, `InputRichBlockAudio`, `InputRichBlockPhoto`, `InputRichBlockVideo`, `InputRichBlockVoiceNote`, `InputRichBlockThinking` — all Input variants for structured blocks

### Ephemeral Messages
- Added `is_ephemeral`, `ephemeral_user_id`, `ephemeral_expiration_date`, `ephemeral_chat_id` to `Message`
- Added `ephemeral` field to `BotCommand`
- Added `ephemeral`, `ephemeral_user_id`, `ephemeral_expiration_date` parameters to `sendMessage`, `sendPhoto`, `sendVideo`, `sendAnimation`, `sendAudio`, `sendDocument`, `sendSticker`, `sendVideoNote`, `sendVoice`, `sendContact`, `sendLocation`, `sendVenue`, `sendPoll`, `sendDice`
- Added `ephemeral_user_id` to `ReplyParameters`
- Added methods: `editEphemeralMessageText`, `editEphemeralMessageMedia`, `editEphemeralMessageCaption`, `editEphemeralMessageReplyMarkup`, `deleteEphemeralMessage`

### Communities
- Added `Community` class
- Added `community` field to `ChatFullInfo`
- Added `CommunityChatAdded`, `CommunityChatRemoved` service message types
- Added `community_chat_added`, `community_chat_removed` fields to `Message`
- Added `community` field to `Update`

### General
- Added `BotSubscriptionUpdated` class + `subscription` field to `Update`
- Added `BotAccessSettings` class + `getManagedBotAccessSettings` / `setManagedBotAccessSettings` methods
- Added `getUserPersonalChatMessages` method
- Hardened Mini App security (external origin isolation from July 20, 2026)
- Added `secret_token` header documentation for webhooks
- Bot-to-bot messaging via username (if both enabled)
- Business bot reply to other bots
- Empty text allowed in `sendMessageDraft`

---

## Python Helpers for API 10.2

```python
# ephemeral_helpers.py

from typing import Optional, Dict, Any, List

def send_ephemeral(
    bot_token: str,
    chat_id: int,
    text: str,
    ephemeral_user_id: int,
    expiration_seconds: int = 86400,  # 24 hours
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """Send ephemeral message to specific user in group."""
    import time
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "ephemeral": True,
        "ephemeral_user_id": ephemeral_user_id,
        "ephemeral_expiration_date": int(time.time()) + expiration_seconds
    }
    payload.update(kwargs)

    async def _send():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    return _send()


def edit_ephemeral_text(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    text: str,
    parse_mode: str = "MarkdownV2"
) -> Dict[str, Any]:
    """Edit ephemeral message text."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id,
        "text": text,
        "parse_mode": parse_mode
    }

    async def _send():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    return _send()


def delete_ephemeral(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int
) -> Dict[str, Any]:
    """Delete ephemeral message before expiration."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/deleteEphemeralMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id
    }

    async def _send():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    return _send()


def reply_to_ephemeral(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    text: str,
    **kwargs
) -> Dict[str, Any]:
    """Reply to an ephemeral message."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_parameters": {
            "message_id": message_id,
            "chat_id": chat_id,
            "ephemeral_user_id": ephemeral_user_id
        }
    }
    payload.update(kwargs)

    async def _send():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    return _send()


def rich_message_with_media(
    bot_token: str,
    chat_id: int,
    blocks: List[Dict],
    media_type: str,  # "photo", "video", "animation", "audio", "voice_note"
    media_file_id: str,
    caption: List[Dict] = None,
    credit: List[Dict] = None
) -> Dict[str, Any]:
    """Send rich message with embedded media (10.2+)."""
    import aiohttp

    media = {"type": media_type, "media": media_file_id}
    if caption:
        media["caption"] = {"type": "caption", "content": caption}
    if credit:
        media["credit"] = {"type": "caption", "content": credit}

    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": {
            "blocks": blocks,
            "media": media
        }
    }

    async def _send():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()

    return _send()
```

---

## Error Codes (New in 10.2)

| Code | Description |
|------|-------------|
| 400 | `EPHEMERAL_MESSAGE_NOT_FOUND` — Message expired or deleted |
| 400 | `EPHEMERAL_USER_MISMATCH` — Wrong `ephemeral_user_id` |
| 400 | `EPHEMERAL_EXPIRED` — Expiration date in past |
| 400 | `RICH_MESSAGE_MEDIA_UNSUPPORTED` — Media type not allowed |
| 400 | `COMMUNITY_NOT_FOUND` — Community ID invalid |
| 403 | `MINI_APP_EXTERNAL_ORIGIN_BLOCKED` — External site tried Mini App API |
| 400 | `BOT_COMMAND_EPHEMERAL_INVALID` — Ephemeral command used incorrectly |

---

## Migration Guide: 10.1 → 10.2

### Rich Messages
| Before (10.1) | After (10.2) |
|---------------|--------------|
| Media via `sendPhoto` etc. | `InputRichMessageMedia` in `rich_message.media` |
| Voice notes not in rich | `InputMediaVoiceNote` + `InputRichBlockVoiceNote` |
| List items inline | `InputRichBlockListItem` |

### Ephemeral — NEW
```python
# 10.1: Not possible
# 10.2:
send_ephemeral(token, group_id, "Private!", user_id=123)
```

### Communities — NEW (Read-only)
```python
# Detect community
if message.chat.get("community"):
    community_id = message.chat["community"]["id"]
```

### Mini Apps — BREAKING (July 20)
- External links lose Mini App API access
- Opt-out via @BotFather if needed
- Audit all `target="_blank"` links

---

## References

- [Bot API 10.2 Changelog](https://core.telegram.org/bots/api-changelog#july-14-2026)
- [Ephemeral Messages](https://core.telegram.org/bots/features#ephemeral-messages)
- [Rich Messages](https://core.telegram.org/bots/api#rich-messages)
- [Rich Markdown Style](https://core.telegram.org/bots/api#rich-markdown-style)
- [Rich HTML Style](https://core.telegram.org/bots/api#rich-html-style)
- [InputRichMessageMedia](https://core.telegram.org/bots/api#inputrichmessagemedia)
- [Communities](https://core.telegram.org/bots/api#community)
- [Mini App Security](https://core.telegram.org/bots/api-changelog#july-14-2026)
- [BotNews 119](https://t.me/BotNews/119)