---
name: telegram-rich-messages
description: "Use Telegram Bot API 10.1 Rich Messages (sendRichMessage, sendRichMessageDraft) with Hermes Agent for beautiful formatted responses with tables, code blocks, thinking animations, and draft previews."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, rich-messages, bot-api, sendRichMessage, sendRichMessageDraft, formatting]
    related_skills: [xurl, github-issues, hermes-desktop-plugins]
---

# Telegram Rich Messages Skill

## Overview

Telegram Bot API 10.1 introduced **Rich Messages** — a new message format that renders natively in Telegram clients with:
- **Tables** (`<table>`, `<tr>`, `<td>`, `<th>`)
- **Syntax-highlighted code blocks** (`<pre><code class="language-python">`)
- **Thinking animations** (`<tg-thinking>`)
- **Collapsible details** (`<details>`, `<summary>`)
- **Blockquotes** (`<blockquote>`)
- **Draft previews** via `sendRichMessageDraft` (animated typing effect)

This skill teaches Hermes how to compose Rich HTML and integrate with the Telegram adapter's auto-detection (`_supports_rich`).

## When to Use

- ✅ Sending structured data (comparison tables, metrics, results)
- ✅ Showing code with syntax highlighting
- ✅ Animated "thinking" indicators during long operations
- ✅ Progressive streaming updates (draft → final)
- ✅ Collapsible technical details (logs, stack traces, raw JSON)
- ❌ Simple text messages — use regular `sendMessage` with MarkdownV2
- ❌ When bot token doesn't support Bot API 10.1+ (check `_supports_rich` in adapter)

## Quick Reference: Allowed Rich HTML Tags

| Feature | HTML Tag | Example | Status |
|---------|----------|---------|--------|
| Table | `<table><tr><th>H</th></tr><tr><td>C</td></tr></table>` | Comparison matrices | ✅ Works |
| Code block | `<pre><code class="language-python">print("hi")</code></pre>` | Syntax-highlighted code | ✅ Works |
| Details | `<details><summary>Title</summary>Content</details>` | Collapsible logs | ✅ Works |
| Blockquote | `<blockquote>Quote</blockquote>` | Quotes | ✅ Works |
| Bold/Italic | `<b>`, `<i>`, `<u>`, `<s>` | Inline formatting | ✅ Works |
| Links | `<a href="...">text</a>` | Hyperlinks | ✅ Works |
| Streaming draft | `sendRichMessageDraft` + `editMessageText` | Animated typing effect | ✅ Works |
| Thinking (draft only) | `<tg-thinking>Computing...</tg-thinking>` | Animated spinner | ⚠️ **Works ONLY in `sendRichMessageDraft` (streaming)** — fails in `sendRichMessage`/`editMessageText` with `RICH_MESSAGE_BLOCK_UNSUPPORTED` |
| Spoiler | `<tg-spoiler>text</tg-spoiler>` | Hidden text | ❌ **Not supported** |
| Custom emoji | `<tg-emoji emoji-id="...">😀</tg-emoji>` | Telegram emoji platform | ❌ **Not supported** |
| Superscript | `<sup>text</sup>` | Math exponents | ❌ **Not supported** (use unicode: `xʳ/²` or plain text `x^(r/2)`) |
| Subscript | `<sub>text</sub>` | Math indices | ❌ **Not supported** (use unicode: `xᵣ` or plain text `x_r`) |

**Note:** Bot API 10.1 rich messages only support a subset of HTML tags. The adapter (`plugins/platforms/telegram/adapter.py`) auto-detects rich-eligible content (tables, `<details>`, code blocks, math) and routes via `sendRichMessage`/`sendRichMessageDraft`. Unsupported tags cause `RICH_MESSAGE_BLOCK_UNSUPPORTED` error.

**KEY FINDING FROM TESTING: `<tg-thinking>` works ONLY in drafts (streaming)**

**Telegram Bot API 10.1 limitation:** `<tg-thinking>` renders **only** in `sendRichMessageDraft` (streaming frames). In `sendRichMessage` or `editMessageText` it causes `RICH_MESSAGE_BLOCK_UNSUPPORTED` error.

**Correct pattern:**
1. **Streaming frames** → `sendRichMessageDraft` WITH `<tg-thinking>` ✅
2. **Final message** → `sendRichMessage` / `editMessageText` WITHOUT `<tg-thinking>` ✅

The Hermes Telegram adapter (`plugins/platforms/telegram/adapter.py`) already handles this correctly:
- `_try_send_rich_draft()` → sends drafts WITH thinking
- `_try_edit_rich()` → finalizes WITHOUT thinking

**KEY FINDING FROM TESTING:** The adapter's `_needs_rich_rendering()` method was modified to **ALWAYS return True** for any non-empty content. This ensures ALL responses use Rich Messages, not just those with tables/details/math.

```python
# In plugins/platforms/telegram/adapter.py
def _needs_rich_rendering(self, content: str) -> bool:
    """Return True to ALWAYS use Rich Messages for all responses.

    Previously this only triggered for special markdown constructs (tables,
    task lists, details, math). Now we ALWAYS use Rich Messages for better
    rendering across all responses.
    """
    return bool(content and content.strip())
```

This change was pushed to the fork: https://github.com/i-execute/hermes-agent/commit/991c4f7

### **CRITICAL FINDING FROM TESTING: `<tg-thinking>` works ONLY in `sendRichMessageDraft`**

**CONFIRMED FROM TESTING:** The `<tg-thinking>` tag renders **only** in `sendRichMessageDraft` (streaming frames). In `sendRichMessage` or `editMessageText` it causes `RICH_MESSAGE_BLOCK_UNSUPPORTED` error with message "Bad Request: RICH_MESSAGE_BLOCK_UNSUPPORTED".

**Testing Results:**
- ✅ `<tg-thinking>` in `sendRichMessageDraft` (streaming frames) → **WORKS** (animated spinner)
- ❌ `<tg-thinking>` in `sendRichMessage` → **FAILS** with `RICH_MESSAGE_BLOCK_UNSUPPORTED`
- ❌ `<tg-thinking>` in `editMessageText` → **FAILS** with `RICH_MESSAGE_BLOCK_UNSUPPORTED`

**Correct pattern for streaming with thinking animation:**
1. **Streaming frames** → `sendRichMessageDraft` WITH `<tg-thinking>` ✅
2. **Final message** → `editMessageText` with `rich_message` (NO `<tg-thinking>`) ✅

The Hermes Telegram adapter (`plugins/platforms/telegram/adapter.py`) already handles this correctly:
- `_try_send_rich_draft()` → sends drafts WITH thinking
- `_try_edit_rich()` → finalizes WITHOUT thinking

### **UNSUPPORTED HTML TAGS IN BOT API 10.1 RICH MESSAGES (CONFIRMED)**

These tags cause `RICH_MESSAGE_BLOCK_UNSUPPORTED` error and MUST BE AVOIDED:

| Tag | Status | Alternative |
|-----|--------|-------------|
| `<tg-thinking>` | ❌ **Fails in `sendRichMessage`/`editMessageText`** | Works ONLY in `sendRichMessageDraft` (streaming). Use `<b>Thinking...</b>` or plain text for final messages |
| `<tg-spoiler>` | ❌ Not supported | Use `<details><summary>Spoiler</summary>Content</details>` |
| `<tg-emoji>` | ❌ Not supported | Use standard Unicode emoji: 😀 🎉 🚀 |
| `<sup>` | ❌ Not supported | Use Unicode superscripts: `x²`, `xʳ/²`, or plain text `x^(r/2)` |
| `<sub>` | ❌ Not supported | Use Unicode subscripts: `xᵣ`, `xᵢ`, or plain text `x_r` |

**CRITICAL FINDING FROM TESTING:** `<tg-thinking>` works **ONLY** in `sendRichMessageDraft` (streaming frames). In `sendRichMessage` or `editMessageText` it causes `RICH_MESSAGE_BLOCK_UNSUPPORTED` error.

**Confirmed working tags:** `<table>`, `<pre><code>`, `<details>`, `<summary>`, `<blockquote>`, `<b>`, `<i>`, `<u>`, `<s>`, `<a>`, `<pre>`, `<code>`, `<details>`, `<summary>`, `<blockquote>`, `<hr>`, `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>`, `<li>`, `<br>`, `<div>`, `<span>`, `<code>`, `<pre>`, `<a>`, `<b>`, `<i>`, `<u>`, `<s>`, `<ins>`, `<del>`, `<strong>`, `<em>`, `<mark>`, `<small>`, `<details>`, `<summary>`, `<blockquote>`, `<hr>`, `<tg-thinking>` (draft only).

### **FORMULA RENDERING IN RICH MESSAGES**

LaTeX formulas render correctly when wrapped in `<code>` tags:
- Inline: `<code>E = mc²</code>` or `<code>x = (-b ± √(b²-4ac))/2a</code>`
- Block: `<pre><code class="language-latex">E = mc^2</code></pre>`
- Unicode math symbols work directly: `∫`, `∑`, `√`, `π`, `α`, `β`, `γ`, `±`, `×`, `÷`, `∞`, `∂`, `∇`, `∈`, `∉`, `⊂`, `⊃`, `∀`, `∃`, `⇒`, `⇔`, `≤`, `≥`, `≠`, `≈`, `∝`

### **FORK WORKFLOW & GATEWAY DEPLOYMENT (This Session)**

**Repository:** https://github.com/i-execute/hermes-agent (fork of NousResearch/hermes-agent)
**Branch:** `beta` (all Rich Messages changes)
**Key commit:** `991c4f7` - "feat(telegram): always use Rich Messages for all responses"

**Deployment:**
- Gateway runs via systemd: `hermes-gateway.service`
- Working directory: `/home/forget/.hermes/hermes-agent-fork` (fork copy)
- Config: `~/.hermes/config.yaml` with `platforms.telegram.extra.rich_messages: true` and `rich_drafts: true`

**GitHub authentication:**
- Never commit a PAT, even a redacted-looking token, into skills, logs, examples, or documentation.
- Use an authenticated credential helper / `gh auth login`, or inject a secret only at runtime via the environment or repository secret store.
- Token scope and value are intentionally not recorded here.

**Fork sync workflow used (no `gh` CLI):**
```bash
# Add fork remote
git remote add fork https://github.com/i-execute/hermes-agent.git
git fetch fork

# Reset to fork/beta
git reset --hard fork/beta

# Push changes
git push fork beta

# Delete all other branches from fork (bulk via API)
git branch -r | grep fork/ | grep -vE "main|beta" | sed 's|fork/||' | xargs -I {} git push fork --delete {}
```

**Gateway restart (must run from outside gateway):**
```bash
systemctl --user restart hermes-gateway
# Verify: systemctl --user status hermes-gateway
```

### **BRANCH CLEANUP**

Use GitHub CLI or a credential helper; never place a real token in a command,
document, shell history, or commit. Keep the branches that must remain and
remove others only after confirming the target repository and branch list.

```bash
# Example: list branches first, then delete only explicitly approved names.
git ls-remote --heads origin
```

## ⚠️ CRITICAL: Unsupported HTML tags in Bot API 10.1 Rich Messages

**These tags cause `RICH_MESSAGE_BLOCK_UNSUPPORTED` error and MUST BE AVOIDED:**

| Tag | Status | Alternative |
|-----|--------|-------------|
| `<tg-thinking>` | ❌ **Fails in `sendRichMessage`/`editMessageText`** | Works ONLY in `sendRichMessageDraft` (streaming). Use `<b>Thinking...</b>` or plain text for final messages |
| `<tg-spoiler>` | ❌ Not supported | Use `<details><summary>Spoiler</summary>Content</details>` |
| `<tg-emoji>` | ❌ Not supported | Use standard Unicode emoji: 😀 🎉 🚀 |
| `<sup>` | ❌ Not supported | Use Unicode superscripts: `x²`, `xʳ/²`, or plain text `x^(r/2)` |
| `<sub>` | ❌ Not supported | Use Unicode subscripts: `xᵣ`, `xᵢ`, or plain text `x_r` |

**CRITICAL FINDING FROM TESTING:** `<tg-thinking>` works **ONLY** in `sendRichMessageDraft` (streaming frames). In `sendRichMessage` or `editMessageText` it causes `RICH_MESSAGE_BLOCK_UNSUPPORTED` error.

**Confirmed working tags:** `<table>`, `<pre><code>`, `<details>`, `<summary>`, `<blockquote>`, `<b>`, `<i>`, `<u>`, `<s>`, `<a>`, `<pre>`, `<code>`, `<details>`, `<summary>`, `<blockquote>`, `<hr>`, `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>`, `<li>`, `<br>`, `<div>`, `<span>`, `<code>`, `<pre>`, `<a>`, `<b>`, `<i>`, `<u>`, `<s>`, `<ins>`, `<del>`, `<strong>`, `<em>`, `<mark>`, `<small>`, `<details>`, `<summary>`, `<blockquote>`, `<hr>`, `<tg-thinking>` (draft only).

**IMPORTANT:** Bot API 10.1 rich messages only support a subset of HTML tags. The adapter (`plugins/platforms/telegram/adapter.py`) auto-detects rich-eligible content (tables, `<details>`, code blocks, math) and routes via `sendRichMessage`/`sendRichMessageDraft`. Unsupported tags cause `RICH_MESSAGE_BLOCK_UNSUPPORTED` error.

## Streaming with `sendRichMessageDraft`

## Sending a Rich Message

### Via Hermes Adapter (Recommended)

The Telegram adapter in `plugins/platforms/telegram/adapter.py` automatically detects Rich Message support and uses `sendRichMessage` / `sendRichMessageDraft` when available.

```python
# In your skill/tool — just return rich_html key:
async def my_tool(...):
    html = """
    <h1>Analysis Complete</h1>
    <tg-thinking>Finalizing results...</tg-thinking>
    <table>
      <tr><th>Metric</th><th>Value</th></tr>
      <tr><td>Latency</td><td>42ms</td></tr>
    </table>
    <details><summary>Raw JSON</summary>
    <pre><code class="language-json">{"key": "value"}</code></pre>
    </details>
    """
    return {"rich_html": html}
```

The adapter handles:
- Capability detection (`_supports_rich` property)
- Automatic fallback to MarkdownV2 on failure
- Size limits (4096 chars per message)
- Draft streaming via `sendRichMessageDraft`

### Direct Bot API Call (Advanced)

```bash
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendRichMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "rich_message": {"html": "<h1>Hello</h1><table>...</table>"},
    "parse_mode": "HTML"
  }'
```

## Streaming with `sendRichMessageDraft`

For animated typing effect (like ShorBot factorization):

```python
import aiohttp
import asyncio

async def stream_rich_draft(bot_token: str, chat_id: int, frames: list[str], frame_delay: float = 0.3):
    draft_id = int(time.time() * 1000)
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"

    async with aiohttp.ClientSession() as session:
        for html in frames:
            await session.post(url, json={
                "chat_id": chat_id,
                "draft_id": draft_id,
                "rich_message": {"html": html}
            })
            await asyncio.sleep(frame_delay)

        # Send final message
        await session.post(
            f"https://api.telegram.org/bot{bot_token}/sendRichMessage",
            json={"chat_id": chat_id, "rich_message": {"html": frames[-1]}}
        )
```

## Python Helpers (`references/rich_helpers.py`)

```python
from skills.social_media.telegram_rich_messages.references.rich_helpers import (
    rich_table, rich_code, rich_thinking, rich_details,
    format_factorization_rich, validate_rich_html
)

# Table
table = rich_table(
    ["Metric", "Value", "Unit"],
    [["Latency", 42, "ms"], ["Throughput", 1200, "req/s"]]
)

# Code block
code = rich_code('print("hello")\nfor i in range(10):\n    print(i)', "python")

# Thinking animation
thinking = rich_thinking("Computing gcd(a, N)...")

# Collapsible details
details = rich_details("Raw JSON", rich_code('{"key": "value"}', "json"))

# ShorBot-style factorization visualizer
html = format_factorization_rich(
    n=91,
    attempts=[{"attempt": 1, "a": 2, "period_r": 6, "factors": (7, 13)}],
    success=True,
    factors=(7, 13)
)

# Validate before sending
valid, errors = validate_rich_html(html)
```

## Complete Example: Factorization Visualizer

Matches ShorBot module style (`i-execute/Modules/ShorBot.py`):

```python
attempts = [
    {"attempt": 1, "a": 2, "period_r": 6, "candidate_factors": (3, 5)},
    {"attempt": 2, "a": 3, "period_r": 4, "factors": (7, 13)},
]

html = format_factorization_rich(
    n=91,
    attempts=attempts,
    success=True,
    factors=(7, 13)
)
# Returns complete Rich HTML with table, code block, collapsible RSA disclaimer
```

## Telegram delivery discipline

### One final reply only

When replying in the same Telegram conversation, let the gateway deliver the agent's final response. **Do not additionally invoke `hermes send`** to send a formatted copy: that creates a duplicate message (one direct send plus the gateway's normal final delivery).

Use `hermes send` only for a genuinely separate, explicitly requested outbound notification or when the agent loop will not produce a final chat reply. For normal replies, return the desired Markdown/Rich-Message content directly as the final response.

If a user asks for a normal message rather than a JSON-looking payload, do not put the intended reply inside a JSON object such as `{"message":"..."}`. Return the message body itself; the Telegram adapter handles rendering.

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Rich Message not rendering | Bot API version < 10.1 or client outdated | Check `_supports_rich` in adapter; fallback to MarkdownV2 |
| "Rich message too long" | HTML > 4096 chars | Split into multiple messages or truncate |
| Draft not animating | Wrong `draft_id` or chat_id mismatch | Use consistent `draft_id` per conversation |
| Code highlighting missing | Missing `class="language-xxx"` | Always specify language: `class="language-python"` |
| Tables collapse on mobile | Too many columns | Limit to 4-5 columns; use `<details>` for extra data |
| HTML injection | Unescaped user content | Always use `html.escape()` on dynamic values |
| `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Using unsupported tags: `<tg-thinking>`, `<tg-spoiler>`, `<tg-emoji>`, `<sup>` | Use `<b>Thinking...</b>` instead of `<tg-thinking>`, avoid `<sup>` (use unicode superscripts or plain text) |
| `<tg-thinking>` not animating | Used in final `sendRichMessage` instead of draft | `<tg-thinking>` ONLY works in `sendRichMessageDraft` streaming; final `editMessageText` must not contain it |
| Thinking block persists in final | Forgot to remove `<tg-thinking>` before final send | Final message via `editMessageText` must NOT contain `<tg-thinking>` |
| **DM topic messages share context** | `thread_sessions_per_user: false` (default) | Set `platforms.telegram.extra.thread_sessions_per_user: true` in config.yaml |
| **Rich Messages not routing to correct topic** | Missing `message_thread_id` in payload | Ensure `thread_id` extracted from `message_thread_id` and passed in `_thread_kwargs_for_send()` |

## Common Pitfalls

| Pitfall | Cause | Fix |
|---------|-------|-----|
| `RICH_MESSAGE_BLOCK_UNSUPPORTED` | Using unsupported tags: `<tg-thinking>` (in final message), `<tg-spoiler>`, `<tg-emoji>`, `<sup>`, `<sub>` | Use only supported tags: table, code, details, blockquote, b/i/u/s, a, pre/code. **`<tg-thinking>` works ONLY in `sendRichMessageDraft` (streaming)** — use `<b>Thinking...</b>` or plain text for final messages |
| `<sup>` / `<sub>` not rendering | Bot API doesn't support superscript/subscript tags | Use Unicode superscripts (¹²³) or plain text `x^(r/2)` |
| `<tg-thinking>` fails | Not supported in Bot API 10.1 rich messages for final messages | Use `<tg-thinking>` **only in `sendRichMessageDraft` frames**; for final message use bold text `<b>Computing...</b>` or plain text |
| Draft streaming not animating | Missing `draft_id` consistency or wrong chat type | Use same `draft_id` per conversation; works in DMs only |
| Rich final message not replacing draft | Final `sendRichMessage` doesn't auto-replace draft | Adapter uses `editMessageText` with `rich_message` param |
| HTML too long (>32KB) | Content exceeds `RICH_MESSAGE_MAX_CHARS` (32,768) | Split into multiple messages or truncate |
| CJK text garbled | Telegram Desktop bug with CJK in rich drafts | Adapter detects and falls back to MarkdownV2 for CJK |

## Verification Checklist

- [ ] Bot token has Bot API 10.1+ support (most tokens do)
- [ ] Test `sendRichMessage` with a simple `<h1>Test</h1>`
- [ ] Verify fallback works when rich fails (check adapter logs)
- [ ] Test draft streaming with 3+ frames
- [ ] Validate HTML with Telegram's [Rich Message tester](https://core.telegram.org/bots/api#sendrichmessage)
- [ ] Ensure all user content is HTML-escaped (`html.escape()`)
- [ ] Test with tables, code blocks, `<details>`, and formulas
- [ ] Verify streaming draft works in DM (not groups)
- [ ] Test on Telegram Desktop, Android, iOS

## References

- [Bot API 10.1: sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage)
- [Bot API 10.1: sendRichMessageDraft](https://core.telegram.org/bots/api#sendrichmessagedraft)
- [InputRichMessage object](https://core.telegram.org/bots/api#inputrichmessage)
- [Allowed HTML tags](https://core.telegram.org/bots/api#html-style)
- Hermes adapter: `plugins/platforms/telegram/adapter.py` (lines 1450-1960)
- ShorBot example: `i-execute/Modules/ShorBot.py`

## Supporting Files in This Skill

| File | Purpose |
|------|---------|
| `references/rich_helpers.py` | Python composers: `rich_table`, `rich_code`, `rich_thinking`, `rich_details`, `format_factorization_rich`, `validate_rich_html` |
| `references/fork-workflow.md` | Complete fork→PR workflow using `git` + `curl` (no `gh` CLI) |
| `references/fork-sync-and-branch-cleanup.md` | Fork sync workflow: upstream sync, beta branch workflow, bulk remote branch deletion, local cleanup |
| `references/fork-workflow-and-branch-cleanup.md` | Combined fork workflow reference |
| `references/dm-topic-handling.md` | Telegram DM topic/thread isolation, session keys, Rich Message routing in topics |
| `references/obhod-bot-patterns.md` | OBHOD bot dev patterns: VK OAuth, inline queries, echo-id mode, dedup, HTML formatting, WireGuard scripts |
| `references/obhod-android-freeturn-uri.md` | Authoritative freeturn:// URI spec (Android `FreeturnLink.kt` parser + `docs/uri.md`): all fields, `wg` embedding, `cid` allowlist, `peer` requirements |
| `scripts/rich_stream_demo.py` | Runnable ShorBot-style streaming demo using `sendRichMessageDraft` |