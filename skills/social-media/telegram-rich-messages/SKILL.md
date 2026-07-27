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
- **Code blocks** with syntax highlighting (`<pre><code>`)
- **Thinking animations** (`<tg-thinking>`)
- **Collapsible details** (`<details>`, `<summary>`)
- **Blockquotes** (`<blockquote>`)
- **Draft previews** via `sendRichMessageDraft` (animated typing effect)

This skill teaches Hermes how to compose and send Rich Messages instead of falling back to MarkdownV2 or HTML.

## When to Use

- ✅ Sending structured data (tables, comparison matrices)
- ✅ Showing code with syntax highlighting
- ✅ Animated "thinking" indicators during long operations
- ✅ Progressive draft updates (streaming responses)
- ✅ Collapsible technical details (logs, stack traces)
- ❌ Simple text messages — use regular `sendMessage` with MarkdownV2
- ❌ When bot token doesn't support Bot API 10.1+ (check `_supports_rich` in adapter)

## Quick Reference

| Feature | HTML Tag | Example |
|---------|----------|---------|
| Table | `<table><tr><th>H</th></tr><tr><td>C</td></tr></table>` | Comparison matrices |
| Code block | `<pre><code class="language-python">print("hi")</code></pre>` | Syntax-highlighted code |
| Thinking | `<tg-thinking>Computing...</tg-thinking>` | Animated spinner |
| Details | `<details><summary>Title</summary>Content</details>` | Collapsible logs |
| Blockquote | `<blockquote>Quote</blockquote>` | Quotes |
| Bold/Italic | `<b>`, `<i>`, `<u>`, `<s>` | Inline formatting |
| Links | `<a href="...">text</a>` | Hyperlinks |

## Sending a Rich Message

### Via Hermes Adapter (Recommended)

The Telegram adapter in `plugins/platforms/telegram/adapter.py` automatically detects Rich Message support and uses `sendRichMessage` / `sendRichMessageDraft` when possible.

```python
# In your skill/tool code - just return rich HTML!
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
- Draft streaming via `sendRichMessageDraft`
- Size limits (4096 chars per message)

### Direct Bot API Call (Advanced)

If you need raw control, use the gateway RPC:

```python
from hermes_tools import terminal

# Via gateway JSON-RPC
await terminal(command="""
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendRichMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "rich_message": {"html": "<h1>Hello</h1><table>...</table>"},
    "parse_mode": "HTML"
  }'
""")
```

## Composing Rich HTML

### Helper Functions (Python)

```python
def rich_table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate a <table> from headers + rows."""
    thead = "".join(f"<th>{h}</th>" for h in headers)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><tr>{thead}</tr>{tbody}</table>"

def rich_code(code: str, lang: str = "python") -> str:
    """Wrap code in <pre><code class='language-{lang}'>."""
    from html import escape
    return f"<pre><code class=\"language-{lang}\">{escape(code)}</code></pre>"

def rich_thinking(text: str) -> str:
    """Thinking animation block."""
    from html import escape
    return f"<tg-thinking>{escape(text)}</tg-thinking>"

def rich_details(summary: str, content: str, open_by_default: bool = False) -> str:
    """Collapsible details block."""
    open_attr = " open" if open_by_default else ""
    from html import escape
    return f"<details{open_attr}><summary>{escape(summary)}</summary>{content}</details>"

def rich_blockquote(text: str) -> str:
    from html import escape
    return f"<blockquote>{escape(text)}</blockquote>"
```

### Complete Example: Factorization Results (like ShorBot)

```python
def format_factorization_rich(n: int, attempts: list, success: bool, factors: tuple = None) -> str:
    """Generate Rich HTML for Shor's algorithm visualization."""
    from html import escape
    
    # Table of attempts
    rows = ""
    for st in attempts:
        idx = st["attempt"]
        a = st["a"]
        if "shortcut_gcd" in st:
            gcd = st["shortcut_gcd"]
            f1, f2 = st["factors"]
            period = "shortcut"
            result = f"<b>{f1} × {f2}</b>"
        else:
            gcd = 1
            period = escape(str(st.get("period_r", "?")))
            cand = st.get("candidate_factors")
            if st.get("factors"):
                f1, f2 = st["factors"]
                result = f"<b>{f1} × {f2}</b>"
            elif cand:
                result = f"candidates: {cand[0]}, {cand[1]}"
            else:
                result = escape(st.get("result", "-"))
        rows += f"<tr><td>{idx}</td><td>{a}</td><td>{gcd}</td><td>{period}</td><td>{result}</td></tr>"
    
    table = f"<table><tr><th>No.</th><th>a</th><th>gcd(a,N)</th><th>period r</th><th>result</th></tr>{rows}</table>"
    
    if success and factors:
        f1, f2 = factors
        result_html = f"<h2>Result</h2><p><b>{n} = {f1} × {f2}</b></p>"
    else:
        result_html = f"<p>Tried {len(attempts)} attempts — failed to factorize.</p>"
    
    # Add algorithm explanation
    code_block = """<pre><code class="language-python">
x = a^(r/2) mod N
factor1 = gcd(x-1, N)
factor2 = gcd(x+1, N)
</code></pre>"""
    
    details = f"<details><summary>Why this won't break RSA tomorrow</summary><p>This is a <b>classical simulation</b> — no quantum speedup. Real Shor's algorithm needs thousands of logical qubits.</p><p>Module repo: <a href='https://github.com/i-execute/Modules'>i-execute/Modules</a></p></details>"
    
    return f"<h1>Factorization N = {n}</h1>{table}{code_block}{result_html}{details}"
```

## Streaming with `sendRichMessageDraft`

For animated "typing" effect during long operations:

```python
async def stream_rich_draft(bot_token: str, chat_id: int, frames: list[str]):
    """Send a sequence of Rich Message drafts."""
    import aiohttp
    draft_id = int(time.time() * 1000)
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"
    
    async with aiohttp.ClientSession() as session:
        for i, html in enumerate(frames):
            payload = {
                "chat_id": chat_id,
                "draft_id": draft_id,
                "rich_message": {"html": html}
            }
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    break
            await asyncio.sleep(0.3)  # frame delay
        
        # Send final message
        final_url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
        async with session.post(final_url, json={
            "chat_id": chat_id,
            "rich_message": {"html": frames[-1]}
        }) as resp:
            return await resp.json()
```

## Hermes Integration Points

### 1. Skill Response Format

When a skill returns a result, include `rich_html` key:

```python
# In your skill's handler
return {
    "text": "Fallback plain text for non-rich clients",
    "rich_html": "<h1>Rich Version</h1><table>...</table>",
    "parse_mode": "HTML"
}
```

The Telegram adapter will pick up `rich_html` automatically.

### 2. Gateway Event Subscription

Listen for Rich Message capability changes:

```python
# In a plugin or background task
host.onEvent("telegram.rich_capability_changed", lambda data: log(f"Rich: {data}"))
```

### 3. Desktop Plugin for Preview

Use `hermes-desktop-plugins` skill to build a Rich Message composer pane in the desktop app.

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Rich Message not rendering | Bot API version < 10.1 or client outdated | Check `_supports_rich` in adapter; fallback to MarkdownV2 |
| "Rich message too long" | HTML > 4096 chars | Split into multiple messages or truncate |
| Draft not animating | Missing `draft_id` or wrong chat | Use consistent `draft_id` per conversation |
| Code highlighting not working | Missing `class="language-xxx"` | Always specify language class |
| Tables collapse on mobile | Too many columns | Limit to 4-5 columns; use `<details>` for extra data |

## Verification Checklist

- [ ] Bot token has Bot API 10.1+ support (most tokens do)
- [ ] Test `sendRichMessage` with a simple `<h1>Test</h1>`
- [ ] Verify fallback works when rich fails (check adapter logs)
- [ ] Test draft streaming with 3+ frames
- [ ] Validate HTML with Telegram's [Rich Message tester](https://core.telegram.org/bots/api#sendrichmessage)
- [ ] Ensure all user content is HTML-escaped (`html.escape()`)

## References

- [Bot API 10.1: sendRichMessage](https://core.telegram.org/bots/api#sendrichmessage)
- [Bot API 10.1: sendRichMessageDraft](https://core.telegram.org/bots/api#sendrichmessagedraft)
- [InputRichMessage object](https://core.telegram.org/bots/api#inputrichmessage)
- [Allowed HTML tags](https://core.telegram.org/bots/api#html-style)
- Hermes adapter: `plugins/platforms/telegram/adapter.py` (lines 1450-1960)
- ShorBot example: `~/.hermes/cache/documents/doc_5131e2ef5ef7_ShorBot.py`