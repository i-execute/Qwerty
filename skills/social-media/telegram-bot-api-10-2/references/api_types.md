# Telegram Bot API 10.2 — Complete Type Reference

## Overview

**Released:** July 14, 2026
**Base:** Bot API 10.1 (June 11, 2026)
**Key Additions:** Ephemeral Messages, Rich Messages v2, Communities, Mini App Security

---

## New Types (10.2)

### Ephemeral Messages

| Type | Fields |
|------|--------|
| `Message` (extended) | `is_ephemeral: Boolean`, `ephemeral_user_id: Integer`, `ephemeral_expiration_date: Integer`, `ephemeral_chat_id: Integer` |
| `BotCommand` (extended) | `ephemeral: Boolean` |
| `ReplyParameters` (extended) | `ephemeral_user_id: Integer` |

### Rich Messages v2

| Type | Description |
|------|-------------|
| `InputRichMessageMedia` | Explicit media attachment for rich messages |
| `InputMediaVoiceNote` | Voice note as media input |
| `InputRichBlockListItem` | Input variant for list items |
| `InputRichBlock*` | All 24 Input variants for structured blocks |

### Communities

| Type | Fields |
|------|--------|
| `Community` | `id: String`, `title: String`, `description: String`, `icon: ChatPhoto`, `member_count: Integer`, `chat_ids: Integer[]`, `bot_ids: Integer[]` |
| `ChatFullInfo` (extended) | `community: Community` |
| `CommunityChatAdded` | `community: Community`, `chat: Chat` |
| `CommunityChatRemoved` | `community: Community`, `chat: Chat` |

### General

| Type | Description |
|------|-------------|
| `BotSubscriptionUpdated` | User payment subscription changes |
| `BotAccessSettings` | Managed bot access control |
| `Update` (extended) | `subscription`, `community_chat_added`, `community_chat_removed`, `community` fields |

---

## InputRichMessageMedia

```json
{
  "type": "photo" | "video" | "animation" | "audio" | "voice_note",
  "media": "file_id" | "https://..." | "attach://<name>",
  "caption": { "type": "caption", "content": [...] },
  "credit": { "type": "caption", "content": [...] }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | String | Yes | Media type |
| `media` | String | Yes | File identifier |
| `caption` | InputRichBlockCaption | No | Rich caption |
| `credit` | InputRichBlockCaption | No | Attribution |

---

## InputMediaVoiceNote

```json
{
  "type": "voice_note",
  "media": "file_id",
  "duration": 30,
  "caption": "Voice caption",
  "parse_mode": "MarkdownV2",
  "caption_entities": [{ "type": "bold", "offset": 0, "length": 4 }]
}
```

| Field | Type | Required |
|-------|------|----------|
| `type` | `"voice_note"` | Yes |
| `media` | String | Yes |
| `duration` | Integer | No |
| `caption` | String | No |
| `parse_mode` | String | No |
| `caption_entities` | MessageEntity[] | No |

---

## InputRichBlockListItem

```json
{
  "type": "list_item",
  "prefix": [{ "type": "plain", "text": "☐ " }],
  "content": [
    { "type": "paragraph", "content": [{ "type": "plain", "text": "Task 1" }] }
  ]
}
```

| Field | Type | Required |
|-------|------|----------|
| `type` | `"list_item"` | Yes |
| `prefix` | RichText[] | Yes |
| `content` | InputRichBlock[] | Yes |

---

## Methods (New in 10.2)

### Ephemeral Messages

| Method | Parameters |
|--------|------------|
| `sendMessage` (extended) | `ephemeral: Boolean`, `ephemeral_user_id: Integer`, `ephemeral_expiration_date: Integer` |
| `sendPhoto` (extended) | Same ephemeral params |
| `sendVideo` (extended) | Same ephemeral params |
| `sendAnimation` (extended) | Same ephemeral params |
| `sendAudio` (extended) | Same ephemeral params |
| `sendDocument` (extended) | Same ephemeral params |
| `sendSticker` (extended) | Same ephemeral params |
| `sendVideoNote` (extended) | Same ephemeral params |
| `sendVoice` (extended) | Same ephemeral params |
| `sendContact` (extended) | Same ephemeral params |
| `sendLocation` (extended) | Same ephemeral params |
| `sendVenue` (extended) | Same ephemeral params |
| `sendPoll` (extended) | Same ephemeral params |
| `sendDice` (extended) | Same ephemeral params |
| `editEphemeralMessageText` | `chat_id`, `message_id`, `ephemeral_user_id`, `text`, `parse_mode`, `entities`, `reply_markup` |
| `editEphemeralMessageMedia` | `chat_id`, `message_id`, `ephemeral_user_id`, `media`, `reply_markup` |
| `editEphemeralMessageCaption` | `chat_id`, `message_id`, `ephemeral_user_id`, `caption`, `parse_mode`, `caption_entities`, `reply_markup` |
| `editEphemeralMessageReplyMarkup` | `chat_id`, `message_id`, `ephemeral_user_id`, `reply_markup` |
| `deleteEphemeralMessage` | `chat_id`, `message_id`, `ephemeral_user_id` |

### Rich Messages

| Method | New Parameters |
|--------|----------------|
| `sendRichMessage` | `rich_message.media: InputRichMessageMedia` |
| `sendRichMessageDraft` | `rich_message.media: InputRichMessageMedia` |

### Communities

| Method | Description |
|--------|-------------|
| (Read-only in 10.2) | `getChat` returns `community` field in `ChatFullInfo` |
| Future | Community management methods |

### Bot Access

| Method | Description |
|--------|-------------|
| `getManagedBotAccessSettings` | Get bot access settings |
| `setManagedBotAccessSettings` | Set bot access settings |

### User Personal Chats

| Method | Description |
|--------|-------------|
| `getUserPersonalChatMessages` | Get messages from user's personal chat with bot |

### Bot Commands

| Method | New Field |
|--------|-----------|
| `setMyCommands` | `commands[].ephemeral: Boolean` |

---

## Updated Objects

### Message (Extended)

```json
{
  "message_id": 123,
  "date": 1700000000,
  "chat": { "id": -1001234567890, "type": "supergroup" },
  "from": { "id": 987654321, "is_bot": true },
  "is_ephemeral": true,
  "ephemeral_user_id": 123456789,
  "ephemeral_expiration_date": 1700086400,
  "ephemeral_chat_id": -1001234567890,
  "text": "Private message"
}
```

### BotCommand (Extended)

```json
{
  "command": "start",
  "description": "Start bot",
  "ephemeral": true
}
```

### ReplyParameters (Extended)

```json
{
  "message_id": 123,
  "chat_id": -1001234567890,
  "ephemeral_user_id": 123456789,
  "quote": "Optional quote",
  "quote_entities": [...]
}
```

### ChatFullInfo (Extended)

```json
{
  "id": -1001234567890,
  "title": "Group Name",
  "type": "supergroup",
  "community": {
    "id": "comm_123",
    "title": "Tech Community",
    "description": "All about tech",
    "member_count": 15000
  }
}
```

### Update (Extended)

```json
{
  "update_id": 12345,
  "community_chat_added": {
    "community": { "id": "comm_123", "title": "Tech Community" },
    "chat": { "id": -100999, "title": "New Channel" }
  },
  "community_chat_removed": {
    "community": { "id": "comm_123" },
    "chat": { "id": -100999 }
  },
  "subscription": {
    "user": { "id": 123 },
    "is_active": true,
    "expiration_date": 1700000000
  }
}
```

---

## Error Codes (New in 10.2)

| Code | Description | Context |
|------|-------------|---------|
| 400 | `EPHEMERAL_MESSAGE_NOT_FOUND` | Expired/deleted ephemeral message |
| 400 | `EPHEMERAL_USER_MISMATCH` | Wrong `ephemeral_user_id` |
| 400 | `EPHEMERAL_EXPIRED` | Expiration date in past |
| 400 | `RICH_MESSAGE_MEDIA_UNSUPPORTED` | Invalid media type in rich message |
| 400 | `COMMUNITY_NOT_FOUND` | Community ID invalid |
| 403 | `MINI_APP_EXTERNAL_ORIGIN_BLOCKED` | External site used Mini App API |
| 400 | `BOT_COMMAND_EPHEMERAL_INVALID` | Ephemeral command used incorrectly |
| 400 | `INPUT_RICH_MESSAGE_MEDIA_REQUIRED` | Media required but not provided |

---

## Limits & Constraints (10.2 Additions)

| Limit | Value |
|-------|-------|
| Ephemeral message max expiration | 30 days (2,592,000 seconds) |
| Ephemeral message min expiration | 60 seconds |
| Communities per chat | 1 (currently) |
| Mini App external origin block | Effective July 20, 2026 |
| BotAccessSettings per managed bot | 1 |

---

## Version Comparison

| Feature | 10.0 (May 8) | 10.1 (Jun 11) | 10.2 (Jul 14) |
|---------|--------------|---------------|---------------|
| Guest Mode | ✅ | ✅ | ✅ |
| Rich Messages | ❌ | ✅ | ✅ v2 |
| Guardian Bots | ❌ | ✅ | ✅ |
| Poll Media Links | ❌ | ✅ | ✅ |
| Ephemeral Messages | ❌ | ❌ | ✅ |
| InputRichMessageMedia | ❌ | ❌ | ✅ |
| InputMediaVoiceNote | ❌ | ❌ | ✅ |
| Communities | ❌ | ❌ | ✅ (read-only) |
| Mini App Security | ❌ | ❌ | ✅ (Jul 20) |
| Bot Subscriptions | ❌ | ❌ | ✅ |
| Bot Access Settings | ❌ | ❌ | ✅ |

---

## Migration Checklist

### For Existing Bots

- [ ] **Rich Messages**: Migrate to `InputRichMessageMedia` for embedded media
- [ ] **Ephemeral**: Add `ephemeral` commands for group privacy
- [ ] **Communities**: Detect `chat.community` in `getChat` responses
- [ ] **Mini Apps**: Audit external links before July 20, 2026
- [ ] **Voice Notes**: Use `InputMediaVoiceNote` in rich messages

### Breaking Changes (July 20, 2026)

- External origins **blocked** from Mini App methods by default
- Opt-out via @BotFather → Mini Apps → Security Settings
- Requires security review if opting out

---

## Quick Reference: Method Parameters

### sendMessage (10.2 Full)

```json
{
  "chat_id": -1001234567890,
  "text": "Hello",
  "parse_mode": "MarkdownV2",
  "ephemeral": true,
  "ephemeral_user_id": 123456789,
  "ephemeral_expiration_date": 1700086400,
  "reply_parameters": {
    "message_id": 456,
    "chat_id": -1001234567890,
    "ephemeral_user_id": 123456789
  },
  "reply_markup": { "inline_keyboard": [...] }
}
```

### sendRichMessage (10.2 Full)

```json
{
  "chat_id": 123456789,
  "rich_message": {
    "blocks": [...],
    "media": {
      "type": "photo",
      "media": "AgACAgIAAxkBA...",
      "caption": { "type": "caption", "content": [...] },
      "credit": { "type": "caption", "content": [...] }
    }
  }
}
```

### setMyCommands (10.2)

```json
{
  "commands": [
    { "command": "start", "description": "Start", "ephemeral": true },
    { "command": "help", "description": "Help", "ephemeral": true },
    { "command": "public", "description": "Public", "ephemeral": false }
  ]
}
```

---

## Links

- [Bot API 10.2 Changelog](https://core.telegram.org/bots/api-changelog#july-14-2026)
- [Ephemeral Messages](https://core.telegram.org/bots/features#ephemeral-messages)
- [Rich Messages](https://core.telegram.org/bots/api#rich-messages)
- [Rich Markdown Style](https://core.telegram.org/bots/api#rich-markdown-style)
- [Rich HTML Style](https://core.telegram.org/bots/api#rich-html-style)
- [InputRichMessageMedia](https://core.telegram.org/bots/api#inputrichmessagemedia)
- [InputMediaVoiceNote](https://core.telegram.org/bots/api#inputmediavoicenote)
- [Communities](https://core.telegram.org/bots/api#community)
- [BotNews 119](https://t.me/BotNews/119)
- [Mini App Security](https://core.telegram.org/bots/api-changelog#july-14-2026)