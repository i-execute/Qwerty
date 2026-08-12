"""
Telegram Custom Emoji Helpers for Rich Messages
================================================

Bot API 10.1+ supports custom emojis via RichTextCustomEmoji inline entity.

Format: {"type": "custom_emoji", "text": "😀", "custom_emoji_id": "5334882760735598374"}

Usage:
    from skills.social_media.telegram_custom_emoji.references.emoji_helpers import (
        custom_emoji, CE, EMOJI_IDS, paragraph, bold, plain
    )

    # Single custom emoji
    ce = custom_emoji("😎", "5334882760735598374")

    # Predefined constants
    paragraph(plain("Status: "), CE.party, plain(" Done!"))

    # In heading
    heading(1, bold(plain("Title ")), CE.cool)

    # With fallback
    custom_emoji("🔥", "5384294976496619218")  # text="🔥" is fallback
"""

from typing import Dict, Any


# ============================================================
# Your Custom Emoji IDs (from messages)
# ============================================================

EMOJI_IDS: Dict[str, str] = {
    # First batch
    "relieved_1": "5449619723966761441",      # 😌
    "smirk": "5384214488809490070",           # 😏
    "joy_1": "5298937724168853193",           # 😂
    "joy_2": "5384478698017670587",           # 😂
    "grin": "5296786967755771785",            # 😁
    "ok_hand": "5447363161034346459",         # 👌
    "smiling_tear_1": "5190491238758898985",  # 🥲
    "smiling_tear_2": "5298524385106218208",  # 🥲
    "smile": "5190867898800821266",           # 😊
    "relaxed": "5298812156504987574",         # ☺️
    "relieved_2": "5447526417036234763",      # 😌
    "star_struck": "5190683945351535076",     # 🤩
    "relieved_3": "5211101893459199876",      # 😌
    "neutral_face": "5384453284696181912",    # 🫤
    "kissing": "5296335880225575986",         # 😗
    "kissing_smiling": "5447193685919811994", # 😙
    "raised_eyebrow": "5384294976496619218",  # 🤨
    "shrug": "5211112038171958439",           # 🤷‍♂️
    # Second batch (approximate IDs - update with actuals)
    "eggplant_1": "5211025120918785460",      # 🍆
    "eggplant_2": "5211155151053675393",      # 🍆
    "banana": "5314647211299067950",           # 🍌
    "donut": "5316870406630564710",           # 🍩
    "heart": "5316715774923004572",           # ❤️
    "broken_heart_1": "5190742593129971422",  # 💔
    "heart_arrow": "5210767689168999246",     # 💘
    "broken_heart_2": "5190775904896308220",  # 💔
    "broken_heart_3": "5210777181046722111",  # 💔
    "potato": "5384443861537932638",          # 🥔
    "brain": "5447595110743168717",           # 🧠
    "coffee_1": "5314806674844835288",        # ☕️
    "coffee_2": "5316645728301374271",        # ☕️
    "lungs": "5296426834748002089",           # 🫁
    "toilet_paper": "5193157563046189671",    # 🧻
    "money_bag": "5317054012187499321",       # 💰
    "trap": "5190404278556055959",            # 🪤
    "money_wings_1": "5447458260200214425",   # 💸
    "money_wings_2": "5382199784075448966",   # 💸
    "skull": "5190682871609712455",           # 💀
    "xray": "5193012388856618565",            # 🩻
    "calendar": "5192784923093652913",        # 📅
}


# ============================================================
# Helper Functions
# ============================================================

def custom_emoji(text: str, emoji_id: str) -> Dict[str, Any]:
    """
    Create RichTextCustomEmoji object.

    Args:
        text: Fallback Unicode emoji (shown if custom emoji fails to load)
        emoji_id: Custom emoji ID from sticker pack

    Returns:
        Dict for use in RichText content arrays
    """
    return {
        "type": "custom_emoji",
        "text": text,
        "custom_emoji_id": str(emoji_id)
    }


def ce_by_name(name: str, fallback: str = None) -> Dict[str, Any]:
    """Create custom emoji by name from EMOJI_IDS."""
    emoji_id = EMOJI_IDS.get(name)
    if not emoji_id:
        raise KeyError(f"Emoji '{name}' not found in EMOJI_IDS")
    fb = fallback or list(EMOJI_IDS.keys())[list(EMOJI_IDS.values()).index(emoji_id)][0]
    # Find a reasonable fallback
    fallbacks = {
        "relieved_1": "😌", "smirk": "😏", "joy_1": "😂", "joy_2": "😂",
        "grin": "😁", "ok_hand": "👌", "smiling_tear_1": "🥲", "smiling_tear_2": "🥲",
        "smile": "😊", "relaxed": "☺️", "relieved_2": "😌", "star_struck": "🤩",
        "relieved_3": "😌", "neutral_face": "🫤", "kissing": "😗", "kissing_smiling": "😙",
        "raised_eyebrow": "🤨", "shrug": "🤷‍♂️",
        "eggplant_1": "🍆", "eggplant_2": "🍆", "banana": "🍌", "donut": "🍩",
        "heart": "❤️", "broken_heart_1": "💔", "heart_arrow": "💘",
        "broken_heart_2": "💔", "broken_heart_3": "💔",
        "potato": "🥔", "brain": "🧠", "coffee_1": "☕", "coffee_2": "☕",
        "lungs": "🫁", "toilet_paper": "🧻", "money_bag": "💰",
        "trap": "🪤", "money_wings_1": "💸", "money_wings_2": "💸",
        "skull": "💀", "xray": "🩻", "calendar": "📅",
    }
    return custom_emoji(fallbacks.get(name, "😀"), emoji_id)


# ============================================================
# Predefined Constants (CE namespace)
# ============================================================

class CE:
    """Predefined custom emoji constants for easy access."""

    # Faces
    relieved = custom_emoji("😌", EMOJI_IDS["relieved_1"])
    smirk = custom_emoji("😏", EMOJI_IDS["smirk"])
    joy = custom_emoji("😂", EMOJI_IDS["joy_1"])
    joy_alt = custom_emoji("😂", EMOJI_IDS["joy_2"])
    grin = custom_emoji("😁", EMOJI_IDS["grin"])
    ok = custom_emoji("👌", EMOJI_IDS["ok_hand"])
    tear_smile = custom_emoji("🥲", EMOJI_IDS["smiling_tear_1"])
    tear_smile_alt = custom_emoji("🥲", EMOJI_IDS["smiling_tear_2"])
    smile = custom_emoji("😊", EMOJI_IDS["smile"])
    relaxed = custom_emoji("☺️", EMOJI_IDS["relaxed"])
    relieved_alt = custom_emoji("😌", EMOJI_IDS["relieved_2"])
    star_struck = custom_emoji("🤩", EMOJI_IDS["star_struck"])
    relieved_alt2 = custom_emoji("😌", EMOJI_IDS["relieved_3"])
    neutral = custom_emoji("🫤", EMOJI_IDS["neutral_face"])
    kiss = custom_emoji("😗", EMOJI_IDS["kissing"])
    kiss_smile = custom_emoji("😙", EMOJI_IDS["kissing_smiling"])
    eyebrow = custom_emoji("🤨", EMOJI_IDS["raised_eyebrow"])
    shrug = custom_emoji("🤷‍♂️", EMOJI_IDS["shrug"])

    # Objects/Food
    eggplant = custom_emoji("🍆", EMOJI_IDS["eggplant_1"])
    eggplant_alt = custom_emoji("🍆", EMOJI_IDS["eggplant_2"])
    banana = custom_emoji("🍌", EMOJI_IDS["banana"])
    donut = custom_emoji("🍩", EMOJI_IDS["donut"])
    heart = custom_emoji("❤️", EMOJI_IDS["heart"])
    broken_heart = custom_emoji("💔", EMOJI_IDS["broken_heart_1"])
    heart_arrow = custom_emoji("💘", EMOJI_IDS["heart_arrow"])
    broken_heart_alt = custom_emoji("💔", EMOJI_IDS["broken_heart_2"])
    broken_heart_alt2 = custom_emoji("💔", EMOJI_IDS["broken_heart_3"])
    potato = custom_emoji("🥔", EMOJI_IDS["potato"])
    brain = custom_emoji("🧠", EMOJI_IDS["brain"])
    coffee = custom_emoji("☕", EMOJI_IDS["coffee_1"])
    coffee_alt = custom_emoji("☕", EMOJI_IDS["coffee_2"])
    lungs = custom_emoji("🫁", EMOJI_IDS["lungs"])
    toilet = custom_emoji("🧻", EMOJI_IDS["toilet_paper"])
    money = custom_emoji("💰", EMOJI_IDS["money_bag"])
    trap = custom_emoji("🪤", EMOJI_IDS["trap"])
    money_wings = custom_emoji("💸", EMOJI_IDS["money_wings_1"])
    money_wings_alt = custom_emoji("💸", EMOJI_IDS["money_wings_2"])
    skull = custom_emoji("💀", EMOJI_IDS["skull"])
    xray = custom_emoji("🩻", EMOJI_IDS["xray"])
    calendar = custom_emoji("📅", EMOJI_IDS["calendar"])

    # Semantic groups
    party = star_struck
    cool = smirk
    thinking = eyebrow
    approved = ok
    sad = tear_smile
    love = heart
    broken = broken_heart
    money_bag_emoji = money
    dead = skull


# ============================================================
# RichText Base Helpers (minimal inline)
# ============================================================

def plain(text: str) -> Dict[str, Any]:
    return {"type": "plain", "text": text}

def bold(*content) -> Dict[str, Any]:
    return {"type": "bold", "text": list(content)}

def italic(*content) -> Dict[str, Any]:
    return {"type": "italic", "text": list(content)}

def paragraph(*content) -> Dict[str, Any]:
    return {"type": "paragraph", "content": list(content)}

def heading(level: int, *content) -> Dict[str, Any]:
    return {"type": "section_heading", "level": max(1, min(6, level)), "content": list(content)}

def build_message(*blocks) -> Dict[str, Any]:
    return {"blocks": list(blocks)}


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    import json

    # Example 1: Simple paragraph with custom emoji
    msg1 = build_message(
        paragraph(
            plain("Server status: "),
            CE.approved,
            plain(" All systems operational "),
            CE.party
        )
    )
    print("Example 1 - Status:")
    print(json.dumps(msg1, indent=2, ensure_ascii=False))
    print()

    # Example 2: Heading with emoji
    msg2 = build_message(
        heading(1, bold(plain("Deploy Complete ")), CE.cool),
        paragraph(
            plain("Version 2.4.1 deployed successfully "),
            CE.rocket if hasattr(CE, 'rocket') else CE.party
        )
    )
    print("Example 2 - Deploy:")
    print(json.dumps(msg2, indent=2, ensure_ascii=False))
    print()

    # Example 3: Using by name
    msg3 = build_message(
        paragraph(
            plain("Mood: "),
            ce_by_name("star_struck"),
            plain(" | "),
            ce_by_name("brain"),
            plain(" | "),
            ce_by_name("money")
        )
    )
    print("Example 3 - By name:")
    print(json.dumps(msg3, indent=2, ensure_ascii=False))
    print()

    # Show all available
    print("Available emoji names:")
    for name in sorted(EMOJI_IDS.keys()):
        print(f"  CE.{name}  →  {EMOJI_IDS[name]}")