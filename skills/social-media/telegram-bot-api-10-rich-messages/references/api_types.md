# Telegram Bot API 10.1/10.2 Rich Messages - Complete Type Reference

## Quick Reference: All Types

### RichText Types (Inline Entities)

| Type | Class | Extends | Nestable? | Fields |
|------|-------|---------|-----------|--------|
| plain | — | base | N/A | `text: string` |
| bold | RichTextBold | RichText | ✅ | `text: RichText[]` |
| italic | RichTextItalic | RichText | ✅ | `text: RichText[]` |
| underline | RichTextUnderline | RichText | ✅ | `text: RichText[]` |
| strikethrough | RichTextStrikethrough | RichText | ✅ | `text: RichText[]` |
| spoiler | RichTextSpoiler | RichText | ✅ | `text: RichText[]` |
| marked | RichTextMarked | RichText | ✅ | `text: RichText[]` |
| subscript | RichTextSubscript | RichText | ✅ | `text: RichText[]` |
| superscript | RichTextSuperscript | RichText | ✅ | `text: RichText[]` |
| code | RichTextCode | RichText | ❌ | `text: string` |
| url | RichTextUrl | RichText | ❌ | `text: RichText[], url: string` |
| email | RichTextEmailAddress | RichText | ❌ | `text: RichText[], email: string` |
| phone | RichTextPhoneNumber | RichText | ❌ | `text: RichText[], phone_number: string` |
| bank_card | RichTextBankCardNumber | RichText | ❌ | `text: RichText[], number: string` |
| mention | RichTextMention | RichText | ❌ | `text: RichText[], user: User` |
| hashtag | RichTextHashtag | RichText | ❌ | `text: RichText[], hashtag: string` |
| cashtag | RichTextCashtag | RichText | ❌ | `text: RichText[], cashtag: string` |
| bot_command | RichTextBotCommand | RichText | ❌ | `text: RichText[], command: string` |
| custom_emoji | RichTextCustomEmoji | RichText | ❌ | `text: string, custom_emoji_id: string` |
| math | RichTextMathematicalExpression | RichText | ❌ | `text: string` |
| anchor | RichTextAnchor | RichText | N/A | `name: string` |
| anchor_link | RichTextAnchorLink | RichText | ❌ | `text: RichText[], anchor_name: string` |
| reference | RichTextReference | RichText | ❌ | `text: RichText[], reference_id: string` |
| reference_link | RichTextReferenceLink | RichText | ❌ | `text: RichText[], reference_id: string` |
| date_time | RichTextDateTime | RichText | N/A | `text: RichText[], timestamp: int` |

### RichBlock Types (Structural Blocks)

| Type | Class | Fields |
|------|-------|--------|
| paragraph | RichBlockParagraph | `content: RichText[]` |
| section_heading | RichBlockSectionHeading | `level: 1-6, content: RichText[]` |
| preformatted | RichBlockPreformatted | `content: RichText[], language?: string` |
| footer | RichBlockFooter | `content: RichText[]` |
| divider | RichBlockDivider | — |
| math | RichBlockMathematicalExpression | `content: string` |
| anchor | RichBlockAnchor | `name: string` |
| list | RichBlockList | `items: RichBlockListItem[], ordered: bool, numeral: string` |
| list_item | RichBlockListItem | `prefix: RichText[], content: RichBlock[]` |
| block_quote | RichBlockBlockQuotation | `content: RichBlock[], citation?: RichText[]` |
| pull_quote | RichBlockPullQuotation | `content: RichBlock[], citation?: RichText[]` |
| collage | RichBlockCollage | `items: RichBlockCollageItem[]` |
| slideshow | RichBlockSlideshow | `items: RichBlockSlideshowItem[]` |
| table | RichBlockTable | `rows: RichBlockTableRow[], caption?: RichBlockCaption, bordered: bool, striped: bool` |
| details | RichBlockDetails | `summary: RichText[], content: RichBlock[], open: bool` |
| map | RichBlockMap | `location: Location, zoom?: int` |
| animation | RichBlockAnimation | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` |
| audio | RichBlockAudio | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` |
| photo | RichBlockPhoto | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` |
| video | RichBlockVideo | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` |
| voice_note | RichBlockVoiceNote | `media: InputRichMessageMedia, caption?: RichBlockCaption` |
| thinking | RichBlockThinking | `text: string` |

### Table Types

| Type | Class | Fields |
|------|-------|--------|
| table_row | RichBlockTableRow | `cells: RichBlockTableCell[]` |
| table_cell | RichBlockTableCell | `content: RichText[], header: bool, align: "left"\|"center"\|"right", colspan: int, rowspan: int` |
| caption | RichBlockCaption | `content: RichText[]` |

### Collage/Slideshow Types

| Type | Class | Fields |
|------|-------|--------|
| collage_item | RichBlockCollageItem | `media: InputRichMessageMedia, width: int, height: int` |
| slideshow_item | RichBlockSlideshowItem | `media: InputRichMessageMedia, caption?: RichBlockCaption` |

### Input Types (For Sending)

| Input Class | For Block Type | Key Fields |
|-------------|----------------|------------|
| InputRichBlockParagraph | paragraph | `content: RichText[]` |
| InputRichBlockSectionHeading | section_heading | `level: 1-6, content: RichText[]` |
| InputRichBlockPreformatted | preformatted | `content: RichText[], language?: string` |
| InputRichBlockFooter | footer | `content: RichText[]` |
| InputRichBlockDivider | divider | — |
| InputRichBlockMathematicalExpression | math | `content: string` |
| InputRichBlockAnchor | anchor | `name: string` |
| InputRichBlockList | list | `items: InputRichBlockListItem[], ordered: bool, numeral: string` |
| InputRichBlockListItem | list_item | `prefix: RichText[], content: InputRichBlock[]` |
| InputRichBlockBlockQuotation | block_quote | `content: InputRichBlock[], citation?: RichText[]` |
| InputRichBlockPullQuotation | pull_quote | `content: InputRichBlock[], citation?: RichText[]` |
| InputRichBlockCollage | collage | `items: InputRichBlockCollageItem[]` |
| InputRichBlockSlideshow | slideshow | `items: InputRichBlockSlideshowItem[]` |
| InputRichBlockTable | table | `rows: InputRichBlockTableRow[], caption?: InputRichBlockCaption, bordered: bool, striped: bool` |
| InputRichBlockDetails | details | `summary: RichText[], content: InputRichBlock[], open: bool` |
| InputRichBlockMap | map | `location: Location, zoom?: int` |
| InputRichBlockAnimation | animation | `media: InputRichMessageMedia, caption?: InputRichBlockCaption, credit?: InputRichBlockCaption` |
| InputRichBlockAudio | audio | `media: InputRichMessageMedia, caption?: InputRichBlockCaption, credit?: InputRichBlockCaption` |
| InputRichBlockPhoto | photo | `media: InputRichMessageMedia, caption?: InputRichBlockCaption, credit?: InputRichBlockCaption` |
| InputRichBlockVideo | video | `media: InputRichMessageMedia, caption?: InputRichBlockCaption, credit?: InputRichBlockCaption` |
| InputRichBlockVoiceNote | voice_note (10.2) | `media: InputRichMessageMedia, caption?: InputRichBlockCaption` |
| InputRichBlockThinking | thinking (draft only!) | `text: string` |

### InputRichMessageMedia (10.2+)

| Field | Type | Required |
|-------|------|----------|
| type | "photo" \| "video" \| "animation" \| "audio" \| "voice_note" | Yes |
| media | string (file_id or attach://) | Yes |
| caption | InputRichBlockCaption | No |
| credit | InputRichBlockCaption | No |

### InputRichMessage

| Field | Type | Required |
|-------|------|----------|
| blocks | InputRichBlock[] | Yes |
| media | InputRichMessageMedia | No (10.2+) |

---

## Method Reference

### sendRichMessage

```http
POST /bot<token>/sendRichMessage
Content-Type: application/json

{
  "chat_id": 123456789,
  "message_thread_id": 123,          // optional
  "rich_message": { ... },           // InputRichMessage
  "disable_notification": false,     // optional
  "protect_content": false,          // optional
  "reply_parameters": { ... },       // optional
  "reply_markup": { ... }            // optional
}
```

**Response:** `Message` with `rich_message` field.

### sendRichMessageDraft

```http
POST /bot<token>/sendRichMessageDraft
Content-Type: application/json

{
  "chat_id": 123456789,
  "draft_id": 1700000000000,         // unique per stream
  "rich_message": { ... }            // InputRichMessage (partial)
}
```

**Response:** `True` on success.

### editMessageText (with rich_message)

```http
POST /bot<token>/editMessageText
Content-Type: application/json

{
  "chat_id": 123456789,
  "message_id": 987,
  "rich_message": { ... },           // InputRichMessage (final)
  "reply_markup": { ... }            // optional
}
```

### answerChatJoinRequestQuery

```http
POST /bot<token>/answerChatJoinRequestQuery
Content-Type: application/json

{
  "chat_join_request_query_id": "abc123",
  "approve": true,
  "queue": false,
  "url": "https://example.com/captcha"  // if queue=true
}
```

### sendChatJoinRequestWebApp

```http
POST /bot<token>/sendChatJoinRequestWebApp
Content-Type: application/json

{
  "chat_join_request_query_id": "abc123",
  "web_app": {
    "url": "https://example.com/captcha",
    "platform": "android" | "ios" | "desktop" | "macos" | "windows" | "linux"
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | RICH_MESSAGE_BLOCK_UNSUPPORTED - Used unsupported block (e.g., thinking in final message) |
| 400 | RICH_MESSAGE_TOO_LONG - Exceeds 32KB limit |
| 400 | INVALID_DRAFT_ID - draft_id mismatch or expired |
| 400 | RICH_MESSAGE_INVALID - Malformed rich message structure |
| 403 | BOT_BLOCKED - User blocked the bot |
| 404 | CHAT_NOT_FOUND - Invalid chat_id |

---

## Nesting Rules Summary

```
RichText (nestable):
├── bold, italic, underline, strikethrough, spoiler, marked
├── subscript, superscript
└── plain (leaf)

RichText (NOT nestable):
├── code, url, email, phone, bank_card
├── mention, hashtag, cashtag, bot_command
├── custom_emoji, math
├── anchor_link, reference_link
└── date_time

RichBlock (structural):
├── paragraph, heading, preformatted, footer, divider, math, anchor
├── list → list_item → RichBlock[] (recursive)
├── block_quote, pull_quote → RichBlock[]
├── collage → collage_item[]
├── slideshow → slideshow_item[]
├── table → table_row → table_cell
├── details → content: RichBlock[]
├── map
├── media blocks (photo, video, animation, audio, voice_note)
└── thinking (DRAFT ONLY!)
```

---

## Limits

| Parameter | Limit |
|-----------|-------|
| Max message size | 32 KB |
| Max blocks per message | ~50 (practical) |
| Max RichText nesting depth | 100 |
| Max table rows | ~100 |
| Max table columns | ~20 |
| Draft frame rate | ~10 fps (100ms) |
| Draft session timeout | ~5 minutes |
| Collage items | ~20 |
| Slideshow items | ~20 |

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| Bot API 10.0 | May 8, 2026 | Guest Mode, Chat Management, Polls, Live Photos |
| **Bot API 10.1** | **June 11, 2026** | **Rich Messages, Guardian Bots, Poll Media Links** |
| **Bot API 10.2** | **July 14, 2026** | **InputRichMessageMedia, InputMediaVoiceNote, InputRichBlockListItem** |

---

## Links

- [Bot API 10.1 Changelog](https://core.telegram.org/bots/api-changelog#june-11-2026)
- [Bot API 10.2 Changelog](https://core.telegram.org/bots/api-changelog#july-14-2026)
- [Rich Messages API](https://core.telegram.org/bots/api#rich-messages)
- [Rich Message Formatting Options](https://core.telegram.org/bots/api#rich-message-formatting-options)
- [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage)
- [sendRichMessageDraft](https://core.telegram.org/bots/api#sendrichmessagedraft)
- [Guardian Bots](https://core.telegram.org/bots/api#chatjoinrequest)
- [Interactive Demo](https://t.me/richtextdemobot)