---
name: herouserbot-module-dev
description: "Author Hero Userbot modules: inline buttons, strings (EN+RU), callback handlers, InlineCall patterns, DB usage, loader.command, style colors, and input buttons."
version: 1.0.0
author: i-execute
license: MIT
---

Skill for authoring modules for Heroku userbot. Based on reverse-engineering patterns from @I_execute's production modules: XRay (2,467 lines), Buttons (625 lines), Info (572 lines), and others at [github.com/i-execute/Modules](https://github.com/i-execute/Modules).

## Module Skeleton

```python
__version__ = (1, 0, 0)
# meta developer: @your_username
# meta banner: https://link-to-banner.jpeg   # optional

import os
import asyncio
import logging
from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

@loader.tds
class MyModule(loader.Module):
    """Short docstring — appears in .help"""

    strings = {
        "name": "MyModule",
        # ... EN strings
    }

    strings_ru = {
        # ... RU strings — mirror of strings
    }

    def __init__(self):
        self._db = None
        self._client = None

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        # load state from db

    async def on_unload(self):
        # cleanup: cancel tasks, stop processes
        pass

    @loader.command()
    async def mycmd(self, message):
        """Command docstring"""
        await self.inline.form(
            text=self.strings["some_key"].format(...),
            message=message,
            reply_markup=[...],
            silent=True,
        )
```

## Strings Convention

- **`strings`** — English dictionary. **`strings_ru`** — Russian dictionary (mirror keys).
- Use `<b>`, `<code>`, `<blockquote>`, `<u>` — HTML, not Markdown.
- **`\n`** inside strings for newlines. NEVER use triple-quoted strings inside the dict — they mess with formatting.
- Use `.format(**kwargs)` for substitutions. The `**kwargs` trick lets you have keys that are Python reserved words (e.g., `pass`):
  ```python
  self.strings["socks5_sent"].format(
      name=_escape(name),
      ip=ip,
      port=port,
      user=_escape(user),
      **{"pass": _escape(pass_)},
  )
  ```
- String keys naming convention: `snake_case` describing what the string IS (not where it's used).
- Common key patterns:
  - `"name"` — module display name
  - `"main_menu"`, `"setup_menu"`, `"users_menu"` — menu screens
  - `"user_menu"`, `"user_settings"` — entity detail screens
  - `"add_user_name"`, `"add_user_transport"` — wizard steps
  - `"btn_start"`, `"btn_stop"`, `"btn_back"`, `"btn_close"` — button labels
  - `"input_name"`, `"input_limit"`, `"input_sni"` — input prompts
  - `"err_name_exists"`, `"err_invalid_name"` — validation errors
  - `"user_started"`, `"user_stopped"`, `"user_deleted"` — action confirmations
  - `"loading"` — shown while async operation runs
  - `"status_online"`, `"status_offline"` — status labels

## Response and UI Style

When the user requests it, module source, strings, captions, and final delivery text must not contain comments, emoji, or em dashes. Keep status messages compact and use clean HTML formatting.

## Inline Form Basics

The primary UI pattern: `self.inline.form()` sends an inline message with buttons.

```python
await self.inline.form(
    text="<b>Title</b>\n<blockquote>content...</blockquote>",
    message=message,          # the original user message
    reply_markup=[...],       # list of button rows
    silent=True,              # suppress notification
)
```

Additional kwargs for media:
```python
await self.inline.form(
    text=...,
    message=message,
    reply_markup=[...],
    photo="https://...",      # or: video=, gif=
    silent=True,
)
```

## Inline Buttons — reply_markup Structure

`reply_markup` is a `list[list[dict]]` — outer list = rows, inner list = buttons.

### Standard callback button:
```python
{
    "text": self.strings["btn_start"],        # display text
    "callback": self._cb_start_user,           # async method
    "args": (name,),                           # tuple of extra args
    "style": "primary",                        # optional color
}
```

### Button with **input** (text field that opens when clicked):
```python
{
    "text": self.strings["btn_set_sni"],
    "input": self.strings["input_sni"],        # placeholder/prompt text
    "handler": self._cb_set_sni,               # async handler called with user input
    "args": (name,),                           # extra args (passed AFTER the input value)
    "style": "primary",
}
```

**Critical**: When using input buttons, the handler signature is:
```python
async def _cb_set_sni(self, call: InlineCall, sni: str, name: str):
    # sni = user's input text
    # name = from args tuple
```

The input value is inserted as the **first** argument after `call`, BEFORE the `args` tuple elements.

### Button styles (colors):
| Style | Meaning |
|-------|---------|
| `"primary"` | Default blue (most common) |
| `"danger"` | Red (delete, stop, close) |
| `"success"` | Green (toggle on, active state) |

From XRay.py analysis:
- `primary` is used for most action buttons
- `danger` is used for: Close, Stop, Delete User, Revoke Token
- `success` is used for: Autostart toggle (On state)
- When toggling state (autostart on/off), use `success` for ON, `danger` for OFF

Example of a conditional style toggle:
```python
{
    "text": self.strings["btn_autostart_on"] if autostart else self.strings["btn_autostart_off"],
    "callback": self._cb_toggle_autostart,
    "args": (name,),
    "style": "success" if autostart else "danger",
},
```

### Button with `style="danger"`:
```python
{"text": self.strings["btn_close"], "callback": self._cb_close, "style": "danger"},
```

## InlineCall API

Every callback receives `call: InlineCall`.

### Essential methods:
```python
await call.edit(text, reply_markup=markup)     # edit the inline message
await call.answer("Alert text", show_alert=True)  # show popup alert
await call.delete()                             # delete the inline message
```

### call.edit() with empty markup (loading screen):
```python
await call.edit(
    self.strings["xray_installing"].format(version=tag),
    reply_markup=[]     # removes all buttons
)
```

### Accessing chat from call:
```python
call.form["chat"]  # the chat where inline message is shown
```

## Callback Method Patterns

### Simple navigation (no args):
```python
async def _cb_main_menu(self, call: InlineCall):
    await call.edit(text, reply_markup=markup)

async def _cb_close(self, call: InlineCall):
    await call.delete()
```

### Navigation with string args:
```python
async def _cb_user_menu(self, call: InlineCall, name: str):
    await call.edit(self.strings["loading"])
    # ... fetch data ...
    await call.edit(text, reply_markup=markup)
```

### Action with result screen:
```python
async def _cb_start_user(self, call: InlineCall, name: str):
    await call.edit(self.strings["loading"])
    ok, err = await self._start_user(name)
    if ok:
        text = self.strings["user_started"].format(name=_escape(name))
    else:
        text = self.strings["setup_fail"].format(error=_escape(err[:200]))
    await call.edit(
        text,
        reply_markup=[[{
            "text": self.strings["btn_back"],
            "callback": self._cb_user_menu,
            "args": (name,),
            "style": "primary",
        }]]
    )
```

### Input handler (called with user text inserted before args):
```python
# Button definition:
{"text": "Set SNI", "input": "Enter SNI:", "handler": self._cb_set_sni, "args": (name,)}

# Handler receives: call, user_input, *args
async def _cb_set_sni(self, call: InlineCall, sni: str, name: str):
    user = self._users.get(name)
    user["sni"] = sni.strip().lower()
    self._save_users()
    await call.edit(
        self.strings["sni_set"].format(sni=_escape(sni)),
        reply_markup=[[{"text": self.strings["btn_back"], ...}]]
    )
```

### Wizard pattern (multi-step creation):
```
_cb_add_user_name → shows input button
_cb_add_user_transport_choice → shows transport buttons
_cb_add_user_limit_input → shows input button
_cb_create_user_final → creates entity, shows result
```

Each step stores intermediate state implicitly via the `args` tuple passed forward.

## State Persistence — DB API

```python
# client_ready gives you (client, db)
self._db = db

# Save
self._db.set("Namespace", "key", value)   # value can be dict, list, str, int

# Load
value = self._db.get("Namespace", "key", default_value)
```

Namespace is typically the module abbreviation (e.g., `"XR"` for XRay, `"InlineButtons"` for Buttons).

**Always save after mutation:**
```python
def _save_users(self):
    self._db.set("XR", "users", self._users)
```

## HTML Escaping

Always escape user-provided strings before inserting into HTML:

```python
def _escape(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
```

Use `_escape()` on every user-controlled value in `.format()` calls.

## Markdown Stripping

When accepting user input that may contain Markdown links:

```python
def _strip_md(text: str) -> str:
    import re
    return re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'', text).strip()
```

Apply before saving user input.

## @loader.command Decorator

```python
@loader.command(
    ru_doc="Описание команды на русском",
    en_doc="Command description in English",
)
async def xr(self, message):
    """XRay multi-user VPN manager"""
    await self.inline.form(
        text=...,
        message=message,
        reply_markup=[...],
        silent=True,
    )
```

## Loading Pattern

Always show `"loading"` before any async operation that takes >0.2s:

```python
async def _cb_user_menu(self, call: InlineCall, name: str):
    await call.edit(self.strings["loading"])
    # ... async work ...
    await call.edit(text, reply_markup=markup)
```

## File Sending from Inline Context

Use `self._client.send_file()` with `call.form["chat"]`:

```python
tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
tmp.write(content)
tmp.close()
try:
    await self._client.send_file(
        call.form["chat"],
        tmp.name,
        force_document=True,
        file_name=f"link_for_{name}.txt",
    )
finally:
    os.unlink(tmp.name)
```

## Module Lifecycle

```python
def __init__(self):
    # set defaults BEFORE client_ready
    self._users = {}
    self._processes = {}
    self._monitor_task = None

async def client_ready(self, client, db):
    # One-time setup: load state, detect things, start watchers
    self._client = client
    self._db = db
    self._users = self._db.get("NS", "users", {})
    self._start_monitor()

async def on_unload(self):
    # Cleanup: cancel tasks, stop subprocesses
    if self._monitor_task:
        self._monitor_task.cancel()
    for name in list(self._processes.keys()):
        await self._stop_user(name)
```

## Pitfalls

1. **No Markdown** — Heroku inline uses HTML tags only (`<b>`, `<code>`, `<blockquote>`, `<u>`). Never use `**` or `*` or backticks.

2. **`\n` vs triple-quotes** — Always use `\n` inside single-quoted strings. Triple-quoted strings inside the `strings` dict cause formatting issues.

3. **InlineCall has no `.answer()` with markup** — `call.edit()` for updates, `call.answer()` only for simple alert popups.

4. **`**kwargs` trick for reserved words** — When `.format()` needs a key that's a Python keyword (`pass`, `class`, etc.), use `**{"pass": value}` unpacking.

5. **Input button handler signature** — The user's input text is inserted as the FIRST arg after `call`, BEFORE items from `args` tuple. NEVER forget this — it's the #1 bug source.

6. **Always escape user input** — Call `_escape(name)` on every user-provided value before inserting into HTML strings. XSS via `<script>` is blocked by Telegram, but `<` and `>` can break formatting.

7. **Empty reply_markup removes buttons** — Use `reply_markup=[]` during loading screens.

8. **DB namespace collisions** — Use unique short prefixes (`"XR"`, `"IB"`, `"IF"`), not generic names.

9. **`silent=True`** — Always pass `silent=True` to `inline.form()` to avoid double-notifications.

10. **Process lifecycle** — For modules spawning subprocesses, kill them in `on_unload()`, reattach in `client_ready()`.

## Reference Modules

- **XRay.py** (2,467 lines) — Complex: multi-screen inline UI, DB persistence, subprocess management, GitHub OAuth device flow, input buttons with handler+args pattern, conditional button styles
- **Buttons.py** (625 lines) — Medium: wizard-style inline button constructor, DB-backed config, media attachment
- **Info.py** (572 lines) — Medium: user/chat info display, premium-aware strings (two variants per key), avatar download, x0.at upload
- **Repo**: https://github.com/i-execute/Modules — all modules follow these patterns

## Quick Checklist for New Modules

- [ ] `__version__` + `# meta developer:` header
- [ ] `@loader.tds` decorator on class
- [ ] `strings` dict (EN) + `strings_ru` dict (RU) — identical keys
- [ ] `def __init__(self)` with state defaults
- [ ] `async def client_ready(self, client, db)` — load state, setup
- [ ] `async def on_unload(self)` — cleanup
- [ ] At least one `@loader.command()` entry point → `self.inline.form()`
- [ ] All user input HTML-escaped with `_escape()`
- [ ] `"loading"` string shown before async operations
- [ ] `silent=True` on all `inline.form()` calls
- [ ] Button styles: `primary` (default), `danger` (delete/stop), `success` (on/active)
- [ ] Input buttons: `"input"` for prompt, `"handler"` for callback, input value inserted BEFORE `args`
- [ ] Back-navigation: every screen has a `"btn_back"` button to parent menu
- [ ] Close button: top-level menu has `"btn_close"` → `call.delete()`

## Cloudflared WebSocket VLESS

When adding WebSocket VLESS behind Cloudflare Tunnel, distinguish a locally verified WS proxy from a fully externally verified Cloudflare route. A static site server alone cannot proxy WebSocket upgrades to Xray. The reverse proxy must forward WebSocket binary frames, text frames, ping/pong, and closure in both directions. Install cloudflared into the module-owned user directory, expose installation/reinstallation in Setup, and run the exact installed binary rather than relying on PATH. Lifecycle handling must stop the Xray inbound, tunnel, and local proxy together, and reattach or restart all required components after module reload. Follow `references/cloudflared-websocket-vless.md` for the architecture, lifecycle, client-link fields, and mandatory local plus external E2E checks.

## Forum Topic Logging

For module audit logs, obtain the asset forum channel from `heroku.forums/channel_id`, create or reuse a topic through `utils.asset_forum_topic`, and use the requested topic icon. Send messages through `self.inline.bot.send_message` with `parse_mode="HTML"` and `message_thread_id=topic.id`; do not send these logs through the user client. Log process starts, stops, deletions, and enforcement actions. When a device limit is exceeded, persist `autostart=False` before stopping the process, then record the exact limit and observed active-device count.

## Xray / VLESS Transport Validation

For Hero modules that create Xray users, configs, or VLESS links, static JSON validation is not enough. A listener can accept TCP and a REALITY TLS handshake can complete while VLESS/XHTTP traffic is reset immediately. Before delivering a claimed transport fix, perform an isolated server + SOCKS-client E2E probe and require a successful proxied HTTP request. See `references/xray-reality-xhttp-validation.md` for the reproducible procedure, compatibility finding, and configuration/link rules.

When a user explicitly asks to fix a module and send the file, do not send an unverified speculative patch. Verify the transport behavior first, then provide the artifact with concise factual results.

## Critical Workflow Rule

**When user sends files and says "rewrite/переделай based on these — write from scratch using the skill":**

1. Load the skill (already in context — just follow it).
2. **IMMEDIATELY start writing the output file** via `write_file` tool call in the SAME turn as any analysis. NEVER do analysis-only turns — batch the analysis tool calls WITH the first write_file call.
3. If the module is large, write the whole thing in one pass — don't chunk it across turns.
4. After writing, validate with a quick syntax check (`python3 -c "import ast; ast.parse(open('...').read())"`) in the SAME turn.
5. Report "Done. File at: PATH" — nothing more. No explanations, no summaries.
6. User expects the FILE to exist on disk, not a description of what would be written.
7. Zip archives: extract (`python3 -c "import zipfile; ..."`), read key source files, then write — all tool calls batched per turn, no pauses.