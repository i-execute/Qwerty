# Qwerty CLI Reference

Live sources when anything looks stale: `qwerty --help`, `qwerty <command> --help`,
https://qwerty-agent.nousresearch.com/docs/reference/cli-commands

### Global Flags

```
qwerty [flags] [command]        (no subcommand = interactive chat)

  --version, -V             Show version
  -z, --oneshot PROMPT      One-shot: print ONLY the final response (for scripts/pipes)
  -m MODEL  --provider P    Model/provider override for this invocation
  -t, --toolsets LIST       Comma-separated toolsets for this invocation
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --tui / --cli             Force the Ink TUI / classic REPL
  --ignore-rules            Skip AGENTS.md/SOUL.md/memory/skill injection
  --safe-mode               Disable ALL customizations (troubleshooting)
  --pass-session-id         Include session ID in system prompt
```

### Chat

```
qwerty chat [flags]
  -q, --query TEXT          Single query, non-interactive
  --image PATH              Attach a local image to a single query
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --max-turns N             Cap tool-calling iterations
  --source TAG              Session source tag (default: cli)
```
(plus the global flags above)

### Configuration

```
qwerty setup [section]      Wizard (model|tts|terminal|gateway|tools|agent)
qwerty model                Interactive model/provider picker
qwerty fallback [add|remove|list]  Fallback provider chain
qwerty config [show|edit|get|set|unset|path|env-path|check|migrate]
qwerty login / logout       OAuth sign-in / clear stored auth
qwerty doctor [--fix]       Check dependencies and config
qwerty status [--all]       Component status
```

### Tools & Skills

```
qwerty tools [list|enable NAME|disable NAME]   Per-platform toolsets (curses UI with no args)

qwerty skills list|browse|search QUERY|inspect ID
qwerty skills install ID    Hub identifier OR a direct https://…/SKILL.md URL
qwerty skills config        Enable/disable skills per platform
qwerty skills check|update|uninstall|publish PATH
qwerty skills tap add REPO  Add a GitHub repo as a skill source
qwerty bundles              Skill bundles (one /<name> alias loads several skills)
```

### MCP Servers

```
qwerty mcp add NAME (--url or --command) | remove | list | test NAME
qwerty mcp catalog | install NAME     Curated catalog install
qwerty mcp configure NAME             Toggle tool selection
qwerty mcp serve                      Run Qwerty as an MCP server
```
Details (transport, tool discovery, catalog): `references/native-mcp.md`.

### Gateway (Messaging Platforms)

```
qwerty gateway run|install|start|stop|restart|status|setup
```

20+ platforms: Telegram, Discord, Slack, WhatsApp (Baileys + Business Cloud API), iMessage (Photon — `qwerty photon setup`), Signal, Email, SMS, Matrix, Mattermost, Teams, LINE, SimpleX, ntfy, Google Chat, Home Assistant, DingTalk, Feishu, WeCom, Weixin, API Server, Webhooks. Open WebUI connects via the API Server adapter. Most adapters ship under `plugins/platforms/`.
Docs: https://qwerty-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
qwerty sessions list|browse|rename ID TITLE|delete ID|export OUT|prune|stats
```

### Cron / Webhooks

```
qwerty cron list|create SCHED|edit ID|pause|resume|run ID|remove|status
    Schedules: '30m', 'every 2h', '0 9 * * *', ISO timestamp
qwerty webhook subscribe NAME|list|remove NAME|test NAME
```
Webhook payloads/routes: `references/webhooks.md`.

### Profiles

```
qwerty profile list|create NAME (--clone|--clone-all|--clone-from)|use|show|delete
qwerty profile rename A B | alias NAME | export NAME | import FILE
```

### Credentials & Pools

```
qwerty auth                 Interactive credential manager
qwerty auth add [PROVIDER]  Add OAuth or API-key credential (nous, openai-codex, qwen-oauth, …)
qwerty auth list|remove P IDX|reset PROVIDER|status
```
Multiple credentials per provider form a pool that rotates automatically and skips exhausted keys.

### Other

```
qwerty desktop / gui        Native desktop app
qwerty dashboard            Web admin panel + embedded chat (--stop / --status)
qwerty proxy                OpenAI-compatible local proxy backed by an OAuth provider
qwerty portal               Quick setup / sign in via Nous Portal
qwerty kanban <verb>        Multi-agent work-queue board
qwerty project              Named multi-folder workspaces
qwerty skin list|use|set    Switch/tweak skins (see references/themes.md)
qwerty pets <verb>          Pet mascots (see references/petdex.md)
qwerty memory setup|status|off|reset   Memory provider
qwerty secrets bitwarden|onepassword   External secret stores
qwerty moa                  Mixture-of-Agents slots
qwerty hooks / security / backup / import / checkpoints / console
qwerty logs [-f] [errors]   View agent/error logs
qwerty send                 One-off message through a gateway platform
qwerty pairing / plugins / insights / journey / computer-use
qwerty acp                  ACP server (IDE integration)
qwerty completion bash|zsh|fish
qwerty update / uninstall / claw migrate
```

Plugin- and provider-supplied subcommands (e.g. `qwerty photon setup`) only appear once their plugin is installed/active.

### Where to Find Things

| Looking for... | Location |
|---|---|
| Config options | `qwerty config edit` · [Configuration docs](https://qwerty-agent.nousresearch.com/docs/user-guide/configuration) |
| Tools / toolsets | `qwerty tools list` · [Tools reference](https://qwerty-agent.nousresearch.com/docs/reference/tools-reference) |
| Skills catalog | `qwerty skills browse` · [Skills catalog](https://qwerty-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `qwerty model` · [Providers guide](https://qwerty-agent.nousresearch.com/docs/integrations/providers) |
| Env variables | `qwerty config env-path` · [Env vars reference](https://qwerty-agent.nousresearch.com/docs/reference/environment-variables) |
| Gateway logs | `~/.qwerty/logs/gateway.log` (or `qwerty logs`) |
| Sessions | `qwerty sessions browse` (reads state.db) |
