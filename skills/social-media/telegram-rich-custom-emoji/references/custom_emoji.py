"""
Telegram Rich Messages — Custom Emoji Helpers
==============================================

Python helpers for using RichTextCustomEmoji in structured rich messages.
Uses emoji IDs from user's collection.

IMPORTANT: Use RichTextCustomEmoji JSON format, NOT <tg-emoji> HTML tag!
HTML tag causes RICH_MESSAGE_BLOCK_UNSUPPORTED error.

Usage:
    from skills.social_media.telegram_rich_custom_emoji.references.custom_emoji import (
        custom_emoji, custom_emoji_raw, plain, paragraph, heading,
        build_message, send_rich_message
    )

    msg = build_message(
        heading(1, custom_emoji("doc"), plain(" Report"), custom_emoji("stars")),
        paragraph(custom_emoji("shield"), plain(" Protected by custom emoji"))
    )
"""

from typing import Dict, Any, List


# ============================================================
# Emoji Registry (from user's messages)
# ============================================================

CUSTOM_EMOJI = {
    # UI / Status
    "doc": ("5334882760735598374", "📝"),
    "shield": ("4958900559139570572", "🛡"),
    "chart": ("5431577498364158238", "📊"),
    "chat": ("5449509905947967949", "💬"),
    "warn": ("5447644880824181073", "⚠"),
    "ok": ("5447363161034346459", "👌"),
    "point": ("5210997160681688876", "🫵"),
    "point_right": ("5296365472550244967", "👉"),
    "flex": ("5296691786985527033", "💪"),
    "crown": ("5210952531676516344", "👑"),
    "calendar": ("5192784923093652913", "📅"),
    "calendar": ("5192784923093652913", "📅"),

    # Faces / Reactions
    "relieved": ("5449619723966761441", "😌"),
    "smirk": ("5384214488809490070", "😏"),
    "joy": ("5298937724168853193", "😂"),
    "joy2": ("5384478698017670587", "😂"),
    "grin": ("5296786967755771785", "😁"),
    "tear": ("5190491238758898985", "🥲"),
    "tear2": ("5298524385106218208", "🥲"),
    "blush": ("5190867898800821266", "😊"),
    "relaxed": ("5298812156504987574", "☺️"),
    "relieved2": ("5447526417036234763", "😌"),
    "stars": ("5190683945351535076", "🤩"),
    "relieved3": ("5211101893459199876", "😌"),
    "neutral": ("5384453284696181912", "🫤"),
    "kiss": ("5296335880225575986", "😗"),
    "kiss2": ("5447193685919811994", "😙"),
    "raised_brow": ("5384294976496619218", "🤨"),
    "raised_brow2": ("5190783670197180086", "🤨"),
    "thinking": ("5296739894914207637", "🤔"),
    "thinking2": ("5447271394763099136", "🤔"),
    "thinking3": ("5210985766133453153", "🤔"),
    "shrug": ("5211112038171958439", "🤷‍♂️"),
    "no": ("5190568977666957657", "🙅‍♂️"),
    "scream": ("5296525713485089826", "😱"),
    "tired": ("5210808229365305258", "😫"),
    "neutral_face": ("5384157249780337109", "😑"),
    "monocle": ("5384182985224374928", "🧐"),
    "monocle2": ("5447610314927396099", "🧐"),
    "disappointed": ("5193200486949346651", "😞"),
    "zipper": ("5190415054629002671", "🤐"),
    "flushed": ("5192857499451021759", "😳"),
    "neutral2": ("5210890383499745988", "😑"),
    "neutral3": ("5447348871678154623", "😐"),
    "angry": ("5296305622180972936", "😡"),
    "unamused": ("5384059066827949054", "😒"),
    "yum": ("5298519909750296720", "😋"),
    "yum2": ("5193133348020574567", "😋"),
    "tongue": ("5447198809815795961", "👅"),
    "biting_lip": ("5447630192036040634", "🫦"),
    "kiss_closed": ("5211042257838296209", "😚"),
    "grimace": ("5190958793193710110", "😬"),
    "grimace2": ("5384187537889710348", "😬"),
    "open_mouth": ("5213305791502634699", "😮"),
    "melting": ("5190660975866437599", "🫠"),

    # Objects / Symbols
    "gun": ("5296383305254459545", "🔫"),
    "gun2": ("5192781392630537817", "🔫"),
    "foot": ("5296732718023857804", "🦶"),
    "foot2": ("5210972980015810506", "🦶"),
    "eggplant": ("5447432125324216825", "🍆"),
    "eggplant2": ("5211025120918785460", "🍆"),
    "eggplant3": ("5211155151053675393", "🍆"),
    "banana": ("5314647211299067950", "🍌"),
    "donut": ("5316870406630564710", "🍩"),
    "donut2": ("5211042502651432248", "🍩"),
    "heart": ("5316715774923004572", "❤️"),
    "broken_heart": ("5190742593129971422", "💔"),
    "broken_heart2": ("5190775904896308220", "💔"),
    "broken_heart3": ("5210777181046722111", "💔"),
    "heart_arrow": ("5210767689168999246", "💘"),
    "hearts": ("5213447602732813642", "💞"),
    "poop": ("5296250904297624056", "💩"),
    "brick": ("5316742244806451762", "🧱"),
    "dash": ("5298854260069389723", "💨"),
    "exploding": ("5447163161587241349", "🤯"),
    "blood": ("5384285987130065744", "🩸"),
    "microbe": ("5298775778131986041", "🦠"),
    "ice": ("5384108682290152083", "🧊"),
    "knife": ("5384495396850520754", "🔪"),
    "middle": ("5192966772008966700", "🖕"),
    "middle2": ("5190640291303939012", "🖕"),
    "love_sign": ("5193037226652491753", "🤟"),
    "potato": ("5384443861537932638", "🥔"),
    "brain": ("5447595110743168717", "🧠"),
    "coffee": ("5314806674844835288", "☕"),
    "coffee2": ("5316645728301374271", "☕"),
    "lungs": ("5296426834748002089", "🫁"),
    "toilet": ("5193157563046189671", "🧻"),
    "money": ("5317054012187499321", "💰"),
    "trap": ("5190404278556055959", "🪤"),
    "money_wings": ("5447458260200214425", "💸"),
    "money_wings2": ("5382199784075448966", "💸"),
    "skull": ("5190682871609712455", "💀"),
    "xray": ("5193012388856618565", "🩻"),
    "soap": ("5316965570220941367", "🧼"),

    # Animals / Characters
    "vampire": ("5447191366637476040", "🧛‍♂️"),
    "cowboy": ("5384268407828924341", "🤠"),
    "wolf": ("5192808914780971277", "🐺"),
    "black_cat": ("5213311533873907167", "🐈‍⬛"),
    "dragon": ("5447456593752903617", "🐲"),
    "peach": ("5447614579829921377", "🍑"),
    "chestnut": ("5316885872807794414", "🌰"),
}


# ============================================================
# Helper Functions
# ============================================================

def custom_emoji(key: str) -> Dict[str, Any]:
    """
    Create RichTextCustomEmoji by key from registry.

    Args:
        key: Emoji key from CUSTOM_EMOJI registry

    Returns:
        RichTextCustomEmoji dict
    """
    emoji_id, fallback = CUSTOM_EMOJI.get(key, ("5334882760735598374", "📝"))
    return {
        "type": "custom_emoji",
        "text": fallback,
        "custom_emoji_id": emoji_id
    }


def custom_emoji_raw(emoji_id: str, fallback: str) -> Dict[str, Any]:
    """
    Create RichTextCustomEmoji with raw ID and fallback.

    Args:
        emoji_id: Custom emoji document ID
        fallback: Unicode fallback emoji

    Returns:
        RichTextCustomEmoji dict
    """
    return {
        "type": "custom_emoji",
        "text": fallback,
        "custom_emoji_id": emoji_id
    }


def list_emojis(category: str = None) -> Dict[str, tuple]:
    """List available emojis, optionally filtered by category prefix."""
    if category:
        return {k: v for k, v in CUSTOM_EMOJI.items() if k.startswith(category)}
    return CUSTOM_EMOJI.copy()


def search_emojis(query: str) -> Dict[str, tuple]:
    """Search emojis by key or fallback character."""
    query = query.lower()
    return {
        k: v for k, v in CUSTOM_EMOJI.items()
        if query in k.lower() or query in v[1]
    }


# ============================================================
# RichText Base Types
# ============================================================

def plain(text: str) -> Dict[str, Any]:
    return {"type": "plain", "text": text}


def bold(*content: Dict) -> Dict[str, Any]:
    return {"type": "bold", "text": list(content)}


def italic(*content: Dict) -> Dict[str, Any]:
    return {"type": "italic", "text": list(content)}


def code(text: str) -> Dict[str, Any]:
    return {"type": "code", "text": text}


def url(text: str, url: str) -> Dict[str, Any]:
    return {"type": "url", "text": [plain(text)], "url": url}


def math_inline(latex: str) -> Dict[str, Any]:
    return {"type": "math", "text": latex}


# ============================================================
# RichBlock Builders
# ============================================================

def paragraph(*content: Dict) -> Dict[str, Any]:
    return {"type": "paragraph", "content": list(content)}


def heading(level: int, *content: Dict) -> Dict[str, Any]:
    level = max(1, min(6, level))
    return {"type": "section_heading", "level": level, "content": list(content)}


def divider() -> Dict[str, Any]:
    return {"type": "divider"}


def preformatted(text: str, language: str = "") -> Dict[str, Any]:
    return {"type": "preformatted", "content": [plain(text)], "language": language}


def math_block(latex: str) -> Dict[str, Any]:
    return {"type": "math", "content": latex}


def table_cell(content, header: bool = False, align: str = "left") -> Dict[str, Any]:
    if isinstance(content, str):
        content = [plain(content)]
    return {"type": "table_cell", "content": content, "header": header, "align": align}


def table_row(*cells: Dict) -> Dict[str, Any]:
    return {"type": "table_row", "cells": list(cells)}


def table(rows, headers=None, caption="", bordered=True, striped=True) -> Dict[str, Any]:
    table_rows = []
    if headers:
        table_rows.append(table_row(*[table_cell(h, header=True, align="center") for h in headers]))
    for row in rows:
        table_rows.append(table_row(*[table_cell(c, align="left" if isinstance(c, str) else "center") for c in row]))
    result = {"type": "table", "rows": table_rows, "bordered": bordered, "striped": striped}
    if caption:
        result["caption"] = {"type": "caption", "content": [plain(caption)]}
    return result


def details(summary: str, *blocks: Dict, open: bool = False) -> Dict[str, Any]:
    return {"type": "details", "summary": [plain(summary)], "content": list(blocks), "open": open}


def footer(*content: Dict) -> Dict[str, Any]:
    return {"type": "footer", "content": list(content)}


def build_message(*blocks: Dict, media: Dict = None) -> Dict[str, Any]:
    msg = {"blocks": list(blocks)}
    if media:
        msg["media"] = media
    return msg


# ============================================================
# Example Builders
# ============================================================

def demo_emoji_showcase() -> Dict[str, Any]:
    """Showcase all custom emojis in a table."""
    rows = []
    for key, (eid, fallback) in sorted(CUSTOM_EMOJI.items()):
        rows.append([
            plain(key),
            custom_emoji_raw(eid, fallback),
            plain(eid),
            plain(fallback)
        ])

    return build_message(
        heading(1, custom_emoji("doc"), plain(" Custom Emoji Registry"), custom_emoji("stars")),
        paragraph(plain(f"Total: {len(CUSTOM_EMOJI)} custom emojis from your collection")),
        table(
            rows,
            headers=["Key", "Emoji", "ID", "Fallback"],
            caption="Custom Emoji Collection"
        )
    )


def demo_rich_message_with_emojis() -> Dict[str, Any]:
    """Example rich message using custom emojis throughout."""
    return build_message(
        heading(1,
            custom_emoji("doc"), plain(" "),
            plain("Rich Messages + Custom Emoji"),
            plain(" "), custom_emoji("stars")
        ),
        divider(),
        paragraph(
            plain("Use "), custom_emoji("brain"), plain(" "),
            bold(plain("RichTextCustomEmoji")), plain(" inline entity — "),
            custom_emoji("ok"), plain(" NOT "),
            code("<tg-emoji>"), plain(" HTML tag!")
        ),
        paragraph(
            custom_emoji("shield"), plain(" "),
            plain("Bot API 10.1+ supports structured JSON format only")
        ),
        heading(2, custom_emoji("chart"), plain(" Feature Comparison")),
        table(
            [
                ["HTML <tg-emoji>", custom_emoji("no"), plain("RICH_MESSAGE_BLOCK_UNSUPPORTED")],
                ["JSON RichTextCustomEmoji", custom_emoji("ok"), plain("Fully supported ✓")],
                ["Unicode fallback", custom_emoji("yum"), plain("Always works")],
            ],
            headers=["Method", "Status", "Notes"]
        ),
        heading(2, custom_emoji("heart"), plain(" Inline Usage")),
        paragraph(
            plain("Mix with other formatting: "),
            bold(custom_emoji("stars")), plain(" "),
            italic(custom_emoji("heart")), plain(" "),
            code("custom_emoji('key')"), plain(" "),
            custom_emoji("brain")
        ),
        details(
            "How it works",
            paragraph(
                custom_emoji("monocle"), plain(" "),
                plain("1. Register emoji IDs in CUSTOM_EMOJI dict")
            ),
            paragraph(
                custom_emoji("monocle"), plain(" "),
                plain("2. Use custom_emoji('key') to create RichTextCustomEmoji")
            ),
            paragraph(
                custom_emoji("monocle"), plain(" "),
                plain("3. Embed in paragraphs, headings, tables, details, captions")
            ),
            paragraph(
                custom_emoji("warn"), plain(" "),
                bold(plain("NEVER use <tg-emoji> HTML tag in rich messages!"))
            ),
            open=False
        ),
        footer(
            custom_emoji("crown"), plain(" "),
            plain("Powered by Telegram Bot API 10.1+ "),
            custom_emoji("brain")
        )
    )


# ============================================================
# Async API (requires aiohttp)
# ============================================================

async def send_rich_message(bot_token: str, chat_id: int, message: Dict) -> Dict[str, Any]:
    """Send rich message via Bot API."""
    import aiohttp
    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"chat_id": chat_id, "rich_message": message}) as resp:
            return await resp.json()


# ============================================================
# Demo / Test
# ============================================================

if __name__ == "__main__":
    import json

    # Showcase
    print("=== CUSTOM EMOJI REGISTRY ===")
    print(f"Total emojis: {len(CUSTOM_EMOJI)}")
    print()

    # Search demo
    print("=== SEARCH 'heart' ===")
    for k, v in search_emojis("heart").items():
        print(f"  {k}: {v[1]} (ID: {v[0]})")
    print()

    # Build demo message
    msg = demo_rich_message_with_emojis()
    print("=== RICH MESSAGE JSON ===")
    print(json.dumps(msg, indent=2, ensure_ascii=False))
    print()

    # Validate structure
    def validate(message):
        blocks = message.get("blocks", [])
        emoji_count = 0
        for block in blocks:
            if block.get("type") == "paragraph":
                for item in block.get("content", []):
                    if item.get("type") == "custom_emoji":
                        emoji_count += 1
        return emoji_count

    print(f"Custom emojis in message: {validate(msg)}")