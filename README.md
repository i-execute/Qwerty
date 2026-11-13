<p align="center">
  <a href="https://t.me/I_execute"><img src="https://img.shields.io/badge/Telegram-@I__execute-26A5E4?style=flat&logo=telegram&logoColor=white" alt="Telegram" /></a>
  <a href="https://github.com/i-execute/Qwerty/commits/forget"><img src="https://img.shields.io/badge/Branch-forget-8A2BE2?style=flat&logo=git&logoColor=white" alt="Branch" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License: MIT" /></a>
</p>

# Qwerty Agent

Fork of [NousResearch/qwerty-agent](https://github.com/NousResearch/qwerty-agent) (ex-Hermes Agent), maintained by [@I_execute](https://t.me/I_execute).

A personal AI agent that runs on your own machine: terminal CLI, TUI, and a messaging gateway (Telegram, Discord, Slack, WhatsApp, Signal and ~20 more) — one core, one config. Persistent memory, self-written skills, cron jobs, subagent delegation, real terminal and browser control. Any OpenAI-compatible provider.

## Install

Linux / macOS / WSL2 / Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/i-execute/Qwerty/forget/install.sh | bash
```

What it does: installs uv + Python 3.11 + Node.js + ripgrep + ffmpeg, clones this repo to `~/.qwerty/qwerty-agent`, creates a venv inside it, wires the `qwerty` command into `~/.local/bin`, runs the setup wizard (API keys, provider, gateway).

Windows (PowerShell):

```powershell
iex (irm https://raw.githubusercontent.com/i-execute/Qwerty/forget/scripts/install.ps1)
```

After install:

```bash
source ~/.bashrc   # or ~/.zshrc
qwerty             # start chatting
```

Install as root on a VPS: layout is FHS — code in `/usr/local/lib/qwerty-agent`, command in `/usr/local/bin/qwerty`, data still in `~/.qwerty`.

## Commands

```bash
qwerty              # interactive CLI
qwerty model        # pick provider/model
qwerty tools        # toggle tools
qwerty gateway setup / start   # messaging gateway
qwerty setup        # full wizard
qwerty update       # update to latest branch HEAD
qwerty doctor       # diagnostics
```

Slash commands work in both CLI and chat: `/new` `/model` `/skills` `/retry` `/undo` `/compress` `/usage` `/stop`.

## Data layout

| Path | What |
|---|---|
| `~/.qwerty/qwerty-agent/` | repo + venv (managed install) |
| `~/.qwerty/` | config.yaml, state.db, sessions, skills, memories, logs |
| `~/.qwerty/skills/` | skills (synced from repo on install/update) |

## Backup / restore

Chats and sessions live in `~/.qwerty/state.db`:

```bash
sqlite3 ~/.qwerty/state.db .dump | gzip > backup.sql.gz
gunzip -c backup.sql.gz | sqlite3 ~/.qwerty/state.db
```

## Update

```bash
qwerty update
```

or, from the checkout:

```bash
cd ~/.qwerty/qwerty-agent && git pull && venv/bin/pip install -e . --no-deps
```

## License

MIT — see [LICENSE](LICENSE).
