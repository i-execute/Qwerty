---
name: telegram-rich-custom-emoji
description: "Use Telegram Rich Messages with the user's verified premium custom emoji registry."
version: 2.1.0
author: Hermes Agent
license: MIT
---

# Telegram Rich Replies + Premium Custom Emoji

## Required reply policy

For every Telegram reply to this user, use Rich Messages by default and use **only premium custom emoji entities whose IDs appear in the authoritative registry below**. Ordinary Unicode emoji are forbidden in reply content, including as fallbacks: every visible emoji glyph must be represented by its matching `custom_emoji_id` from the registry. Never invent IDs, never use an unlisted emoji, and never send separate test/double messages. Use registry entities inline in headings, tables, status labels, and prose as appropriate.

The Telegram adapter promotes its configured Unicode glyphs into premium Rich Markdown entities. For a raw Bot API Rich Message, use:

```md
![🤩](tg://emoji?id=5190683945351535076)
```

Do not use `<tg-emoji>` tags in Rich Messages. Use normal Markdown tables and LaTex ($E = mc^2$) for Rich formatting.

## Authoritative registry — uploaded `allidemoji.txt`

**Parsed exactly from the file: 99 unique `emoji-id` values.** Some source text was duplicated; only the first occurrence of an ID is retained.

| Custom emoji ID | Fallback |
|---|---|
| `5449619723966761441` | 😌 |
| `5384214488809490070` | 😏 |
| `5298937724168853193` | 😂 |
| `5384478698017670587` | 😂 |
| `5296786967755771785` | 😁 |
| `5447363161034346459` | 👌 |
| `5190491238758898985` | 🥲 |
| `5298524385106218208` | 🥲 |
| `5190867898800821266` | 😊 |
| `5298812156504987574` | ☺️ |
| `5447526417036234763` | 😌 |
| `5190683945351535076` | 🤩 |
| `5211101893459199876` | 😌 |
| `5384453284696181912` | 🫤 |
| `5296335880225575986` | 😗 |
| `5447193685919811994` | 😙 |
| `5384294976496619218` | 🤨 |
| `5211112038171958439` | 🤷‍♂️ |
| `5190568977666957657` | 🙅‍♂️ |
| `5296739894914207637` | 🤔 |
| `5296383305254459545` | 🔫 |
| `5190768942754324589` | 😏 |
| `5384182985224374928` | 🧐 |
| `5190783670197180086` | 🤨 |
| `5447271394763099136` | 🤔 |
| `5210985766133453153` | 🤔 |
| `5296525713485089826` | 😱 |
| `5210808229365305258` | 😫 |
| `5384157249780337109` | 😑 |
| `5447610314927396099` | 🧐 |
| `5296732718023857804` | 🦶 |
| `5193200486949346651` | 😞 |
| `5192781392630537817` | 🔫 |
| `5190415054629002671` | 🤐 |
| `5210890383499745988` | 😑 |
| `5192857499451021759` | 😳 |
| `5447348871678154623` | 😐 |
| `5210997160681688876` | 🫵 |
| `5296305622180972936` | 😡 |
| `5384059066827949054` | 😒 |
| `5298519909750296720` | 😋 |
| `5193133348020574567` | 😋 |
| `5447198809815795961` | 👅 |
| `5299006615444278021` | 😝 |
| `5447630192036040634` | 🫦 |
| `5211042257838296209` | 😚 |
| `5447432125324216825` | 🍆 |
| `5190958793193710110` | 😬 |
| `5384187537889710348` | 😬 |
| `5296250904297624056` | 💩 |
| `5213305791502634699` | 😮 |
| `5210918605729843558` | 🍆 |
| `5316742244806451762` | 🧱 |
| `5298854260069389723` | 💨 |
| `5447163161587241349` | 🤯 |
| `5384285987130065744` | 🩸 |
| `5298775778131986041` | 🦠 |
| `5190660975866437599` | 🫠 |
| `5384108682290152083` | 🧊 |
| `5384495396850520754` | 🔪 |
| `5210952531676516344` | 👑 |
| `5296365472550244967` | 👉 |
| `5447191366637476040` | 🧛‍♂️ |
| `5384268407828924341` | 🤠 |
| `5211042502651432248` | 🍩 |
| `5316885872807794414` | 🌰 |
| `5213447602732813642` | 💞 |
| `5316965570220941367` | 🧼 |
| `5192966772008966700` | 🖕 |
| `5210972980015810506` | 🦶 |
| `5193037226652491753` | 🤟 |
| `5296691786985527033` | 💪 |
| `5190640291303939012` | 🖕 |
| `5192808914780971277` | 🐺 |
| `5213311533873907167` | 🐈‍⬛ |
| `5447456593752903617` | 🐲 |
| `5447614579829921377` | 🍑 |
| `5211025120918785460` | 🍆 |
| `5211155151053675393` | 🍆 |
| `5314647211299067950` | 🍌 |
| `5316870406630564710` | 🍩 |
| `5316715774923004572` | ❤️ |
| `5190742593129971422` | 💔 |
| `5210767689168999246` | 💘 |
| `5190775904896308220` | 💔 |
| `5210777181046722111` | 💔 |
| `5384443861537932638` | 🥔 |
| `5447595110743168717` | 🧠 |
| `5314806674844835288` | ☕️ |
| `5316645728301374271` | ☕️ |
| `5296426834748002089` | 🫁 |
| `5193157563046189671` | 🧻 |
| `5317054012187499321` | 💰 |
| `5190404278556055959` | 🪤 |
| `5447458260200214425` | 💸 |
| `5382199784075448966` | 💸 |
| `5190682871609712455` | 💀 |
| `5193012388856618565` | 🩻 |
| `5192784923093652913` | 📅 |

## Selection guide

| Use case | Preferred glyphs |
|---|---|
| Completion / positive outcome | 🤩, 😌, 😊, 👌 |
| Analysis / uncertainty | 🧠, 🤔, 🧐, 🫤 |
| Schedule / money | 📅, 💰, 💸 |
| Warning / failure | 😱, 😫, 😞, 😑 |
| Friendly chat | 😏, 😂, 😁, 💞 |

## Constraints

- Use exact fallback glyphs shown in the registry only when the same glyph is emitted as a `custom_emoji` entity with its listed ID.
- **Never emit bare Unicode emoji** in a reply, table, heading, code, or prose.
- Do not use variation-selector variants not present in the registry.
- Do not use `✅`, `❌`, `➡️`, `⬇️`, or any unlisted decorative emoji.
- Emoji must remain inline in prose/table cells, not standalone rich blocks.
