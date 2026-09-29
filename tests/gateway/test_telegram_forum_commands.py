"""Tests for lazy forum command registration in TelegramAdapter."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gateway.config import Platform, PlatformConfig


def _make_test_adapter():
    """Build a TelegramAdapter without running __init__."""
    from plugins.platforms.telegram.adapter import TelegramAdapter

    adapter = object.__new__(TelegramAdapter)
    adapter.platform = Platform.TELEGRAM
    adapter.config = PlatformConfig(enabled=True, token="***", extra={})
    # ``name`` is a property derived from platform.value.title()
    adapter._app = SimpleNamespace(mt_req=AsyncMock(return_value={"result": {"_": "bool", "boolean": True}}))
    adapter._bot = MagicMock()
    adapter._forum_command_registered = set()
    adapter._forum_lock = asyncio.Lock()
    return adapter


def _forum_message(chat_id=-100, is_forum=True):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id, is_forum=is_forum),
    )


@pytest.mark.asyncio
async def test_ensure_forum_commands_skips_non_forum():
    adapter = _make_test_adapter()
    msg = _forum_message(is_forum=False)
    await adapter._ensure_forum_commands(msg)
    adapter._app.mt_req.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_forum_commands_skips_already_registered():
    adapter = _make_test_adapter()
    adapter._forum_command_registered.add(-100)
    msg = _forum_message(is_forum=True)
    await adapter._ensure_forum_commands(msg)
    adapter._app.mt_req.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_forum_commands_registers_once():
    adapter = _make_test_adapter()
    msg = _forum_message(chat_id=-123, is_forum=True)

    with patch("hermes_cli.commands.telegram_menu_commands") as mock_menu:
        mock_menu.return_value = ([("new", "Start new session"), ("help", "Show help")], 0)
        await adapter._ensure_forum_commands(msg)

    assert -123 in adapter._forum_command_registered
    adapter._app.mt_req.assert_awaited_once()
    args, kwargs = adapter._app.mt_req.call_args
    assert args[0] == "bots.setBotCommands"
    assert len(kwargs["commands"]) == 2  # two botCommand dicts
    assert kwargs["commands"][0] == {"_": "botCommand", "command": "new", "description": "Start new session"}
    assert kwargs["scope"] == {"_": "botCommandScopePeer", "peer": -123}


@pytest.mark.asyncio
async def test_ensure_forum_commands_handles_set_failure():
    adapter = _make_test_adapter()
    msg = _forum_message(chat_id=-456, is_forum=True)
    adapter._app.mt_req.side_effect = Exception("Telegram API error")

    with patch("hermes_cli.commands.telegram_menu_commands") as mock_menu:
        mock_menu.return_value = ([("new", "Start new session")], 0)
        # Should NOT raise despite the API error
        await adapter._ensure_forum_commands(msg)

    # On failure we don't retry for this chat, so it's added to the set
    # to avoid hammering a broken chat.
    assert -456 not in adapter._forum_command_registered


@pytest.mark.asyncio
async def test_ensure_forum_commands_race_safety():
    """Two concurrent coroutines must not double-register the same chat."""
    adapter = _make_test_adapter()
    msg = _forum_message(chat_id=-789, is_forum=True)

    with patch("hermes_cli.commands.telegram_menu_commands") as mock_menu:
        mock_menu.return_value = ([("new", "Start new session")], 0)
        coro1 = adapter._ensure_forum_commands(msg)
        coro2 = adapter._ensure_forum_commands(msg)
        await asyncio.gather(coro1, coro2)

    # The lock should make this exactly 1 call, not 2.
    assert adapter._app.mt_req.await_count == 1
