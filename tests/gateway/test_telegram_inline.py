import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from gateway.config import PlatformConfig
from gateway.platforms.base import SendResult
from plugins.platforms.telegram.adapter import TelegramAdapter, _inline_msg_id


def _adapter() -> TelegramAdapter:
    adapter = object.__new__(TelegramAdapter)
    adapter.config = PlatformConfig(enabled=True)
    adapter._bot = SimpleNamespace(
        do_api_request=AsyncMock(),
        edit_message_text=AsyncMock(),
    )
    adapter._inline_edits = {}
    adapter._message_handler = AsyncMock()
    adapter._active_sessions = {}
    adapter._pending_messages = {}
    adapter._session_tasks = {}
    adapter._background_tasks = set()
    adapter._expected_cancelled_tasks = set()
    adapter._topic_recovery_hook = None
    return adapter


def test_inline_send_edits_target_without_dm_send():
    adapter = _adapter()
    token = _inline_msg_id.set("inline-42")
    try:
        result = asyncio.run(adapter.send("123", "answer"))
    finally:
        _inline_msg_id.reset(token)

    assert result == SendResult(success=True, message_id="inline-42")
    adapter._bot.do_api_request.assert_awaited_once()
    method, = adapter._bot.do_api_request.await_args.args
    assert method == "editMessageText"
    assert adapter._bot.do_api_request.await_args.kwargs["api_kwargs"]["inline_message_id"] == "inline-42"


def test_plain_send_does_not_use_inline_edit():
    adapter = _adapter()
    adapter._send_path_degraded = True

    result = asyncio.run(adapter.send("123", "answer"))

    assert result.success is False
    adapter._bot.do_api_request.assert_not_awaited()


def test_inline_auth_uses_adapter_allowlist():
    adapter = _adapter()
    adapter.config.extra["allow_from"] = ["123"]

    assert adapter._is_callback_user_authorized("123") is True
    assert adapter._is_callback_user_authorized("456") is False
