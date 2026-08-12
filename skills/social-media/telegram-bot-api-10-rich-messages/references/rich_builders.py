"""
Telegram Bot API 10.1/10.2 Rich Message Builders
=================================================

Complete Python helpers for building Rich Messages programmatically.
Compatible with Bot API 10.1 (June 11, 2026) and 10.2 (July 14, 2026).

Installation:
    pip install aiohttp  # for async API calls

Usage:
    from skills.social_media.telegram_bot_api_10_rich_messages.references.rich_builders import (
        plain, bold, italic, code, url, math_inline,
        paragraph, heading, divider, preformatted, math_block,
        table, details, thinking, build_message,
        send_rich_message, stream_rich_draft
    )

    msg = build_message(
        heading(1, bold(plain("Report"))),
        divider(),
        paragraph(plain("Revenue: "), bold(plain("$4.2M"))),
        table([["Q2", "$3.4M"], ["Q3", "$4.2M"]], headers=["Period", "Revenue"]),
        details("Methodology", paragraph(plain("Internal data..."))),
        math_block("\\sum R_i = R_{total}")
    )
"""

from typing import List, Any, Optional, Union, Dict, Callable
import json


# ============================================================
# RichText Builders (Inline Formatting)
# ============================================================

def plain(text: str) -> Dict:
    """Plain text node."""
    return {"type": "plain", "text": text}


def bold(*content: Dict) -> Dict:
    """Bold text - can nest other rich text."""
    return {"type": "bold", "text": list(content)}


def italic(*content: Dict) -> Dict:
    """Italic text - can nest other rich text."""
    return {"type": "italic", "text": list(content)}


def underline(*content: Dict) -> Dict:
    """Underlined text - can nest other rich text."""
    return {"type": "underline", "text": list(content)}


def strikethrough(*content: Dict) -> Dict:
    """Strikethrough text - can nest other rich text."""
    return {"type": "strikethrough", "text": list(content)}


def spoiler(*content: Dict) -> Dict:
    """Spoiler text (tap to reveal) - can nest other rich text."""
    return {"type": "spoiler", "text": list(content)}


def marked(*content: Dict) -> Dict:
    """Highlighted/marked text - can nest other rich text."""
    return {"type": "marked", "text": list(content)}


def subscript(*content: Dict) -> Dict:
    """Subscript text - can nest other rich text."""
    return {"type": "subscript", "text": list(content)}


def superscript(*content: Dict) -> Dict:
    """Superscript text - can nest other rich text."""
    return {"type": "superscript", "text": list(content)}


def code(text: str) -> Dict:
    """Inline monospace code - CANNOT nest other entities."""
    return {"type": "code", "text": text}


def url(text: str, url: str) -> Dict:
    """Hyperlink - CANNOT nest other entities."""
    return {"type": "url", "text": [plain(text)], "url": url}


def email(text: str, email: str) -> Dict:
    """Email link - CANNOT nest other entities."""
    return {"type": "email", "text": [plain(text)], "email": email}


def phone(text: str, phone_number: str) -> Dict:
    """Phone link - CANNOT nest other entities."""
    return {"type": "phone", "text": [plain(text)], "phone_number": phone_number}


def bank_card(text: str, number: str) -> Dict:
    """Bank card link - CANNOT nest other entities."""
    return {"type": "bank_card", "text": [plain(text)], "number": number}


def mention(text: str, user_id: int) -> Dict:
    """User mention - CANNOT nest other entities."""
    return {"type": "mention", "text": [plain(text)], "user": {"id": user_id}}


def hashtag(text: str, hashtag: str) -> Dict:
    """Hashtag link - CANNOT nest other entities."""
    return {"type": "hashtag", "text": [plain(text)], "hashtag": hashtag}


def cashtag(text: str, cashtag: str) -> Dict:
    """Cashtag ($SYMBOL) - CANNOT nest other entities."""
    return {"type": "cashtag", "text": [plain(text)], "cashtag": cashtag}


def bot_command(text: str, command: str) -> Dict:
    """Bot command - CANNOT nest other entities."""
    return {"type": "bot_command", "text": [plain(text)], "command": command}


def custom_emoji(text: str, custom_emoji_id: str) -> Dict:
    """Custom emoji - CANNOT nest other entities."""
    return {"type": "custom_emoji", "text": text, "custom_emoji_id": custom_emoji_id}


def math_inline(latex: str) -> Dict:
    """Inline LaTeX math - CANNOT nest other entities."""
    return {"type": "math", "text": latex}


def anchor_link(text: str, anchor_name: str) -> Dict:
    """Link to document anchor - CANNOT nest other entities."""
    return {"type": "anchor_link", "text": [plain(text)], "anchor_name": anchor_name}


def reference_link(text: str, reference_id: str) -> Dict:
    """Footnote link - CANNOT nest other entities."""
    return {"type": "reference_link", "text": [plain(text)], "reference_id": reference_id}


def date_time(text: str, timestamp: int) -> Dict:
    """Formatted timestamp - leaf node."""
    return {"type": "date_time", "text": [plain(text)], "timestamp": timestamp}


def anchor(name: str) -> Dict:
    """Document anchor (RichText level)."""
    return {"type": "anchor", "name": name}


# ============================================================
# RichBlock Builders (Structural Blocks)
# ============================================================

def paragraph(*content: Dict) -> Dict:
    """Text paragraph."""
    return {"type": "paragraph", "content": list(content)}


def heading(level: int, *content: Dict) -> Dict:
    """Section heading H1-H6."""
    level = max(1, min(6, level))
    return {"type": "section_heading", "level": level, "content": list(content)}


def divider() -> Dict:
    """Horizontal divider."""
    return {"type": "divider"}


def preformatted(text: str, language: str = "") -> Dict:
    """Code block with syntax highlighting."""
    return {"type": "preformatted", "content": [plain(text)], "language": language}


def math_block(latex: str) -> Dict:
    """Block LaTeX math expression."""
    return {"type": "math", "content": latex}


def block_anchor(name: str) -> Dict:
    """Document anchor (block level)."""
    return {"type": "anchor", "name": name}


def footer(*content: Dict) -> Dict:
    """Footer text."""
    return {"type": "footer", "content": list(content)}


def block_quote(*content: Dict, citation: List[Dict] = None) -> Dict:
    """Block quotation."""
    result = {"type": "block_quote", "content": list(content)}
    if citation:
        result["citation"] = citation
    return result


def pull_quote(*content: Dict, citation: List[Dict] = None) -> Dict:
    """Pull quote (highlighted)."""
    result = {"type": "pull_quote", "content": list(content)}
    if citation:
        result["citation"] = citation
    return result


def list_item(prefix: List[Dict], *content: Dict) -> Dict:
    """List item with nested blocks."""
    return {"type": "list_item", "prefix": prefix, "content": list(content)}


def list_block(*items: Dict, ordered: bool = False, numeral: str = "1") -> Dict:
    """Bullet/numbered/task list."""
    return {
        "type": "list",
        "items": list(items),
        "ordered": ordered,
        "numeral": numeral  # "1", "a", "A", "i", "I"
    }


def table_cell(content: Union[str, List[Dict]], header: bool = False, align: str = "left",
               colspan: int = 1, rowspan: int = 1) -> Dict:
    """Table cell."""
    if isinstance(content, str):
        content = [plain(content)]
    return {
        "type": "table_cell",
        "content": content,
        "header": header,
        "align": align,  # "left", "center", "right"
        "colspan": colspan,
        "rowspan": rowspan
    }


def table_row(*cells: Dict) -> Dict:
    """Table row."""
    return {"type": "table_row", "cells": list(cells)}


def table(rows: List[List[Any]], headers: List[str] = None, caption: str = "",
          bordered: bool = True, striped: bool = True) -> Dict:
    """Table with rows and optional headers."""
    table_rows = []

    if headers:
        table_rows.append(table_row(
            *[table_cell(h, header=True, align="center") for h in headers]
        ))

    for row in rows:
        table_rows.append(table_row(
            *[table_cell(c, align="left" if isinstance(c, str) else "center") for c in row]
        ))

    result = {
        "type": "table",
        "rows": table_rows,
        "bordered": bordered,
        "striped": striped
    }
    if caption:
        result["caption"] = {"type": "caption", "content": [plain(caption)]}
    return result


def details(summary: str, *blocks: Dict, open: bool = False) -> Dict:
    """Collapsible details block."""
    return {
        "type": "details",
        "summary": [plain(summary)],
        "content": list(blocks),
        "open": open
    }


def collage(*items: Dict) -> Dict:
    """Media collage/grid."""
    return {"type": "collage", "items": list(items)}


def collage_item(media: Dict, width: int, height: int) -> Dict:
    """Collage item."""
    return {"type": "collage_item", "media": media, "width": width, "height": height}


def slideshow(*items: Dict) -> Dict:
    """Media slideshow/carousel."""
    return {"type": "slideshow", "items": list(items)}


def slideshow_item(media: Dict, caption: Dict = None) -> Dict:
    """Slideshow item."""
    result = {"type": "slideshow_item", "media": media}
    if caption:
        result["caption"] = caption
    return result


def map_block(latitude: float, longitude: float, zoom: int = 10) -> Dict:
    """Map with pin."""
    return {
        "type": "map",
        "location": {"latitude": latitude, "longitude": longitude},
        "zoom": zoom
    }


def photo(media: Dict, caption: Dict = None, credit: Dict = None) -> Dict:
    """Photo block."""
    result = {"type": "photo", "media": media}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def video(media: Dict, caption: Dict = None, credit: Dict = None) -> Dict:
    """Video block."""
    result = {"type": "video", "media": media}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def animation(media: Dict, caption: Dict = None, credit: Dict = None) -> Dict:
    """Animation/GIF block."""
    result = {"type": "animation", "media": media}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def audio(media: Dict, caption: Dict = None, credit: Dict = None) -> Dict:
    """Audio block."""
    result = {"type": "audio", "media": media}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def voice_note(media: Dict, caption: Dict = None) -> Dict:
    """Voice note block (Bot API 10.2+)."""
    result = {"type": "voice_note", "media": media}
    if caption:
        result["caption"] = caption
    return result


def thinking(text: str = "Thinking...") -> Dict:
    """AI thinking animation - ONLY WORKS IN sendRichMessageDraft!"""
    return {"type": "thinking", "text": text}


def caption(*content: Dict) -> Dict:
    """Caption for media blocks."""
    return {"type": "caption", "content": list(content)}


def credit(*content: Dict) -> Dict:
    """Credit/attribution for media blocks."""
    return {"type": "credit", "content": list(content)}


def input_media_photo(file_id: str, caption: Dict = None, credit: Dict = None) -> Dict:
    """Input media for photo (for InputRichMessageMedia in 10.2+)."""
    result = {"type": "photo", "media": file_id}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def input_media_video(file_id: str, caption: Dict = None, credit: Dict = None) -> Dict:
    """Input media for video."""
    result = {"type": "video", "media": file_id}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def input_media_animation(file_id: str, caption: Dict = None, credit: Dict = None) -> Dict:
    """Input media for animation."""
    result = {"type": "animation", "media": file_id}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def input_media_audio(file_id: str, caption: Dict = None, credit: Dict = None) -> Dict:
    """Input media for audio."""
    result = {"type": "audio", "media": file_id}
    if caption:
        result["caption"] = caption
    if credit:
        result["credit"] = credit
    return result


def input_media_voice_note(file_id: str, caption: Dict = None) -> Dict:
    """Input media for voice note (10.2+)."""
    result = {"type": "voice_note", "media": file_id}
    if caption:
        result["caption"] = caption
    return result


# ============================================================
# Message Builders
# ============================================================

def build_message(*blocks: Dict, media: Dict = None) -> Dict:
    """Build complete InputRichMessage."""
    msg = {"blocks": list(blocks)}
    if media:
        msg["media"] = media
    return msg


def validate_rich_message(message: Dict) -> tuple[bool, List[str]]:
    """Basic validation of rich message structure."""
    errors = []

    if "blocks" not in message:
        errors.append("Missing 'blocks' field")
        return False, errors

    blocks = message.get("blocks", [])
    if not isinstance(blocks, list):
        errors.append("'blocks' must be a list")
        return False, errors

    # Check for thinking block in non-draft context
    for block in blocks:
        if block.get("type") == "thinking":
            errors.append("WARNING: 'thinking' block should only be used in sendRichMessageDraft (streaming)")

    # Check size estimate
    size = len(json.dumps(message))
    if size > 32768:
        errors.append(f"Message may exceed 32KB limit (current: {size} bytes)")

    return len(errors) == 0, errors


# ============================================================
# Async API Functions
# ============================================================

async def send_rich_message(
    bot_token: str,
    chat_id: int,
    message: Dict,
    message_thread_id: int = None,
    disable_notification: bool = False,
    protect_content: bool = False,
    reply_parameters: Dict = None,
    reply_markup: Dict = None
) -> Dict:
    """
    Send a rich message via Bot API.

    Args:
        bot_token: Bot authentication token
        chat_id: Target chat ID
        message: Rich message dict from build_message()
        message_thread_id: Optional thread ID for forum topics
        disable_notification: Send silently
        protect_content: Protect from forwarding/saving
        reply_parameters: Reply to message
        reply_markup: Inline keyboard

    Returns:
        API response dict
    """
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": message,
        "disable_notification": disable_notification,
        "protect_content": protect_content
    }

    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    if reply_parameters:
        payload["reply_parameters"] = reply_parameters
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def stream_rich_draft(
    bot_token: str,
    chat_id: int,
    frames: List[Dict],
    frame_delay: float = 0.5,
    draft_id: int = None
) -> List[Dict]:
    """
    Stream a sequence of rich message drafts (animated typing effect).

    Args:
        bot_token: Bot authentication token
        chat_id: Target chat ID
        frames: List of rich message dicts (each frame)
        frame_delay: Delay between frames in seconds
        draft_id: Optional custom draft ID (defaults to timestamp ms)

    Returns:
        List of API responses for each frame
    """
    import aiohttp
    import time

    if draft_id is None:
        draft_id = int(time.time() * 1000)

    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessageDraft"
    responses = []

    async with aiohttp.ClientSession() as session:
        for i, frame in enumerate(frames):
            payload = {
                "chat_id": chat_id,
                "draft_id": draft_id,
                "rich_message": frame
            }

            async with session.post(url, json=payload) as resp:
                result = await resp.json()
                responses.append(result)

                if not result.get("ok"):
                    print(f"⚠️ Frame {i+1} failed: {result}")

            if i < len(frames) - 1:
                await asyncio.sleep(frame_delay)

    return responses


async def edit_rich_message(
    bot_token: str,
    chat_id: int,
    message_id: int,
    message: Dict,
    reply_markup: Dict = None
) -> Dict:
    """
    Edit an existing message with new rich content.

    Note: Do NOT include 'thinking' blocks in final edit!
    """
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "rich_message": message
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def complete_stream(
    bot_token: str,
    chat_id: int,
    frames: List[Dict],
    frame_delay: float = 0.5,
    draft_id: int = None
) -> Dict:
    """
    Complete streaming workflow: send draft frames, then final message.

    Automatically removes 'thinking' blocks from final message.
    """
    import asyncio

    # Send draft frames
    await stream_rich_draft(bot_token, chat_id, frames, frame_delay, draft_id)

    # Send final message (last frame without thinking blocks)
    final_frame = frames[-1] if frames else {"blocks": []}
    final_blocks = [b for b in final_frame.get("blocks", []) if b.get("type") != "thinking"]
    final_message = {"blocks": final_blocks}

    # Add media if present in any frame
    for frame in reversed(frames):
        if "media" in frame:
            final_message["media"] = frame["media"]
            break

    return await send_rich_message(bot_token, chat_id, final_message)


# ============================================================
# Guardian Bots (Chat Join Requests)
# ============================================================

async def answer_join_request(
    bot_token: str,
    query_id: str,
    approve: bool = True,
    queue: bool = False,
    url: str = None
) -> Dict:
    """Answer a chat join request query (Guardian Bot)."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/answerChatJoinRequestQuery"
    payload = {
        "chat_join_request_query_id": query_id,
        "approve": approve,
        "queue": queue
    }
    if queue and url:
        payload["url"] = url

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def send_join_request_webapp(
    bot_token: str,
    query_id: str,
    webapp_url: str,
    platform: str = "android"
) -> Dict:
    """Send Mini App for chat join request verification."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendChatJoinRequestWebApp"
    payload = {
        "chat_join_request_query_id": query_id,
        "web_app": {
            "url": webapp_url,
            "platform": platform  # android, ios, desktop, macos, windows, linux
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


# ============================================================
# Utility Functions
# ============================================================

def to_json(message: Dict, indent: int = 2) -> str:
    """Convert message to pretty JSON for debugging."""
    return json.dumps(message, indent=indent, ensure_ascii=False)


def from_json(json_str: str) -> Dict:
    """Parse JSON to message dict."""
    return json.loads(json_str)


# ============================================================
# Pre-built Templates
# ============================================================

def template_factorization(n: int, attempts: List[Dict], success: bool, factors: tuple = None) -> Dict:
    """ShorBot-style factorization template."""
    rows = []
    for st in attempts:
        idx = st["attempt"]
        a = st["a"]
        if "shortcut_gcd" in st:
            g = st["shortcut_gcd"]
            f1, f2 = st["factors"]
            r_cell = plain("shortcut")
            res = bold(plain(f"{f1} × {f2}"))
        else:
            g = 1
            r = st.get("period_r", "?")
            r_cell = plain(str(r))
            if st.get("factors"):
                f1, f2 = st["factors"]
                res = bold(plain(f"{f1} × {f2}"))
            elif st.get("candidate_factors"):
                c1, c2 = st["candidate_factors"]
                res = plain(f"candidates: {c1}, {c2}")
            else:
                res = plain(st.get("result", "-"))
        rows.append([
            plain(str(idx)), plain(str(a)), plain(str(g)), r_cell, res
        ])

    table_block = table(rows, headers=["No.", "a", "gcd(a,N)", "period r", "result"])

    if success and factors:
        f1, f2 = factors
        result_html = paragraph(bold(plain("Result: ")), plain(f"{n} = "), bold(plain(f"{f1} × {f2}")))
    else:
        result_html = paragraph(plain(f"Tried {len(attempts)} attempts — failed to factorize."))

    code_block = preformatted(
        "x = a^(r/2) mod N\nfactor1 = gcd(x-1, N)\nfactor2 = gcd(x+1, N)",
        "python"
    )

    details_block = details(
        "Why this won't break RSA tomorrow",
        paragraph(plain("This is a "), bold(plain("classical simulation")), plain(" of Shor's period-finding step — no quantum speedup.")),
        paragraph(plain("Real Shor's algorithm needs thousands of logical qubits and error correction.")),
        paragraph(plain("Current quantum computers have < 1000 noisy qubits. RSA is safe for now."))
    )

    return build_message(
        heading(1, plain(f"Factorization N = {n}")),
        table_block,
        code_block,
        result_html,
        details_block
    )


def template_business_report(title: str, metrics: Dict, tables: List[Dict], notes: str = "", formula: str = "") -> Dict:
    """Business report template."""
    blocks = [
        heading(1, bold(plain(title))),
        divider()
    ]

    # Metrics summary
    if metrics:
        metric_items = []
        for k, v in metrics.items():
            metric_items.append(paragraph(plain(f"{k}: "), bold(plain(str(v)))))
        blocks.extend(metric_items)
        blocks.append(divider())

    # Tables
    for t in tables:
        blocks.append(table(t["rows"], headers=t.get("headers"), caption=t.get("caption", "")))

    # Notes
    if notes:
        blocks.append(details("Methodology & Assumptions", paragraph(plain(notes))))

    # Formula
    if formula:
        blocks.append(math_block(formula))

    blocks.append(footer(plain("Confidential — Internal Use Only")))

    return build_message(*blocks)


# ============================================================
# Example Usage / Demo
# ============================================================

if __name__ == "__main__":
    # Demo: Build a rich message
    msg = build_message(
        heading(1, bold(plain("Telegram Rich Messages Demo"))),
        divider(),
        paragraph(
            plain("This demonstrates "),
            bold(plain("inline formatting")),
            plain(": "),
            italic(plain("italic")),
            plain(", "),
            code("code"),
            plain(", "),
            url("link", "https://telegram.org"),
            plain(", "),
            math_inline("E=mc^2"),
            plain(".")
        ),
        heading(2, plain("Code Example")),
        preformatted("def hello():\n    print('Hello, Rich Messages!')\n\nhello()", "python"),
        heading(2, plain("Data Table")),
        table(
            [["Metric", "Value", "Unit"], ["Latency", "42", "ms"], ["Throughput", "1200", "req/s"]],
            headers=["Metric", "Value", "Unit"],
            caption="Performance Metrics"
        ),
        heading(2, plain("Math")),
        math_block("\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}"),
        details(
            "Implementation Notes",
            paragraph(plain("Built with Bot API 10.1+ Rich Messages.")),
            paragraph(plain("Supports streaming via sendRichMessageDraft."))
        ),
        footer(plain("Generated by Hermes Agent"))
    )

    print(to_json(msg))
    print("\n" + "="*50)
    valid, errors = validate_rich_message(msg)
    print(f"Valid: {valid}")
    if errors:
        print(f"Errors: {errors}")