#!/usr/bin/env python3
"""
Telegram Bot API 10.2 Features Demo
====================================

Demonstrates:
1. Ephemeral Messages in groups
2. Rich Messages with embedded media (InputRichMessageMedia)
3. Communities detection
4. Mini App security check
5. Voice notes in rich messages

Requires:
    pip install aiohttp

Usage:
    python demo_10_2.py --token YOUR_BOT_TOKEN --group -1001234567890 --user 123456789
"""

import asyncio
import argparse
import json
from typing import List, Dict, Any
import aiohttp


# ============================================================
# Rich Message Builders (minimal inline)
# ============================================================

def plain(text: str) -> Dict:
    return {"type": "plain", "text": text}

def bold(*content) -> Dict:
    return {"type": "bold", "text": list(content)}

def italic(*content) -> Dict:
    return {"type": "italic", "text": list(content)}

def code(text: str) -> Dict:
    return {"type": "code", "text": text}

def url(text: str, url: str) -> Dict:
    return {"type": "url", "text": [plain(text)], "url": url}

def paragraph(*content) -> Dict:
    return {"type": "paragraph", "content": list(content)}

def heading(level: int, *content) -> Dict:
    level = max(1, min(6, level))
    return {"type": "section_heading", "level": level, "content": list(content)}

def divider() -> Dict:
    return {"type": "divider"}

def preformatted(text: str, lang: str = "") -> Dict:
    return {"type": "preformatted", "content": [plain(text)], "language": lang}

def table_cell(content, header=False, align="left") -> Dict:
    if isinstance(content, str):
        content = [plain(content)]
    return {"type": "table_cell", "content": content, "header": header, "align": align}

def table_row(*cells) -> Dict:
    return {"type": "table_row", "cells": list(cells)}

def table(rows, headers=None, caption="", bordered=True, striped=True) -> Dict:
    table_rows = []
    if headers:
        table_rows.append(table_row(*[table_cell(h, header=True, align="center") for h in headers]))
    for row in rows:
        table_rows.append(table_row(*[table_cell(c, align="left" if isinstance(c, str) else "center") for c in row]))
    result = {"type": "table", "rows": table_rows, "bordered": bordered, "striped": striped}
    if caption:
        result["caption"] = {"type": "caption", "content": [plain(caption)]}
    return result

def details(summary: str, *blocks, open=False) -> Dict:
    return {"type": "details", "summary": [plain(summary)], "content": list(blocks), "open": open}

def build_message(*blocks, media=None) -> Dict:
    msg = {"blocks": list(blocks)}
    if media:
        msg["media"] = media
    return msg


# ============================================================
# API Functions
# ============================================================

async def send_message(bot_token: str, chat_id: int, payload: Dict) -> Dict:
    """Generic send message."""
    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def send_rich_message(bot_token: str, chat_id: int, message: Dict) -> Dict:
    """Send rich message."""
    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"chat_id": chat_id, "rich_message": message}) as resp:
            return await resp.json()


async def edit_ephemeral_text(bot_token: str, chat_id: int, message_id: int, ephemeral_user_id: int, text: str) -> Dict:
    """Edit ephemeral message."""
    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageText"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "chat_id": chat_id,
            "message_id": message_id,
            "ephemeral_user_id": ephemeral_user_id,
            "text": text,
            "parse_mode": "MarkdownV2"
        }) as resp:
            return await resp.json()


async def delete_ephemeral(bot_token: str, chat_id: int, message_id: int, ephemeral_user_id: int) -> Dict:
    """Delete ephemeral message."""
    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/deleteEphemeralMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            "chat_id": chat_id,
            "message_id": message_id,
            "ephemeral_user_id": ephemeral_user_id
        }) as resp:
            return await resp.json()


# ============================================================
# Demo Functions
# ============================================================

async def demo_ephemeral_welcome(bot_token: str, group_id: int, user_id: int):
    """Demo: Send ephemeral welcome to specific user in group."""
    print(f"\n{'='*60}")
    print("DEMO: Ephemeral Welcome Message")
    print(f"{'='*60}")
    print(f"Group: {group_id}, Target User: {user_id}")

    # Send ephemeral message
    result = await send_message(bot_token, group_id, {
        "chat_id": group_id,
        "text": "🎉 **Welcome to the group!**\n\nThis message is **only visible to you** and the bot.\nOther members cannot see it.\n\n*Expires in 24 hours.*",
        "parse_mode": "MarkdownV2",
        "ephemeral": True,
        "ephemeral_user_id": user_id,
        "ephemeral_expiration_date": int(__import__('time').time()) + 86400
    })

    if result.get("ok"):
        msg = result["result"]
        print(f"✅ Sent ephemeral message (ID: {msg.get('message_id')})")
        print(f"   is_ephemeral: {msg.get('is_ephemeral')}")
        print(f"   ephemeral_user_id: {msg.get('ephemeral_user_id')}")
        print(f"   expires: {msg.get('ephemeral_expiration_date')}")
    else:
        print(f"❌ Failed: {result}")

    return result.get("result")


async def demo_ephemeral_edit_delete(bot_token: str, group_id: int, user_id: int):
    """Demo: Edit and delete ephemeral message."""
    print(f"\n{'='*60}")
    print("DEMO: Edit & Delete Ephemeral Message")
    print(f"{'='*60}")

    # Send initial
    result = await send_message(bot_token, group_id, {
        "chat_id": group_id,
        "text": "Original ephemeral message",
        "ephemeral": True,
        "ephemeral_user_id": user_id
    })

    if not result.get("ok"):
        print(f"❌ Send failed: {result}")
        return

    msg = result["result"]
    msg_id = msg["message_id"]
    print(f"✅ Sent (ID: {msg_id})")

    await asyncio.sleep(1)

    # Edit
    edit_result = await edit_ephemeral_text(bot_token, group_id, msg_id, user_id,
        "✏️ *Edited!* This ephemeral message was updated.")
    print(f"✅ Edited: {edit_result.get('ok')}")

    await asyncio.sleep(1)

    # Delete
    del_result = await delete_ephemeral(bot_token, group_id, msg_id, user_id)
    print(f"✅ Deleted: {del_result.get('ok')}")


async def demo_rich_with_media(bot_token: str, chat_id: int):
    """Demo: Rich message with embedded photo (10.2 InputRichMessageMedia)."""
    print(f"\n{'='*60}")
    print("DEMO: Rich Message with Embedded Media")
    print(f"{'='*60}")

    blocks = [
        heading(1, bold(plain("Q3 2026 Analytics Dashboard"))),
        divider(),
        paragraph(plain("Revenue grew "), bold(plain("23%")), plain(" YoY")),
        table(
            [["$3.4M", "$4.2M", "+23%"], ["1.2M", "1.5M", "+25%"]],
            headers=["Q2", "Q3", "Δ"],
            caption="Quarterly Revenue"
        ),
        details(
            "Methodology",
            paragraph(plain("Data from internal analytics platform.")),
            open=False
        ),
        paragraph(plain("Chart: "), url("Revenue Trend", "https://example.com/chart.png"))
    ]

    # NOTE: Requires actual file_id from uploaded photo
    # For demo, we'll send without media
    print("ℹ️  Sending rich message without media (need file_id for media)")
    result = await send_rich_message(bot_token, chat_id, build_message(*blocks))

    if result.get("ok"):
        print("✅ Rich message sent successfully")
    else:
        print(f"❌ Failed: {result}")


async def demo_voice_note_rich(bot_token: str, chat_id: int):
    """Demo: Voice note in rich message (10.2 InputMediaVoiceNote)."""
    print(f"\n{'='*60}")
    print("DEMO: Voice Note in Rich Message")
    print(f"{'='*60}")
    print("ℹ️  Requires voice file_id - showing structure only")

    # Structure for voice note rich message
    blocks = [
        heading(2, plain("Voice Update")),
        paragraph(plain("Here's the latest audio briefing:"))
    ]

    # Would use:
    # media = {"type": "voice_note", "media": "VOICE_FILE_ID"}
    # message = build_message(*blocks, media=media)
    print("Structure:")
    print(json.dumps({
        "blocks": blocks,
        "media": {"type": "voice_note", "media": "VOICE_FILE_ID"}
    }, indent=2, ensure_ascii=False))


async def demo_communities_detection(bot_token: str, chat_id: int):
    """Demo: Detect community from chat."""
    print(f"\n{'='*60}")
    print("DEMO: Community Detection")
    print(f"{'='*60}")

    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"chat_id": chat_id}) as resp:
            result = await resp.json()

    if result.get("ok"):
        chat = result["result"]
        community = chat.get("community")
        if community:
            print(f"✅ Chat belongs to Community:")
            print(f"   ID: {community.get('id')}")
            print(f"   Title: {community.get('title')}")
        else:
            print("ℹ️  Chat is not part of a Community")
    else:
        print(f"❌ Failed: {result}")


async def demo_bot_command_ephemeral(bot_token: str):
    """Demo: Set bot commands with ephemeral flag."""
    print(f"\n{'='*60}")
    print("DEMO: Ephemeral Bot Commands")
    print(f"{'='*60}")

    commands = [
        {"command": "start", "description": "Start the bot", "ephemeral": True},
        {"command": "help", "description": "Show help", "ephemeral": True},
        {"command": "private", "description": "Private command", "ephemeral": True},
        {"command": "public", "description": "Public command", "ephemeral": False}
    ]

    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"commands": commands}) as resp:
            result = await resp.json()

    if result.get("ok"):
        print("✅ Commands set with ephemeral flags:")
        for cmd in commands:
            flag = "🔒 Ephemeral" if cmd.get("ephemeral") else "🌐 Public"
            print(f"   /{cmd['command']} - {cmd['description']} [{flag}]")
    else:
        print(f"❌ Failed: {result}")


async def demo_mini_app_security():
    """Demo: Mini App external origin security check."""
    print(f"\n{'='*60}")
    print("DEMO: Mini App Security Check (July 20, 2026)")
    print(f"{'='*60}")

    test_cases = [
        ("https://myapp.example.com", "https://myapp.example.com/page"),
        ("https://myapp.example.com", "https://evil.com/phishing"),
        ("https://myapp.example.com", "https://sub.myapp.example.com/link"),
        ("https://myapp.example.com", "https://api.myapp.example.com/callback"),
    ]

    for app_url, external_url in test_cases:
        from urllib.parse import urlparse
        app_domain = urlparse(app_url).netloc
        ext_domain = urlparse(external_url).netloc
        same = app_domain == ext_domain
        sub = ext_domain.endswith("." + app_domain) or app_domain.endswith("." + ext_domain)
        blocked = not (same or sub)

        status = "🚫 BLOCKED" if blocked else "✅ ALLOWED"
        print(f"   {external_url}")
        print(f"      → {status} (same_origin={same}, subdomain={sub})")

    print("\n⚠️  After July 20, 2026: BLOCKED origins lose Mini App API access")
    print("   Opt-out: @BotFather → Mini Apps → Security Settings")


# ============================================================
# Main
# ============================================================

async def main():
    parser = argparse.ArgumentParser(description="Telegram Bot API 10.2 Demo")
    parser.add_argument("--token", required=True, help="Bot token")
    parser.add_argument("--group", type=int, help="Group chat ID (negative) for ephemeral demos")
    parser.add_argument("--user", type=int, help="Target user ID for ephemeral demos")
    parser.add_argument("--chat", type=int, help="Chat ID for rich message demos")
    parser.add_argument("--demo", choices=["ephemeral", "rich", "voice", "community", "commands", "security", "all"],
                        default="all", help="Which demo to run")

    args = parser.parse_args()

    print(f"🎬 Telegram Bot API 10.2 Demo")
    print(f"   Bot: {args.token[:10]}...")
    print(f"   Demo: {args.demo}")

    if args.demo in ("ephemeral", "all"):
        if not args.group or not args.user:
            print("⚠️  Ephemeral demo requires --group and --user")
        else:
            await demo_ephemeral_welcome(args.token, args.group, args.user)
            await demo_ephemeral_edit_delete(args.token, args.group, args.user)

    if args.demo in ("rich", "all"):
        chat = args.chat or args.group
        if not chat:
            print("⚠️  Rich demo requires --chat or --group")
        else:
            await demo_rich_with_media(args.token, chat)

    if args.demo in ("voice", "all"):
        chat = args.chat or args.group
        if not chat:
            print("⚠️  Voice demo requires --chat or --group")
        else:
            await demo_voice_note_rich(args.token, chat)

    if args.demo in ("community", "all"):
        chat = args.chat or args.group
        if not chat:
            print("⚠️  Community demo requires --chat or --group")
        else:
            await demo_communities_detection(args.token, chat)

    if args.demo in ("commands", "all"):
        await demo_bot_command_ephemeral(args.token)

    if args.demo in ("security", "all"):
        await demo_mini_app_security()

    print(f"\n{'='*60}")
    print("✅ All demos complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())