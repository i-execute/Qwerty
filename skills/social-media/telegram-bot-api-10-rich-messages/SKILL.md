---
name: telegram-bot-api-10-rich-messages
description: "Complete reference for Telegram Bot API 10.1/10.2 Rich Messages - block-based formatting, inline rich text, streaming drafts, media blocks, tables, LaTeX, maps, collages, slideshows, and Guardian Bots"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, bot-api, rich-messages, bot-api-10.1, bot-api-10.2, sendRichMessage, sendRichMessageDraft, formatting]
    related_skills: [telegram-rich-messages, xurl, github-issues]
---

# Telegram Bot API 10.1/10.2 Rich Messages Skill

## Overview

**Bot API 10.1 (June 11, 2026)** introduced **Rich Messages** — a block-based formatting system that replaces simple HTML/Markdown with structured objects for highly formatted messages.

**Bot API 10.2 (July 14, 2026)** added media specification (`InputRichMessageMedia`), voice notes (`InputMediaVoiceNote`), and list item inputs (`InputRichBlockListItem`).

### Key Concepts

| Concept | Description |
|---------|-------------|
| **RichText** | Inline formatted text entities (bold, italic, code, math, links, mentions, etc.) |
| **RichBlock** | Structural blocks (paragraph, heading, table, list, media, quote, details, map, collage, slideshow, thinking) |
| **InputRichMessage** | Container for sending rich messages (blocks + optional media) |
| **sendRichMessage** | Method to send a complete rich message |
| **sendRichMessageDraft** | Method to stream partial rich messages (animated typing) |
| **editMessageText** | Now supports `rich_message` parameter for editing |

---

## Rich Text Types (Inline Formatting)

All inline entities extend `RichText` base type with `type` field.

| Type | Class | Fields | Description |
|------|-------|--------|-------------|
| **bold** | `RichTextBold` | `text: RichText[]` | Bold text |
| **italic** | `RichTextItalic` | `text: RichText[]` | Italic text |
| **underline** | `RichTextUnderline` | `text: RichText[]` | Underlined text |
| **strikethrough** | `RichTextStrikethrough` | `text: RichText[]` | Strikethrough text |
| **spoiler** | `RichTextSpoiler` | `text: RichText[]` | Spoiler (tap to reveal) |
| **code** | `RichTextCode` | `text: string` | Inline monospace code |
| **subscript** | `RichTextSubscript` | `text: RichText[]` | Subscript text |
| **superscript** | `RichTextSuperscript` | `text: RichText[]` | Superscript text |
| **marked** | `RichTextMarked` | `text: RichText[]` | Highlighted/marked text |
| **url** | `RichTextUrl` | `text: RichText[], url: string` | Hyperlink |
| **email** | `RichTextEmailAddress` | `text: RichText[], email: string` | Email link |
| **phone** | `RichTextPhoneNumber` | `text: RichText[], phone_number: string` | Phone link |
| **bank_card** | `RichTextBankCardNumber` | `text: RichText[], number: string` | Bank card link |
| **mention** | `RichTextMention` | `text: RichText[], user: User` | User mention |
| **hashtag** | `RichTextHashtag` | `text: RichText[], hashtag: string` | Hashtag link |
| **cashtag** | `RichTextCashtag` | `text: RichText[], cashtag: string` | Cashtag ($SYMBOL) |
| **bot_command** | `RichTextBotCommand` | `text: RichText[], command: string` | Bot command |
| **custom_emoji** | `RichTextCustomEmoji` | `text: string, custom_emoji_id: string` | Custom emoji |
| **math** | `RichTextMathematicalExpression` | `text: string` | Inline LaTeX math |
| **anchor** | `RichTextAnchor` | `name: string` | Document anchor |
| **anchor_link** | `RichTextAnchorLink` | `text: RichText[], anchor_name: string` | Link to anchor |
| **reference** | `RichTextReference` | `text: RichText[], reference_id: string` | Footnote reference |
| **reference_link** | `RichTextReferenceLink` | `text: RichText[], reference_id: string` | Footnote link |
| **date_time** | `RichTextDateTime` | `text: RichText[], timestamp: int` | Formatted timestamp |

### Nesting Rules
- Bold, italic, underline, strikethrough, spoiler, marked, subscript, superscript can nest **arbitrarily deep**
- Code, url, email, phone, bank_card, mention, hashtag, cashtag, bot_command, custom_emoji, math, anchor_link, reference_link **cannot contain other entities**
- Anchor, date_time are leaf nodes

---

## Rich Block Types (Structural)

All blocks extend `RichBlock` with `type` field.

| Type | Class | Key Fields | Description |
|------|-------|------------|-------------|
| **paragraph** | `RichBlockParagraph` | `content: RichText[]` | Text paragraph |
| **section_heading** | `RichBlockSectionHeading` | `level: 1-6, content: RichText[]` | Heading H1-H6 |
| **preformatted** | `RichBlockPreformatted` | `content: RichText[], language?: string` | Code block with syntax highlighting |
| **footer** | `RichBlockFooter` | `content: RichText[]` | Footer text |
| **divider** | `RichBlockDivider` | — | Horizontal rule |
| **math** | `RichBlockMathematicalExpression` | `content: string` | Block LaTeX math |
| **anchor** | `RichBlockAnchor` | `name: string` | Document anchor |
| **list** | `RichBlockList` | `items: RichBlockListItem[], ordered: bool, numeral: string` | Bullet/numbered/task list |
| **list_item** | `RichBlockListItem` | `prefix: RichText[], content: RichBlock[]` | List item with nested blocks |
| **block_quote** | `RichBlockBlockQuotation` | `content: RichBlock[], citation?: RichText[]` | Block quote |
| **pull_quote** | `RichBlockPullQuotation` | `content: RichBlock[], citation?: RichText[]` | Pull quote (highlighted) |
| **collage** | `RichBlockCollage` | `items: RichBlockCollageItem[]` | Media grid |
| **slideshow** | `RichBlockSlideshow` | `items: RichBlockSlideshowItem[]` | Swipeable media carousel |
| **table** | `RichBlockTable` | `rows: RichBlockTableRow[], caption?: RichBlockCaption, bordered: bool, striped: bool` | Table with formatting |
| **details** | `RichBlockDetails` | `summary: RichText[], content: RichBlock[], open: bool` | Collapsible section |
| **map** | `RichBlockMap` | `location: Location, zoom?: int` | Map with pin |
| **animation** | `RichBlockAnimation` | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` | GIF/animation |
| **audio** | `RichBlockAudio` | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` | Audio file |
| **photo** | `RichBlockPhoto` | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` | Photo |
| **video** | `RichBlockVideo` | `media: InputRichMessageMedia, caption?: RichBlockCaption, credit?: RichBlockCaption` | Video |
| **voice_note** | `RichBlockVoiceNote` | `media: InputRichMessageMedia, caption?: RichBlockCaption` | Voice message (10.2) |
| **thinking** | `RichBlockThinking` | `text: string` | AI thinking animation (draft only!) |

### Table Structure
```json
{
  "type": "table",
  "rows": [
    { "type": "table_row", "cells": [
      { "type": "table_cell", "content: RichText[], "header": true, "align": "center", "colspan": 1, "rowspan": 1 },
      { "type": "table_cell", "content: RichText[], "header": false, "align": "left" }
    ]}
  ],
  "caption": { "type": "caption", "content": [...] },
  "bordered": true,
  "striped": true
}
```
- `align`: "left" \| "center" \| "right"
- `header`: boolean for header cells
- `colspan`/`rowspan`: merging cells

### List Structure
```json
{
  "type": "list",
  "items": [
    { "type": "list_item", "prefix": [...], "content": [ { "type": "paragraph", ... } ] }
  ],
  "ordered": true,
  "numeral": "1" | "a" | "A" | "i" | "I"
}
```

---

## Input Types (For Sending)

Use `InputRichMessage` with `sendRichMessage` / `sendRichMessageDraft`.

```json
{
  "blocks": [ /* RichBlock objects - use InputRichBlock* variants */ ],
  "media": { /* InputRichMessageMedia - optional, for 10.2+ */ }
}
```

### InputRichBlock Variants
| Input Class | For Block Type |
|-------------|----------------|
| `InputRichBlockParagraph` | paragraph |
| `InputRichBlockSectionHeading` | section_heading |
| `InputRichBlockPreformatted` | preformatted |
| `InputRichBlockFooter` | footer |
| `InputRichBlockDivider` | divider |
| `InputRichBlockMathematicalExpression` | math |
| `InputRichBlockAnchor` | anchor |
| `InputRichBlockList` | list |
| `InputRichBlockBlockQuotation` | block_quote |
| `InputRichBlockPullQuotation` | pull_quote |
| `InputRichBlockCollage` | collage |
| `InputRichBlockSlideshow` | slideshow |
| `InputRichBlockTable` | table |
| `InputRichBlockDetails` | details |
| `InputRichBlockMap` | map |
| `InputRichBlockAnimation` | animation |
| `InputRichBlockAudio` | audio |
| `InputRichBlockPhoto` | photo |
| `InputRichBlockVideo` | video |
| `InputRichBlockVoiceNote` | voice_note (10.2) |
| `InputRichBlockThinking` | thinking (draft only!) |

### InputRichMessageMedia (Bot API 10.2+)
Explicitly specify media for rich messages:
```json
{
  "media": {
    "type": "photo" | "video" | "animation" | "audio" | "voice_note",
    "media": "file_id" | "attach://...",
    "caption": { /* RichBlockCaption */ },
    "credit": { /* RichBlockCaption */ }
  }
}
```

---

## Methods

### sendRichMessage
```json
POST /sendRichMessage
{
  "chat_id": 123456789,
  "rich_message": { /* InputRichMessage */ },
  "message_thread_id": 123,
  "disable_notification": false,
  "protect_content": false,
  "reply_parameters": { /* ReplyParameters */ },
  "reply_markup": { /* InlineKeyboardMarkup */ }
}
```
Returns `Message` with `rich_message` field populated.

### sendRichMessageDraft (Streaming)
```json
POST /sendRichMessageDraft
{
  "chat_id": 123456789,
  "draft_id": 1700000000000,
  "rich_message": { /* InputRichMessage - partial */ }
}
```
- **draft_id**: Unique per streaming session (use timestamp ms)
- Send multiple frames with same `draft_id` to animate
- **Critical**: `RichBlockThinking` ONLY works in drafts!
- Final message: call `sendRichMessage` or `editMessageText` with `rich_message` (WITHOUT thinking block)

### editMessageText (Rich Editing)
```json
POST /editMessageText
{
  "chat_id": 123456789,
  "message_id": 987,
  "rich_message": { /* InputRichMessage - final version */ }
}
```
- Replaces message with new rich content
- **Do NOT include** `RichBlockThinking` in final edit

---

## Guardian Bots (Bot API 10.1)

Handle chat join requests programmatically.

| Method | Description |
|--------|-------------|
| `answerChatJoinRequestQuery` | Approve/decline/queue join request |
| `sendChatJoinRequestWebApp` | Open Mini App for captcha/verification |

### answerChatJoinRequestQuery
```json
POST /answerChatJoinRequestQuery
{
  "chat_join_request_query_id": "abc123",
  "approve": true | false,
  "queue": false,
  "url": "https://example.com/captcha" // if queue=true
}
```

### sendChatJoinRequestWebApp
```json
POST /sendChatJoinRequestWebApp
{
  "chat_join_request_query_id": "abc123",
  "web_app": { "url": "https://example.com/captcha", "platform": "android" }
}
```

---

## Polls Updates (Bot API 10.1)

- `PollMedia` now has `link: Link` field (external URL for poll option media)
- `InputMediaLink` can be used as `InputPollOptionMedia`
- Allows poll options to link to any website

---

## Complete Example: AI Streaming Response

```python
import asyncio
import aiohttp
import time

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = 123456789

async def stream_ai_response(session, bot_token, chat_id, text_chunks):
    draft_id = int(time.time() * 1000)
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"

    # Initial frame with thinking
    await session.post(url, json={
        "chat_id": chat_id,
        "draft_id": draft_id,
        "rich_message": {
            "blocks": [
                {"type": "thinking", "text": "Thinking..."}
            ]
        }
    })

    accumulated = ""
    for chunk in text_chunks:
        accumulated += chunk
        await session.post(url, json={
            "chat_id": chat_id,
            "draft_id": draft_id,
            "rich_message": {
                "blocks": [
                    {"type": "thinking", "text": "Generating..."},
                    {"type": "paragraph", "content": [{"type": "plain", "text": accumulated}]}
                ]
            }
        })
        await asyncio.sleep(0.1)

    # Final message (no thinking block!)
    final_url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    await session.post(final_url, json={
        "chat_id": chat_id,
        "rich_message": {
            "blocks": [
                {"type": "paragraph", "content": [{"type": "plain", "text": accumulated}]}
            ]
        }
    })
```

---

## Complete Example: Business Report

```json
{
  "blocks": [
    { "type": "section_heading", "level": 1, "content": [{ "type": "bold", "text": [{ "type": "plain", "text": "Q3 2026 Report" }] }] },
    { "type": "divider" },
    { "type": "paragraph", "content": [
      { "type": "plain", "text": "Revenue grew " },
      { "type": "bold", "text": [{ "type": "plain", "text": "23%" }] },
      { "type": "plain", "text": " YoY to " },
      { "type": "marked", "text": [{ "type": "plain", "text": "$4.2M" }] }
    ]},
    { "type": "table", "bordered": true, "striped": true, "caption": { "type": "caption", "content": [{ "type": "italic", "text": [{ "type": "plain", "text": "Quarterly breakdown" }] }], "rows": [
      { "type": "table_row", "cells": [
        { "type": "table_cell", "header": true, "align": "center", "content": [{ "type": "plain", "text": "Metric" }] },
        { "type": "table_cell", "header": true, "align": "center", "content": [{ "type": "plain", "text": "Q2" }] },
        { "type": "table_cell", "header": true, "align": "center", "content": [{ "type": "plain", "text": "Q3" }] },
        { "type": "table_cell", "header": true, "align": "center", "content": [{ "type": "plain", "text": "Δ" }] }
      ]},
      { "type": "table_row", "cells": [
        { "type": "table_cell", "content": [{ "type": "bold", "text": [{ "type": "plain", "text": "Revenue" }] }] },
        { "type": "table_cell", "align": "right", "content": [{ "type": "plain", "text": "$3.4M" }] },
        { "type": "table_cell", "align": "right", "content": [{ "type": "marked", "text": [{ "type": "plain", "text": "$4.2M" }] }] },
        { "type": "table_cell", "align": "center", "content": [{ "type": "bold", "text": [{ "type": "plain", "text": "+23%" }] }] }
      ]}
    ]},
    { "type": "details", "open": false, "summary": [{ "type": "plain", "text": "Methodology" }], "content": [
      { "type": "paragraph", "content": [{ "type": "plain", "text": "Data sourced from internal analytics..." }] }
    ]},
    { "type": "math", "content": "\\sum_{i=1}^{n} R_i = R_{total}" },
    { "type": "footer", "content": [{ "type": "plain", "text": "Confidential — Internal Use Only" }] }
  ]
}
```

---

## LaTeX Math Support

- **Inline**: `RichTextMathematicalExpression` with `text: "$E=mc^2$"`
- **Block**: `RichBlockMathematicalExpression` with `content: "$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$"`
- Uses KaTeX rendering
- Supports most LaTeX math commands

---

## Limits & Constraints

| Limit | Value |
|-------|-------|
| Max rich message size | 32 KB (same as regular message) |
| Max blocks per message | ~50 (practical) |
| Max nesting depth | 100 (rich text) |
| Draft frame rate | ~10 fps recommended (100ms/frame) |
| `RichBlockThinking` | **Drafts only** — causes `RICH_MESSAGE_BLOCK_UNSUPPORTED` in final |

---

## Migration from HTML/MarkdownV2

| Old | New (Rich) |
|-----|------------|
| `<b>bold</b>` | `RichTextBold` |
| `<i>italic</i>` | `RichTextItalic` |
| `<code>code</code>` | `RichTextCode` |
| `<pre>code</pre>` | `RichBlockPreformatted` |
| `<a href="...">link</a>` | `RichTextUrl` |
| `<table>...</table>` | `RichBlockTable` |
| `<details><summary>...</summary></details>` | `RichBlockDetails` |
| `$$math$$` | `RichBlockMathematicalExpression` |
| `> quote` | `RichBlockBlockQuotation` |
| `---` | `RichBlockDivider` |
| `1. item` | `RichBlockList (ordered: true)` |
| `- [ ] task` | `RichBlockList (ordered: false, with checkbox prefix)` |

---

## Python Helpers (Reference Implementation)

```python
# rich_builders.py
from typing import List, Any, Optional
from dataclasses import dataclass, field

def plain(text: str) -> dict:
    return {"type": "plain", "text": text}

def bold(*content) -> dict:
    return {"type": "bold", "text": list(content)}

def italic(*content) -> dict:
    return {"type": "italic", "text": list(content)}

def code(text: str) -> dict:
    return {"type": "code", "text": text}

def url(text: str, url: str) -> dict:
    return {"type": "url", "text": [plain(text)], "url": url}

def math_inline(latex: str) -> dict:
    return {"type": "math", "text": latex}

def paragraph(*content) -> dict:
    return {"type": "paragraph", "content": list(content)}

def heading(level: int, *content) -> dict:
    return {"type": "section_heading", "level": level, "content": list(content)}

def divider() -> dict:
    return {"type": "divider"}

def preformatted(code: str, lang: str = "") -> dict:
    return {"type": "preformatted", "content": [plain(code)], "language": lang}

def math_block(latex: str) -> dict:
    return {"type": "math", "content": latex}

def table(rows: List[List[Any]], headers: List[str] = None, caption: str = "", bordered: bool = True, striped: bool = True) -> dict:
    def cell(content, header=False, align="left"):
        return {"type": "table_cell", "content": [plain(str(content))] if isinstance(content, str) else content, "header": header, "align": align}

    table_rows = []
    if headers:
        table_rows.append({"type": "table_row", "cells": [cell(h, header=True, align="center") for h in headers]})
    for row in rows:
        table_rows.append({"type": "table_row", "cells": [cell(c) for c in row]})

    result = {"type": "table", "rows": table_rows, "bordered": bordered, "striped": striped}
    if caption:
        result["caption"] = {"type": "caption", "content": [plain(caption)]}
    return result

def details(summary: str, *blocks) -> dict:
    return {"type": "details", "summary": [plain(summary)], "content": list(blocks), "open": False}

def thinking(text: str = "Thinking...") -> dict:
    return {"type": "thinking", "text": text}

def build_message(*blocks) -> dict:
    return {"blocks": list(blocks)}
```

---

## References

- [Bot API 10.1 Changelog (June 11, 2026)](https://core.telegram.org/bots/api-changelog#june-11-2026)
- [Bot API 10.2 Changelog (July 14, 2026)](https://core.telegram.org/bots/api-changelog#july-14-2026)
- [Rich Messages Documentation](https://core.telegram.org/bots/api#rich-messages)
- [Rich Message Formatting Options](https://core.telegram.org/bots/api#rich-message-formatting-options)
- [sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage)
- [sendRichMessageDraft](https://core.telegram.org/bots/api#sendrichmessagedraft)
- [Interactive Demo Bot](https://t.me/richtextdemobot)
- [Guardian Bots](https://core.telegram.org/bots/api#chatjoinrequest)
- [Poll Media Links](https://core.telegram.org/bots/api#link)

---

## Related Hermes Skills

- `telegram-rich-messages` — Hermes-specific adapter usage
- `xurl` — X/Twitter posting
- `github-issues` — GitHub issue management