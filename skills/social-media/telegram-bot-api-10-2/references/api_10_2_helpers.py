"""
Telegram Bot API 10.2 — Ephemeral Messages, Communities, Rich Media Helpers
==========================================================================

Python helpers for Bot API 10.2 features released July 14, 2026.

Features:
- Ephemeral Messages (group messages visible to one user)
- Rich Messages with InputRichMessageMedia
- Communities (read-only detection)
- InputMediaVoiceNote
- InputRichBlockListItem

Installation:
    pip install aiohttp

Usage:
    from skills.social_media.telegram_bot_api_10_2.references.api_10_2_helpers import (
        send_ephemeral, edit_ephemeral_text, delete_ephemeral, reply_to_ephemeral,
        rich_message_with_media, send_voice_note_rich,
        detect_community, get_community_info
    )

    # Ephemeral welcome in group
    await send_ephemeral(token, group_id, "Welcome! This is private.", user_id=123456)

    # Rich message with embedded photo
    await rich_message_with_media(token, chat_id, blocks, "photo", file_id)
"""

from typing import List, Dict, Any, Optional, Union
import json
import time


# ============================================================
# Ephemeral Messages Helpers
# ============================================================

async def send_ephemeral(
    bot_token: str,
    chat_id: int,
    text: str,
    ephemeral_user_id: int,
    expiration_seconds: int = 86400,  # 24 hours default
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """
    Send ephemeral message visible only to specific user in group.

    Args:
        bot_token: Bot authentication token
        chat_id: Group/supergroup chat ID (negative)
        text: Message text
        ephemeral_user_id: User ID who can see this message
        expiration_seconds: Auto-delete after this many seconds (default 86400 = 24h)
        parse_mode: MarkdownV2, HTML, or None
        **kwargs: Additional sendMessage parameters (reply_markup, etc.)

    Returns:
        API response with Message object
    """
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "ephemeral": True,
        "ephemeral_user_id": ephemeral_user_id,
        "ephemeral_expiration_date": int(time.time()) + expiration_seconds
    }
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def send_ephemeral_media(
    bot_token: str,
    chat_id: int,
    ephemeral_user_id: int,
    media_type: str,  # "photo", "video", "animation", "audio", "document", "sticker", "voice", "video_note", "contact", "location", "venue", "poll"
    media: str,  # file_id or attach://
    caption: str = "",
    expiration_seconds: int = 86400,
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """Send ephemeral media message."""
    import aiohttp

    method_map = {
        "photo": "sendPhoto",
        "video": "sendVideo",
        "animation": "sendAnimation",
        "audio": "sendAudio",
        "document": "sendDocument",
        "sticker": "sendSticker",
        "voice": "sendVoice",
        "video_note": "sendVideoNote",
        "contact": "sendContact",
        "location": "sendLocation",
        "venue": "sendVenue",
        "poll": "sendPoll",
    }

    method = method_map.get(media_type, "sendMessage")
    url = f"https://api.telegram.org/bot{bot_token}/{method}"

    payload = {
        "chat_id": chat_id,
        "ephemeral": True,
        "ephemeral_user_id": ephemeral_user_id,
        "ephemeral_expiration_date": int(time.time()) + expiration_seconds
    }

    if media_type in ("photo", "video", "animation", "audio", "document", "voice", "video_note"):
        payload[media_type if media_type != "video_note" else "video_note"] = media
        if caption:
            payload["caption"] = caption
            payload["parse_mode"] = parse_mode
    elif media_type == "sticker":
        payload["sticker"] = media
    elif media_type == "contact":
        # media should be dict with phone_number, first_name, etc.
        payload.update(media)
    elif media_type == "location":
        payload.update(media)  # latitude, longitude
    elif media_type == "venue":
        payload.update(media)  # latitude, longitude, title, address
    elif media_type == "poll":
        payload.update(media)  # question, options, etc.

    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def edit_ephemeral_text(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    text: str,
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """Edit ephemeral message text."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id,
        "text": text,
        "parse_mode": parse_mode
    }
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def edit_ephemeral_media(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    media: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """Edit ephemeral message media."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageMedia"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id,
        "media": media
    }
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def edit_ephemeral_caption(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    caption: str,
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """Edit ephemeral message caption."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageCaption"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id,
        "caption": caption,
        "parse_mode": parse_mode
    }
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def edit_ephemeral_reply_markup(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    reply_markup: Dict[str, Any]
) -> Dict[str, Any]:
    """Edit ephemeral message inline keyboard."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/editEphemeralMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id,
        "reply_markup": reply_markup
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def delete_ephemeral(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int
) -> Dict[str, Any]:
    """Delete ephemeral message before expiration."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/deleteEphemeralMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "ephemeral_user_id": ephemeral_user_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def reply_to_ephemeral(
    bot_token: str,
    chat_id: int,
    message_id: int,
    ephemeral_user_id: int,
    text: str,
    parse_mode: str = "MarkdownV2",
    **kwargs
) -> Dict[str, Any]:
    """Reply to an ephemeral message (reply is also ephemeral to same user)."""
    import aiohttp

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "reply_parameters": {
            "message_id": message_id,
            "chat_id": chat_id,
            "ephemeral_user_id": ephemeral_user_id
        }
    }
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


def is_ephemeral_message(message: Dict[str, Any]) -> bool:
    """Check if a Message object is ephemeral."""
    return message.get("is_ephemeral", False)


def get_ephemeral_user_id(message: Dict[str, Any]) -> Optional[int]:
    """Get the user ID who can see the ephemeral message."""
    return message.get("ephemeral_user_id")


def get_ephemeral_expiration(message: Dict[str, Any]) -> Optional[int]:
    """Get expiration timestamp of ephemeral message."""
    return message.get("ephemeral_expiration_date")


def get_ephemeral_chat_id(message: Dict[str, Any]) -> Optional[int]:
    """Get original chat ID where ephemeral message was sent."""
    return message.get("ephemeral_chat_id")


# ============================================================
# Rich Messages v2 Helpers (10.2)
# ============================================================

async def rich_message_with_media(
    bot_token: str,
    chat_id: int,
    blocks: List[Dict],
    media_type: str,  # "photo", "video", "animation", "audio", "voice_note"
    media_file_id: str,
    caption: List[Dict] = None,
    credit: List[Dict] = None,
    message_thread_id: int = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send rich message with embedded media (Bot API 10.2+).

    Args:
        bot_token: Bot token
        chat_id: Target chat
        blocks: List of RichBlock dicts
        media_type: "photo", "video", "animation", "audio", "voice_note"
        media_file_id: file_id, HTTP URL, or attach://<name>
        caption: Rich caption as RichText[] (optional)
        credit: Attribution as RichText[] (optional)
        message_thread_id: Forum topic ID (optional)
        **kwargs: Additional parameters

    Returns:
        API response
    """
    import aiohttp

    media = {"type": media_type, "media": media_file_id}
    if caption:
        media["caption"] = {"type": "caption", "content": caption}
    if credit:
        media["credit"] = {"type": "caption", "content": credit}

    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": {
            "blocks": blocks,
            "media": media
        }
    }
    if message_thread_id:
        payload["message_thread_id"] = message_thread_id
    payload.update(kwargs)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


async def send_voice_note_rich(
    bot_token: str,
    chat_id: int,
    voice_file_id: str,
    blocks: List[Dict] = None,
    caption: List[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """Send voice note with optional rich blocks (10.2+)."""
    media = {
        "type": "voice_note",
        "media": voice_file_id
    }
    if caption:
        media["caption"] = {"type": "caption", "content": caption}

    url = f"https://api.telegram.org/bot{bot_token}/sendRichMessage"
    payload = {
        "chat_id": chat_id,
        "rich_message": {
            "blocks": blocks or [],
            "media": media
        }
    }
    payload.update(kwargs)

    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()


def input_media_voice_note(file_id: str, duration: int = None, caption: str = None, parse_mode: str = None) -> Dict:
    """Create InputMediaVoiceNote for sendMediaGroup or editMessageMedia."""
    media = {"type": "voice_note", "media": file_id}
    if duration:
        media["duration"] = duration
    if caption:
        media["caption"] = caption
        if parse_mode:
            media["parse_mode"] = parse_mode
    return media


def input_rich_block_list_item(prefix: List[Dict], content: List[Dict]) -> Dict:
    """Create InputRichBlockListItem (10.2+)."""
    return {
        "type": "list_item",
        "prefix": prefix,
        "content": content
    }


def input_rich_block_list(items: List[Dict], ordered: bool = False, numeral: str = "1") -> Dict:
    """Create InputRichBlockList."""
    return {
        "type": "list",
        "items": items,
        "ordered": ordered,
        "numeral": numeral  # "1", "a", "A", "i", "I", "bullet", "task"
    }


# ============================================================
# Communities Helpers (Read-Only in 10.2)
# ============================================================

def detect_community(chat_full_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Detect if chat belongs to a Community.

    Args:
        chat_full_info: ChatFullInfo object from getChat

    Returns:
        Community dict if present, None otherwise
    """
    return chat_full_info.get("community")


def get_community_info(chat_full_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract community info from ChatFullInfo."""
    community = chat_full_info.get("community")
    if not community:
        return {"has_community": False}

    return {
        "has_community": True,
        "community_id": community.get("id"),
        "community_title": community.get("title"),
        "chat_id": chat_full_info.get("id"),
        "chat_title": chat_full_info.get("title")
    }


def is_community_service_message(message: Dict[str, Any]) -> bool:
    """Check if message is CommunityChatAdded or CommunityChatRemoved."""
    return "community_chat_added" in message or "community_chat_removed" in message


def get_community_chat_added(message: Dict[str, Any]) -> Optional[Dict]:
    """Extract CommunityChatAdded data."""
    return message.get("community_chat_added")


def get_community_chat_removed(message: Dict[str, Any]) -> Optional[Dict]:
    """Extract CommunityChatRemoved data."""
    return message.get("community_chat_removed")


# ============================================================
# Mini App Security Helpers
# ============================================================

MINI_APP_METHODS = {
    "openLink", "openTelegramLink", "requestWriteAccess", "requestContact",
    "showPopup", "showScanQrPopup", "close", "expand", "collapse",
    "enableVerticalSwipes", "disableVerticalSwipes",
    "setHeaderColor", "setBackgroundColor",
    "onThemeChanged", "onViewportChanged", "onSafeAreaChanged",
    "addToHomeScreen", "checkVersion", "setSafeAreaInsets"
}

def is_mini_app_method(method_name: str) -> bool:
    """Check if a method is a Mini App method (blocked from external origins)."""
    return method_name in MINI_APP_METHODS


def check_mini_app_origin_security(origin: str, mini_app_url: str) -> Dict[str, Any]:
    """
    Check if external origin will be blocked from Mini App methods.

    Returns dict with security assessment.
    """
    from urllib.parse import urlparse

    origin_domain = urlparse(origin).netloc
    app_domain = urlparse(mini_app_url).netloc

    same_origin = origin_domain == app_domain
    subdomain_match = origin_domain.endswith("." + app_domain) or app_domain.endswith("." + origin_domain)

    return {
        "origin": origin,
        "mini_app_domain": app_domain,
        "same_origin": same_origin,
        "subdomain_match": subdomain_match,
        "will_be_blocked": not (same_origin or subdomain_match),
        "effective_date": "2026-07-20",
        "opt_out_available": True,
        "opt_out_via": "@BotFather → Mini Apps → Security Settings"
    }


# ============================================================
# Bot Command — Ephemeral Field
# ============================================================

def bot_command_ephemeral(command: str, description: str, ephemeral: bool = True) -> Dict:
    """Create BotCommand with ephemeral flag."""
    return {
        "command": command,
        "description": description,
        "ephemeral": ephemeral
    }


def set_bot_commands_with_ephemeral(bot_token: str, commands: List[Dict]) -> Dict[str, Any]:
    """Set bot commands including ephemeral ones."""
    import aiohttp

    async def _send():
        url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"commands": commands}) as resp:
                return await resp.json()

    return _send()


# ============================================================
# ReplyParameters — Ephemeral Support
# ============================================================

def reply_parameters_ephemeral(
    message_id: int,
    chat_id: int,
    ephemeral_user_id: int,
    **kwargs
) -> Dict:
    """Create ReplyParameters for ephemeral message."""
    params = {
        "message_id": message_id,
        "chat_id": chat_id,
        "ephemeral_user_id": ephemeral_user_id
    }
    params.update(kwargs)
    return params


# ============================================================
# Validation & Utilities
# ============================================================

def validate_ephemeral_params(
    chat_id: int,
    ephemeral_user_id: int,
    expiration_seconds: int = None
) -> tuple[bool, List[str]]:
    """Validate ephemeral message parameters."""
    errors = []

    if chat_id > 0:
        errors.append("Ephemeral messages only work in groups/supergroups (chat_id must be negative)")

    if ephemeral_user_id <= 0:
        errors.append("ephemeral_user_id must be positive")

    if expiration_seconds is not None:
        if expiration_seconds < 60:
            errors.append("Expiration must be at least 60 seconds")
        if expiration_seconds > 2592000:  # 30 days
            errors.append("Expiration cannot exceed 30 days (2592000 seconds)")

    return len(errors) == 0, errors


# ============================================================
# Example Usage
# ============================================================

async def example_ephemeral_welcome():
    """Example: Ephemeral welcome message in group."""
    # When new user joins, send private welcome
    # await send_ephemeral(
    #     token, group_chat_id,
    #     "Welcome to the group! Here's your personal guide...",
    #     new_user_id
    # )
    pass


async def example_rich_with_chart():
    """Example: Rich message with embedded chart photo."""
    blocks = [
        {"type": "section_heading", "level": 1, "content": [{"type": "plain", "text": "Q3 Report"}]},
        {"type": "paragraph", "content": [{"type": "plain", "text": "Revenue chart below:"}]},
    ]
    # await rich_message_with_media(
    #     token, chat_id, blocks, "photo", chart_file_id
    # )
    pass


if __name__ == "__main__":
    # Demo validation
    valid, errors = validate_ephemeral_params(-1001234567890, 123456789, 86400)
    print(f"Valid: {valid}, Errors: {errors}")

    # Demo community detection
    chat_info = {
        "id": -100111,
        "title": "General Chat",
        "community": {"id": "comm_123", "title": "Tech Community"}
    }
    print(f"Community: {get_community_info(chat_info)}")

    # Demo Mini App check
    print(f"External link check: {check_mini_app_origin_security('https://evil.com', 'https://myapp.example.com')}")