---
name: telegram-rich-gateway
description: "Complete Telegram Bot API 10.2 rich messaging guide: 103 premium custom emoji registry, LaTeX math, markdown tables, blockquotes, code blocks, lists, dropdowns, streaming drafts, and verified gateway deployment."
version: 3.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, rich-messages, bot-api, custom-emoji, latex, gateway]
    related_skills: [telegram-rich-messages, telegram-rich-custom-emoji]
---

# Telegram Rich Gateway — Complete Rich Messages + Premium Emoji Guide

**STATUS:** Consolidated skill for **gateway-only Telegram communication**. ALWAYS use this skill's formatting rules for every reply through `gateway.platforms.telegram`.

---

## 🧠 Executive Summary

- **Emoji:** Use **ONLY** the 103 verified premium custom emoji IDs below — never bare Unicode
- **Markdown:** Rich formatting via **Markdown + HTML** blocks in rich messages
- **Math:** LaTeX support via `$...$` (inline) and `$$...$$` (block)
- **Tables:** HTML `<table>` syntax in rich messages for structured data
- **Streaming:** `sendRichMessageDraft` for animated progression + thinking animations
- **Scope:** Every Telegram reply through gateway adapter must follow these rules

---

## 🎭 Premium Custom Emoji Registry (103 Total)

**Source:** Verified from user's Telegram premium emoji library. These IDs render correctly and must be used exclusively.

### All 103 Emoji (organized by category)

| ID | Glyph | Category |
|----|-------|----------|
| `5449619723966761441` | 😌 | Positive |
| `5384214488809490070` | 😏 | Neutral |
| `5298937724168853193` | 😂 | Happy |
| `5384478698017670587` | 😂 | Happy |
| `5296786967755771785` | 😁 | Happy |
| `5447363161034346459` | 👌 | Positive |
| `5190491238758898985` | 🥲 | Positive |
| `5298524385106218208` | 🥲 | Positive |
| `5190867898800821266` | 😊 | Positive |
| `5298812156504987574` | ☺️ | Positive |
| `5447526417036234763` | 😌 | Positive |
| `5190683945351535076` | 🤩 | Impressed |
| `5211101893459199876` | 😌 | Positive |
| `5384453284696181912` | 🫤 | Uncertain |
| `5296335880225575986` | 😗 | Friendly |
| `5447193685919811994` | 😙 | Friendly |
| `5384294976496619218` | 🤨 | Thinking |
| `5211112038171958439` | 🤷‍♂️ | Uncertain |
| `5190568977666957657` | 🙅‍♂️ | Negative |
| `5296739894914207637` | 🤔 | Analysis |
| `5296383305254459545` | 🔫 | Action |
| `5190768942754324589` | 😏 | Neutral |
| `5384182985224374928` | 🧐 | Analysis |
| `5190783670197180086` | 🤨 | Thinking |
| `5447271394763099136` | 🤔 | Analysis |
| `5210985766133453153` | 🤔 | Analysis |
| `5296525713485089826` | 😱 | Shock |
| `5210808229365305258` | 😫 | Tired |
| `5384157249780337109` | 😑 | Neutral |
| `5447610314927396099` | 🧐 | Analysis |
| `5296732718023857804` | 🦶 | Body |
| `5193200486949346651` | 😞 | Sad |
| `5192781392630537817` | 🔫 | Action |
| `5190415054629002671` | 🤐 | Silent |
| `5210890383499745988` | 😑 | Neutral |
| `5192857499451021759` | 😳 | Surprised |
| `5447348871678154623` | 😐 | Neutral |
| `5210997160681688876` | 🫵 | Pointing |
| `5296305622180972936` | 😡 | Angry |
| `5384059066827949054` | 😒 | Skeptical |
| `5298519909750296720` | 😋 | Tasty |
| `5193133348020574567` | 😋 | Tasty |
| `5447198809815795961` | 👅 | Taste |
| `5299006615444278021` | 😝 | Playful |
| `5447630192036040634` | 🫦 | Mouth |
| `5211042257838296209` | 😚 | Kiss |
| `5447432125324216825` | 🍆 | Food |
| `5190958793193710110` | 😬 | Nervous |
| `5384187537889710348` | 😬 | Nervous |
| `5296250904297624056` | 💩 | Negative |
| `5213305791502634699` | 😮 | Surprised |
| `5210918605729843558` | 🍆 | Food |
| `5316742244806451762` | 🧱 | Object |
| `5298854260069389723` | 💨 | Effect |
| `5447163161587241349` | 🤯 | Mind |
| `5384285987130065744` | 🩸 | Medical |
| `5298775778131986041` | 🦠 | Medical |
| `5190660975866437599` | 🫠 | Melting |
| `5384108682290152083` | 🧊 | Cold |
| `5384495396850520754` | 🔪 | Weapon |
| `5210952531676516344` | 👑 | Status |
| `5296365472550244967` | 👉 | Pointing |
| `5447191366637476040` | 🧛‍♂️ | Monster |
| `5384268407828924341` | 🤠 | Hat |
| `5211042502651432248` | 🍩 | Food |
| `5316885872807794414` | 🌰 | Food |
| `5213447602732813642` | 💞 | Love |
| `5316965570220941367` | 🧼 | Clean |
| `5192966772008966700` | 🖕 | Gesture |
| `5210972980015810506` | 🦶 | Body |
| `5193037226652491753` | 🤟 | Gesture |
| `5296691786985527033` | 💪 | Power |
| `5190640291303939012` | 🖕 | Gesture |
| `5192808914780971277` | 🐺 | Animal |
| `5213311533873907167` | 🐈‍⬛ | Animal |
| `5447456593752903617` | 🐲 | Animal |
| `5447614579829921377` | 🍑 | Food |
| `5211025120918785460` | 🍆 | Food |
| `5211155151053675393` | 🍆 | Food |
| `5314647211299067950` | 🍌 | Food |
| `5316870406630564710` | 🍩 | Food |
| `5316715774923004572` | ❤️ | Love |
| `5190742593129971422` | 💔 | Love |
| `5210767689168999246` | 💘 | Love |
| `5190775904896308220` | 💔 | Love |
| `5210777181046722111` | 💔 | Love |
| `5384443861537932638` | 🥔 | Food |
| `5447595110743168717` | 🧠 | Analysis |
| `5314806674844835288` | ☕️ | Drink |
| `5316645728301374271` | ☕️ | Drink |
| `5296426834748002089` | 🫁 | Medical |
| `5193157563046189671` | 🧻 | Object |
| `5317054012187499321` | 💰 | Money |
| `5190404278556055959` | 🪤 | Trap |
| `5447458260200214425` | 💸 | Money |
| `5382199784075448966` | 💸 | Money |
| `5190682871609712455` | 💀 | Death |
| `5193012388856618565` | 🩻 | Medical |
| `5192784923093652913` | 📅 | Schedule |
| `5384182740411240426` | 💯 | Perfect |
| `5193143651647117966` | ⛺️ | Camping |
| `5190458429503723474` | 🗿 | Monument |
| `5190691671997702118` | 👠 | Fashion |

### Quick Emoji Selection by Use Case

| Use Case | Emoji IDs | Glyphs |
|----------|-----------|--------|
| **Success/Completion** | `5190683945351535076`, `5449619723966761441`, `5190867898800821266`, `5447363161034346459` | 🤩, 😌, 😊, 👌 |
| **Analysis/Thinking** | `5296739894914207637`, `5447271394763099136`, `5384182985224374928`, `5447595110743168717` | 🤔, 🤔, 🧐, 🧠 |
| **Warning/Error** | `5296525713485089826`, `5210808229365305258`, `5193200486949346651`, `5384157249780337109` | 😱, 😫, 😞, 😑 |
| **Money/Time** | `5317054012187499321`, `5447458260200214425`, `5192784923093652913` | 💰, 💸, 📅 |
| **Friendly Chat** | `5384214488809490070`, `5298937724168853193`, `5296786967755771785`, `5213447602732813642` | 😏, 😂, 😁, 💞 |
| **Perfect/Ideal** | `5384182740411240426` | 💯 |

---

## 📝 Markdown Formatting in Rich Messages

### **Supported Markdown Syntax** (convert to HTML by adapter)

| Markdown | HTML Equivalent | Rendered Result |
|----------|-----------------|-----------------|
| `**bold**` | `<b>bold</b>` | **bold** |
| `*italic*` | `<i>italic</i>` | *italic* |
| `~~strikethrough~~` | `<s>strikethrough</s>` | ~~strikethrough~~ |
| `__underline__` | `<u>underline</u>` | __underline__ |
| `` `code` `` | `<code>code</code>` | `code` |
| `` ```python\ncode\n``` `` | `<pre><code class="language-python">code</code></pre>` | Code block with syntax highlighting |
| `[link](url)` | `<a href="url">link</a>` | [link](url) |

### **Block-Level Formatting**

#### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

Converts to HTML:
```html
<table>
  <tr><th>Header 1</th><th>Header 2</th></tr>
  <tr><td>Cell 1</td><td>Cell 2</td></tr>
  <tr><td>Cell 3</td><td>Cell 4</td></tr>
</table>
```

**Constraints:**
- Max 10 columns (recommended ≤5 for mobile)
- Max 100 rows
- HTML special characters must be escaped: `&amp;`, `&lt;`, `&gt;`

#### Code Blocks

```markdown
```python
def hello():
    print("Hello, Telegram!")
```
```

Renders with syntax highlighting for supported languages: `python`, `javascript`, `json`, `bash`, `sql`, `html`, `xml`, `c`, `cpp`, `java`, etc.

#### Blockquotes

```markdown
> This is a blockquote
> Multiple lines supported
```

Converts to:
```html
<blockquote>This is a blockquote<br>Multiple lines supported</blockquote>
```

#### Lists

**Unordered:**
```markdown
- Item 1
- Item 2
  - Nested item
```

**Ordered:**
```markdown
1. First
2. Second
   1. Nested
```

---

## 🧮 LaTeX Mathematical Formulas

### **Inline Math**

Use `$...$` for inline formulas:

```markdown
The equation is $E = mc^2$ where mass meets energy.
```

**Renders as:** The equation is $E = mc^2$ where mass meets energy.

### **Block Math**

Use `$$...$$` for display math:

```markdown
$$\int_0^1 x^2 \, dx = \frac{1}{3}$$
```

### **Common LaTeX Symbols**

| Symbol | LaTeX | Renders |
|--------|-------|---------|
| Greek alpha | `$\alpha$` | α |
| Greek beta | `$\beta$` | β |
| Integral | `$\int$` | ∫ |
| Sum | `$\sum$` | Σ |
| Product | `$\prod$` | ∏ |
| Square root | `$\sqrt{x}$` | √x |
| Fraction | `$\frac{a}{b}$` | a/b |
| Superscript | `$x^2$` | x² |
| Subscript | `$x_i$` | xᵢ |
| Plus/minus | `$\pm$` | ± |
| Times | `$\times$` | × |
| Division | `$\div$` | ÷ |
| Approx | `$\approx$` | ≈ |
| Not equal | `$\neq$` | ≠ |
| Less/greater | `$\leq$`, `$\geq$` | ≤, ≥ |
| Infinity | `$\infty$` | ∞ |
| Partial derivative | `$\partial$` | ∂ |
| Nabla | `$\nabla$` | ∇ |

### **Complex Formula Examples**

```markdown
Pythagorean theorem: $a^2 + b^2 = c^2$

Quadratic formula: $$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Summation: $$\sum_{k=1}^{n} k = \frac{n(n+1)}{2}$$

Double integral: $$\iint_R f(x,y) \, dA = \int_a^b \int_c^d f(x,y) \, dy \, dx$$
```

---

## 🎨 Rich Message HTML Tags (Bot API 10.2 Verified)

### **Supported HTML Tags**

| Tag | Purpose | Example | Status |
|-----|---------|---------|--------|
| `<h1>` — `<h6>` | Headings | `<h1>Title</h1>` | ✅ |
| `<p>` | Paragraph | `<p>Text</p>` | ✅ |
| `<b>`, `<strong>` | Bold | `<b>bold</b>` | ✅ |
| `<i>`, `<em>` | Italic | `<i>italic</i>` | ✅ |
| `<u>` | Underline | `<u>underline</u>` | ✅ |
| `<s>`, `<del>` | Strikethrough | `<s>deleted</s>` | ✅ |
| `<mark>` | Highlighting | `<mark>highlighted</mark>` | ✅ |
| `<code>` | Inline code | `<code>var x = 1</code>` | ✅ |
| `<pre>` | Preformatted | `<pre>code block</pre>` | ✅ |
| `<a>` | Link | `<a href="url">text</a>` | ✅ |
| `<br>` | Line break | `text<br>more` | ✅ |
| `<hr>` | Horizontal divider | `<hr>` | ✅ |
| `<table>`, `<tr>`, `<td>`, `<th>` | Tables | `<table><tr><td>...</td></tr></table>` | ✅ |
| `<ul>`, `<ol>`, `<li>` | Lists | `<ul><li>item</li></ul>` | ✅ |
| `<blockquote>` | Quotes | `<blockquote>quote</blockquote>` | ✅ |
| `<details>`, `<summary>` | Collapsible | `<details><summary>Title</summary>Content</details>` | ✅ |
| `<div>`, `<span>` | Containers | `<div>...</div>` | ✅ |

### **Unsupported / Restricted Tags** (Cause `RICH_MESSAGE_BLOCK_UNSUPPORTED` Error)

| Tag | Status | Alternative |
|-----|--------|-------------|
| `<tg-emoji>` | ❌ Not supported | Use Markdown emoji: `![🤩](tg://emoji?id=5190683945351535076)` |
| `<tg-thinking>` | ⚠️ **Drafts only** | Use `<tg-thinking>` ONLY in `sendRichMessageDraft` streaming frames; omit from final message |
| `<tg-spoiler>` | ❌ Not supported | Use `<details><summary>Spoiler</summary>Content</details>` |
| `<sup>` | ❌ Not supported | Use Unicode: `x²`, `xʳ`, or plain text `x^2` |
| `<sub>` | ❌ Not supported | Use Unicode: `xᵢ`, `xₙ`, or plain text `x_n` |
| `<script>`, `<style>` | ❌ Security blocked | Not applicable for Telegram |

### **CRITICAL: `<tg-thinking>` Behavior**

**`<tg-thinking>` ONLY works in `sendRichMessageDraft` (streaming):**

```html
<!-- ✅ CORRECT: In draft frames -->
<tg-thinking>Analyzing data...</tg-thinking>

<!-- ❌ WRONG: In final sendRichMessage or editMessageText -->
<!-- Will cause: RICH_MESSAGE_BLOCK_UNSUPPORTED error -->
```

**Pattern:**
1. Send progressive drafts WITH `<tg-thinking>` via `sendRichMessageDraft`
2. Final message via `editMessageText` with `rich_message` param (NO `<tg-thinking>`)

---

## 🚀 Streaming Rich Messages (Animated Progression)

### **Using `sendRichMessageDraft` for Animated Updates**

Use for showing AI thinking, calculations, or progressive results:

```python
import asyncio
import aiohttp
import time

async def stream_rich_draft(bot_token: str, chat_id: int):
    """Example: animated factorization progress."""
    
    draft_id = int(time.time() * 1000)  # Unique draft identifier
    frames = [
        "<tg-thinking>Computing gcd(a, N)...</tg-thinking>",
        "<tg-thinking>Period found: r=6</tg-thinking><br>Factors: 7, 13",
        "<h2>✓ Success</h2><b>91 = 7 × 13</b>"
    ]
    
    url_draft = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"
    url_final = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    
    async with aiohttp.ClientSession() as session:
        # Send progressive drafts (with thinking animation)
        for frame in frames[:-1]:
            await session.post(url_draft, json={
                "chat_id": chat_id,
                "draft_id": draft_id,
                "rich_message": {"html": frame}
            })
            await asyncio.sleep(0.5)  # Delay between frames
        
        # Send final message (without thinking)
        await session.post(url_final, json={
            "chat_id": chat_id,
            "rich_message": {"html": frames[-1]}
        })
```

### **Draft Constraints**

- `draft_id`: Unique identifier per conversation (use timestamp or message ID)
- **Works ONLY in DMs** (not in groups/channels)
- **Thinking animation** (`<tg-thinking>`) available only in drafts
- Frame delay: 0.5-2 seconds recommended for smooth animation
- Max 50 frames per draft session

---

## 🔧 Custom Emoji in Replies

### **Markdown Syntax (Recommended)**

```markdown
![🤩](tg://emoji?id=5190683945351535076) **Success!**
```

### **Raw HTML Syntax**

Do NOT use `<tg-emoji>` tags (unsupported). Use Markdown image syntax instead.

### **Emoji Rotation Strategy**

Avoid repeating the same emoji in consecutive replies. Rotate through related emoji:

| Context | Emoji Rotation |
|---------|---|
| Analysis needed | 🤔 → 🧐 → 🧠 → 🤔 |
| Success/completion | 🤩 → 😌 → 😊 → 👌 |
| Uncertain | 🫤 → 🤷‍♂️ → 😐 → 😬 |
| Warning | 😱 → 😫 → ⚠️ (use 😞) |

---

## 🎛️ Gateway Configuration

### **Enable Rich Messages in `config.yaml`**

```yaml
platforms:
  telegram:
    extra:
      # Rich Messages enabled
      rich_messages: true
      
      # Streaming drafts enabled
      rich_drafts: true
      
      # Always use rich formatting (even for plain text)
      always_use_rich: true
```

### **Verify Gateway is Using This Skill**

The Hermes gateway (`plugins/platforms/telegram/adapter.py`) automatically:
1. Detects this skill in the system prompt
2. Routes all responses through `_needs_rich_rendering()`
3. Converts Markdown to HTML for rich messages
4. Promotes emoji to premium custom emoji entities
5. Falls back to MarkdownV2 on failure

---

## ⚡ Performance & Limits

| Constraint | Limit | Notes |
|-----------|-------|-------|
| Rich message HTML | 32,768 chars | Longer: split into multiple messages |
| Single emoji ID length | 19 digits | `5190683945351535076` |
| Table columns | ≤10 (recommend ≤5) | Mobile rendering degrades with >5 |
| Table rows | ≤100 | Practical limit ~50 for UX |
| Code block lines | No hard limit | Use `<details>` for >20 lines |
| Draft frames | ≤50 per session | Stops automatically after final send |
| Draft frame delay | ≥0.2s | <0.2s may not animate |

---

## 🐛 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Emoji not rendering | Unicode instead of custom emoji ID | Use Markdown: `![🤩](tg://emoji?id=5190683945351535076)` |
| `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Unsupported HTML tag used | Remove: `<tg-emoji>`, `<tg-spoiler>`, `<sup>`, `<sub>` (in non-draft messages) |
| `<tg-thinking>` fails | Used in final message (not draft) | Use only in `sendRichMessageDraft`; remove before `editMessageText` |
| Table columns misaligned | Too many columns for mobile | Limit to 3-5 columns; use `<details>` for overflow |
| LaTeX not rendering | Formula syntax error | Validate with `$E = mc^2$` (correct spacing) vs `$E=mc^2$` |
| Draft not animating | Wrong `draft_id` or slow network | Use consistent `draft_id`; add 0.5-1s delay between frames |
| Rich message too long | HTML >32KB | Split into multiple `sendRichMessage` calls |

---

## 📚 Complete Example: Interactive Analysis Report

```markdown
# ![🧠](tg://emoji?id=5447595110743168717) Analysis Report

## Overview

Processing query: *factorization of N=91*

### Results Table

| Metric | Value | Unit |
|--------|-------|------|
| Input N | 91 | integer |
| Algorithm | Shor | quantum |
| Period r | 6 | cycles |
| Factors | 7, 13 | primes |

## Mathematical Details

The result satisfies:
$$7 \times 13 = 91$$

Verification: $\gcd(7, 91) = 7$ ✓

### Technical Breakdown

```python
def verify_factors(n, factors):
    return all(n % f == 0 for f in factors)

assert verify_factors(91, [7, 13])
```

## Confidence: ![💯](tg://emoji?id=5384182740411240426)

---

**Generated:** 2026-08-13T10:45:33Z
```

---

## 🔗 Bot API References

- **Bot API 10.2 Rich Messages:** https://core.telegram.org/bots/api#sendrichmessage
- **Formatting Options:** https://core.telegram.org/bots/api#formatting-options
- **InputRichMessage:** https://core.telegram.org/bots/api#inputrichmessage
- **sendRichMessageDraft:** https://core.telegram.org/bots/api#sendrichmessagedraft
- **Custom Emoji:** https://core.telegram.org/bots/api#custom-emoji
- **HTML-style formatting:** https://core.telegram.org/bots/api#html-style

---

## ✅ Checklist for Telegram Replies

Before sending any reply via gateway:

- [ ] All emoji are from the 103 verified ID registry
- [ ] No bare Unicode emoji in response text
- [ ] LaTeX formulas wrapped in `$...$` or `$$...$$`
- [ ] HTML table syntax correct (closed `<table>`, `<tr>`, `<td>` tags)
- [ ] No `<tg-emoji>`, `<tg-spoiler>`, `<sup>`, `<sub>` in final messages
- [ ] `<tg-thinking>` used ONLY in `sendRichMessageDraft` drafts, not final
- [ ] Markdown links use `[text](url)` syntax
- [ ] Code blocks have language specified: `` ```python\n...\n``` ``
- [ ] No HTML injection from user input (always escape: `html.escape()`)
- [ ] Rich message under 32KB (split if needed)
- [ ] Tables ≤10 columns (recommend ≤5)

---

## 📋 Gateway Adapter Integration

The Telegram adapter in `plugins/platforms/telegram/adapter.py` automatically:

1. **Detects** this skill in system prompt
2. **Checks** `_supports_rich` capability (Bot API 10.1+)
3. **Routes** all responses through `_rich_promote_premium_emoji()`
4. **Converts** Markdown to HTML for rich messages
5. **Sends** via `sendRichMessage` or `sendRichMessageDraft`
6. **Falls back** to MarkdownV2 if rich fails

No additional configuration needed in code — just follow this skill's guidelines.

---

## 📝 Versioning

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-08-13 | Consolidated skill; 103 emoji (99 + 4 new); complete Bot API 10.2 docs |
| 2.1.0 | 2026-08-12 | 99 emoji registry, rich message support |
| 1.0.0 | 2026-08-10 | Initial rich messages skill |

---

**For every Telegram reply via gateway: Use this skill's formatting rules EXCLUSIVELY.**
