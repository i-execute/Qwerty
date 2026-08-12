# Telegram DM Topic Handling & Thread Isolation

## How the Adapter Sees Topics/Threads

### Incoming Message Processing

When a message arrives in a Telegram DM with topics enabled:

```python
# adapter.py lines 937-954
thread_id_raw = getattr(message, "message_thread_id", None)
is_topic_message = bool(getattr(message, "is_topic_message", False))

if chat_type == "dm" and is_topic_message:
    thread_id = str(thread_id_raw)  # e.g., "211916"
```

The `thread_id` becomes part of the `MessageEvent.source.thread_id` and flows through the entire pipeline.

## Session Isolation: `thread_sessions_per_user`

### Default Behavior (No Isolation)

In `config.yaml`, the default is:
```yaml
platforms:
  telegram:
    extra:
      thread_sessions_per_user: false  # DEFAULT
      group_sessions_per_user: true
```

**Result:** All topics in the same DM chat share **one Hermes session**. Context, memory, and history are shared across all threads.

### Enabling Per-Topic Isolation

```yaml
platforms:
  telegram:
    extra:
      thread_sessions_per_user: true   # ENABLE ISOLATION
```

**Result:** Each topic gets its own Hermes session with independent context, memory, and conversation history.

### Session Key Construction

In `_text_batch_key()` (adapter.py:8147):
```python
build_session_key(
    event.source,
    group_sessions_per_user=True,
    thread_sessions_per_user=self.config.extra.get("thread_sessions_per_user", False),
    profile=event.source.profile,
)
```

The `thread_sessions_per_user` flag controls whether `thread_id` is included in the session key.

## Rich Message Routing in Topics

### Draft Streaming (`sendRichMessageDraft`)

```python
# _try_send_rich_draft() - adapter.py:1926-1933
payload: Dict[str, Any] = {
    "chat_id": normalize_telegram_chat_id(chat_id),
    "draft_id": int(draft_id),
    "rich_message": self._rich_message_payload(content),
}
thread_id = self._metadata_thread_id(metadata)
if thread_id is not None:
    payload["message_thread_id"] = int(thread_id)
```

### Final Message (`editMessageText` with `rich_message`)

```python
# _try_edit_rich() - adapter.py:1832-1835
payload: Dict[str, Any] = {
    "chat_id": normalize_telegram_chat_id(chat_id),
    "message_id": int(message_id),
    "rich_message": self._rich_message_payload(content),
}
thread_id = self._metadata_thread_id(metadata)
thread_kwargs = self._thread_kwargs_for_send(...)
payload.update({k: v for k, v in thread_kwargs.items() if v is not None})
```

### Thread Kwargs for Topics

```python
# _thread_kwargs_for_send() - adapter.py:1107-1149
# For DM topics with telegram_dm_topic_reply_fallback:
if metadata and metadata.get("telegram_dm_topic_reply_fallback"):
    if reply_to_mode == "off":
        return {"message_thread_id": cls._message_thread_id_for_send(thread_id)}
    # ... reply anchor logic ...
    return {"message_thread_id": cls._message_thread_id_for_send(thread_id)}

# For direct_messages_topic_id (Bot API native DM topics):
direct_topic_id = cls._metadata_direct_messages_topic_id(metadata)
if direct_topic_id is not None:
    return {
        "message_thread_id": None,
        "direct_messages_topic_id": int(direct_topic_id),
    }

# Forum topics (supergroups):
return {"message_thread_id": cls._message_thread_id_for_send(thread_id)}
```

## Configuration Reference

| Config Key | Default | Description |
|------------|---------|-------------|
| `platforms.telegram.extra.thread_sessions_per_user` | `false` | Isolate Hermes sessions per DM topic |
| `platforms.telegram.extra.group_sessions_per_user` | `true` | Isolate sessions per group/forum topic |
| `platforms.telegram.extra.rich_messages` | `true` | Enable Rich Messages (sendRichMessage) |
| `platforms.telegram.extra.rich_drafts` | `true` | Enable Rich Drafts (sendRichMessageDraft) |

## Practical Implications

### For User with chat_id=7610246474, thread_id=211916

**Current (thread_sessions_per_user=false):**
- All topics in this DM share one session
- Context persists across topic switches
- Rich Messages work in all topics

**With thread_sessions_per_user=true:**
- Topic "211916" gets isolated session
- Switching topics = fresh context
- Rich Messages still work (independent of session isolation)

## Testing Checklist

- [ ] Send message to DM topic → verify `thread_id` in logs
- [ ] Enable `thread_sessions_per_user: true` → verify new session per topic
- [ ] Verify Rich Messages render in topic (tables, code, details, thinking)
- [ ] Verify streaming draft animates in topic
- [ ] Verify final editMessageText replaces draft in topic