---
name: telegram-custom-emoji
description: "Telegram Custom Emoji IDs for Rich Messages - Ready-to-use RichTextCustomEmoji objects for Bot API 10.1+"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, custom-emoji, rich-messages, bot-api-10.1]
    related_skills: [telegram-rich-messages, telegram-bot-api-10-rich-messages, telegram-bot-api-10-2]
---

# Telegram Custom Emoji for Rich Messages

## Overview

**Bot API 10.1+** supports custom emojis in Rich Messages via `RichTextCustomEmoji` (inline entity).

**Format:** `{"type": "custom_emoji", "text": "😀", "custom_emoji_id": "5334882760735598374"}`

**NOT HTML `<tg-emoji emoji-id="...">`** — that's for regular messages only.

---

## Available Emoji IDs (from your collection)

| Emoji | ID | RichTextCustomEmoji Object |
|-------|-----|---------------------------|
| 😌 | 5449619723966761441 | `custom_emoji("😌", "5449619723966761441")` |
| 😏 | 5384214488809490070 | `custom_emoji("😏", "5384214488809490070")` |
| 😂 | 5298937724168853193 | `custom_emoji("😂", "5298937724168853193")` |
| 😂 | 5384478698017670587 | `custom_emoji("😂", "5384478698017670587")` |
| 😁 | 5296786967755771785 | `custom_emoji("😁", "5296786967755771785")` |
| 👌 | 5447363161034346459 | `custom_emoji("👌", "5447363161034346459")` |
| 🥲 | 5190491238758898985 | `custom_emoji("🥲", "5190491238758898985")` |
| 🥲 | 5298524385106218208 | `custom_emoji("🥲", "5298524385106218208")` |
| 😊 | 5190867898800821266 | `custom_emoji("😊", "5190867898800821266")` |
| ☺️ | 5298812156504987574 | `custom_emoji("☺️", "5298812156504987574")` |
| 😌 | 5447526417036234763 | `custom_emoji("😌", "5447526417036234763")` |
| 🤩 | 5190683945351535076 | `custom_emoji("🤩", "5190683945351535076")` |
| 😌 | 5211101893459199876 | `custom_emoji("😌", "5211101893459199876")` |
| 🫤 | 5384453284696181912 | `custom_emoji("🫤", "5384453284696181912")` |
| 😗 | 5296335880225575986 | `custom_emoji("😗", "5296335880225575986")` |
| 😙 | 5447193685919811994 | `custom_emoji("😙", "5447193685919811994")` |
| 🤨 | 5384294976496619218 | `custom_emoji("🤨", "5384294976496619218")` |
| 🤷‍♂️ | 5211112038171958439 | `custom_emoji("🤷‍♂️", "5211112038171958439")` |

**Bonus (from your last message):**
| Emoji | ID (approx) | Note |
|-------|-------------|------|
| 💯 | — | Standard Unicode |
| ⛺️ | — | Standard Unicode |
| 🗿 | — | Standard Unicode |
| 👠 | — | Standard Unicode |
| 🍿 | — | Standard Unicode |

---

## Usage in Rich Messages

### Python Helper

```python
from skills.social_media.telegram_custom_emoji.references.emoji_helpers import custom_emoji, CE

# Single emoji
ce = custom_emoji("😎", "5334882760735598374")

# In paragraph
paragraph(
    plain("Hello "),
    CE.cool,  # predefined
    plain(" world!")
)

# In heading
heading(1, bold(plain("Title ")), CE.party)
```

### Raw JSON (for sendRichMessage)

```json
{
  "type": "paragraph",
  "content": [
    {"type": "plain", "text": "Status: "},
    {"type": "custom_emoji", "text": "😎", "custom_emoji_id": "5334882760735598374"},
    {"type": "plain", "text": " Done!"}
  ]
}
```

---

## Important Notes

1. **Custom emoji IDs are per-sticker-pack** — must be from a pack your bot has access to
2. **Fallback text** (`text` field) shows if emoji fails to load
3. **Only in RichText** — not in block-level content directly
4. **Nesting**: Can be inside bold/italic/etc. but NOT inside code/url/mention

---

## Quick Reference Dict

```python
EMOJI_IDS = {
    "relieved_1": "5449619723966761441",
    "smirk": "5384214488809490070",
    "joy_1": "5298937724168853193",
    "joy_2": "5384478698017670587",
    "grin": "5296786967755771785",
    "ok_hand": "5447363161034346459",
    "smiling_tear_1": "5190491238758898985",
    "smiling_tear_2": "5298524385106218208",
    "smile": "5190867898800821266",
    "relaxed": "5298812156504987574",
    "relieved_2": "5447526417036234763",
    "star_struck": "5190683945351535076",
    "relieved_3": "5211101893459199876",
    "neutral_face": "5384453284696181912",
    "kissing": "5296335880225575986",
    "kissing_smiling": "5447193685919811994",
    "raised_eyebrow": "5384294976496619218",
    "shrug": "5211112038171958439",
}
```