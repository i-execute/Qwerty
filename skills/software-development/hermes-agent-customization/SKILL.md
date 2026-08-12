---
name: hermes-agent-customization
description: "Fork, modify, and contribute to Hermes Agent — local development workflow, forking, PRs, testing, and syncing with upstream."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Hermes, Fork, Development, Contribution, GitHub, PR, Testing]
    related_skills: [github-repo-management, github-auth, github-pr-workflow, hermes-agent-skill-authoring]

---

# Hermes Agent Customization & Fork Development

Class-level skill for forking the Hermes Agent repository, making local changes (skills, plugins, core), testing, and opening pull requests. Complements the bundled `hermes-agent` skill (which covers configuration/extension) by focusing on the **fork → develop → PR** workflow.

## Prerequisites

| Tool | Install | Verify |
|------|---------|--------|
| `git` | `sudo apt install git` | `git --version` |
| `gh` (GitHub CLI) | `sudo apt install gh` or `brew install gh` | `gh --version` |
| Python 3.11+ | System / pyenv | `python3 --version` |
| `uv` (for deps) | `pip install uv` | `uv --version` |

## 1. Local Repository Location

The Hermes Agent source lives at:
```
~/.hermes/hermes-agent/
```
This is a clone of `https://github.com/NousResearch/hermes-agent.git` (origin).

```bash
cd ~/.hermes/hermes-agent
git remote -v
# origin  https://github.com/NousResearch/hermes-agent.git (fetch)
# origin  https://github.com/NousResearch/hermes-agent.git (push)
```

## 2. GitHub Authentication

**Required scopes for token:** `repo`, `workflow`, `read:org`

### Option A: gh CLI (recommended)
```bash
gh auth login --with-token <<< "$GITHUB_TOKEN"
gh auth setup-git
```

### Option B: git credential helper (no gh needed)
```bash
git config --global credential.helper store
# First push/pull will prompt for username/token — token saved to ~/.git-credentials
```

### Option C: SSH
```bash
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub Settings → SSH keys
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

## 3. Fork & Clone Workflow

```bash
# 1. Fork upstream to your account
gh repo fork NousResearch/hermes-agent --clone --remote-name origin
cd hermes-agent  # or your fork directory name

# 2. Add upstream for syncing
git remote add upstream https://github.com/NousResearch/hermes-agent.git

# 3. Verify remotes
git remote -v
# origin    https://github.com/YOUR-USER/hermes-agent.git (fetch/push)
# upstream  https://github.com/NousResearch/hermes-agent.git (fetch)
```

## 4. Branch & Develop

```bash
# Sync with upstream before starting
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feat/your-feature-name

# Make changes (see sections below)
# ...

# Run tests & linters
make lint          # ruff, mypy, etc. (check project Makefile)
pytest -x -q       # or: uv run pytest -x -q

# Commit with conventional commits
git add -A
git commit -m "feat(scope): description

- detail 1
- detail 2

Closes #123"
```

## 5. Common Change Types

| Target | Location | Example |
|--------|----------|---------|
| **Skill** | `skills/<category>/<name>/` | New skill in `skills/creative/my-skill/` |
| **Plugin** | `plugins/<name>/` | Desktop plugin in `plugins/my-plugin/` |
| **Core tool** | `agent/tools/` | New model tool in `agent/tools/my_tool.py` |
| **Config** | `config.yaml` / `cli-config.yaml.example` | New setting |
| **Docs** | `docs/` / `README.md` | Documentation updates |
| **Tests** | `tests/` | Unit/integration tests |

### Skill Authoring
Use `hermes-agent-skill-authoring` skill for skill structure, frontmatter, validation.

### Plugin Development
See `hermes-desktop-plugins` skill for desktop plugin structure (UI panes, commands).

## 6. Push & Pull Request

```bash
# Push feature branch
git push origin feat/your-feature-name

# Create PR
gh pr create --title "feat(scope): description" \
  --body "## Summary
...
## Testing
- [ ] Unit tests pass
- [ ] Manual test: ...
"
```

## 7. Sync Fork with Upstream

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## 8. Migrate a Live Hermes Checkout to a Standalone Fork

Use this when the systemd gateway is already running from a source checkout and
must remain connected while Git remotes and duplicate files are cleaned up.

### Safety invariant

**Do not restart, stop, rename, or delete the active checkout while the gateway
process references its venv.** Changing Git remotes and removing independent
copies is safe; replacing the active directory is not.

### Procedure

1. Inspect the live unit and process before touching files:
   ```bash
   systemctl --user cat hermes-gateway.service
   pid=$(systemctl --user show -p MainPID --value hermes-gateway.service)
   readlink -f /proc/$pid/cwd
   readlink -f /proc/$pid/exe
   ```
   `ExecStart`, `WorkingDirectory`, and `VIRTUAL_ENV` identify the active
   checkout. The launcher (`command -v hermes`) may point there too.

2. Measure before cleaning:
   ```bash
   du -sh ~/.hermes/hermes-agent
   du -xhd1 ~/.hermes/hermes-agent | sort -h | tail -30
   git -C ~/.hermes/hermes-agent count-objects -vH
   ```
   Large `node_modules` (Electron/UI) and duplicate Python venvs are often the
   largest consumers; Git temporary packs can also be reclaimed.

3. Keep the official project as `upstream` and point `origin` at the standalone
   fork, preserving a former fork under a clear remote name:
   ```bash
   cd ~/.hermes/hermes-agent
   git remote rename origin upstream
   git remote rename fork old-fork              # only if `fork` exists
   git remote add origin https://github.com/OWNER/FORK.git
   git config branch.beta.remote origin
   git config branch.beta.merge refs/heads/beta
   ```
   Do not force-push merely to make unrelated remote `beta` history match the
   local branch. Integrate histories deliberately.

4. Before deleting a duplicate checkout, scan process cwd/executable paths. Do
   not use a naive command-line substring check because it can match the cleanup
   command itself:
   ```bash
   python3 - /path/to/duplicate <<'PY'
   import os, sys
   root = os.path.realpath(sys.argv[1])
   hits = []
   for pid in os.listdir('/proc'):
       if not pid.isdigit():
           continue
       for field in ('cwd', 'exe'):
           try:
               target = os.path.realpath(f'/proc/{pid}/{field}')
           except OSError:
               continue
           if target == root or target.startswith(root + os.sep):
               hits.append((pid, field, target))
   if hits:
       print(*hits, sep='\n')
       raise SystemExit(2)
   PY
   rm -rf /path/to/duplicate
   ```

5. If no Git process is running, remove stale `*.lock` files left by a crashed
   Git command, then reclaim unreachable objects:
   ```bash
   git gc --prune=now
   git fsck --no-reflogs --connectivity-only
   ```

6. Verify no disruption:
   ```bash
   systemctl --user is-active hermes-gateway.service
   systemctl --user show hermes-gateway.service -p MainPID -p ActiveEnterTimestamp
   git remote get-url origin
   git branch --show-current
   ```

### Pitfalls

- A live gateway imports from the path in its systemd unit, not simply the repo
  visible in the shell. Verify the unit first.
- `node_modules` is often the dominant footprint. Do not remove it blindly:
  Hermes desktop, web UI, and build tooling can require it.
- A local branch can be ahead of or unrelated to a same-named branch in a new
  standalone remote. Treat it as a history-integration decision, not cleanup.
- `git gc` cannot run with a stale `.git/shallow.lock`. Confirm no real Git
  process exists before removing such a lock.

## 9. Custom Provider API-Key Rotation

When changing or debugging credential rotation for a custom OpenAI-compatible endpoint:

1. Resolve the named pool key with `get_custom_provider_pool_key(base_url, provider_name=name)`; do not inspect similarly named pools by URL alone.
2. Verify the live pool after loading it: primary + backups must be *unique key values*, all runtime-resolvable, and available. A row count alone can hide a duplicated primary key.
3. The primary key may appear in both `custom_providers[].api_key` and `model.api_key`. Treat that as one credential, not two rotation candidates. Otherwise the router retries the same exhausted key before moving to a backup.
4. Add a regression test that seeds the custom pool with equal config/model keys and asserts it emits only the `config:<name>` seed plus true backups. Use an in-memory pool to prove a simulated 429 selects the next key.
5. Preserve helper/API compatibility when salvaging a beta commit: if callers already import a helper such as `sync_credential_pool_entry_id`, do not delete the helper or its pool method (`entry_id_for_api_key`) without migrating every caller and adding an import smoke test. A green diff is insufficient when the gateway constructs agents dynamically.
6. Run focused tests before committing, then inspect the live gateway process/unit and logs. Source changes do not affect the already-running gateway until a verified restart.
7. Verify the push with the remote SHA. If HTTPS push lacks credentials, stop and report the exact blocker; do not claim success. Prefer `gh auth status`/`gh auth setup-git` or a configured credential helper, and use a fresh worktree under `/home/forget/QwertyWork` when repairing a beta branch.
8. The all-key `hi` probe is a conclusive quota verdict, not another ordinary request: persist a probe's 429 as `STATUS_EXHAUSTED`. Reapplying the normal 65-second custom-429 cooldown here would reintroduce a proven-dead key into routing after the cooldown.
9. Deploying code with `git reset --hard origin/beta` does not erase custom pools: they are stored in `$HERMES_HOME/auth.json`. Before telling a user whether re-entry is necessary, inspect the *active named pool* and count unique `runtime_api_key` values; `config:<provider>` and `model_config` can duplicate the primary key and must not be reported as extra rotation slots.

See `references/custom-provider-key-rotation.md for the safe inspection recipe, in-memory rotation probe, and test-runner notes. See `references/custom-provider-429-rotation.md` for the 65-second cooldown contract, full-pool `hi` probe behavior, focused tests, and broken-push recovery recipe. See `references/beta-runtime-compatibility.md` for the missing-helper regression pattern and verification checklist.

## 10. Token Discovery in Userbot Configs (Reference)

When hunting for existing GitHub tokens in userbot configurations (e.g., Heroku/Hikka modules), check:

| File | Key |
|------|-----|
| `config-<user_id>.json` | `"AetherAI" → "__config__" → "github_token"` |
| `loaded_modules/<Module>_<user_id>.py` | `loader.ConfigValue("github_token", ...)` |
| `.env` files | `GITHUB_TOKEN=` |

**Note:** Token is often empty (`""`) — create a fresh PAT if so.

## 11. Repairing a Broken/Shallow Fork Before a Force Push

If GitHub rejects a push with errors such as `did not receive expected object`,
`remote unpack failed`, or the local checkout is shallow/incomplete, do not
keep retrying the same push. The local object graph or the remote's inherited
history is inconsistent.

1. Preserve the verified worktree and commit first; record `git rev-parse HEAD`.
2. Use a **fresh clone of the target fork** under the approved work area:
   ```bash
   git clone https://github.com/OWNER/FORK.git /home/forget/QwertyWork/fork-push-repair
   git -C /home/forget/QwertyWork/fork-push-repair checkout -B beta origin/beta
   ```
3. Copy only the verified changed source/test files from the original checkout
   into the fresh clone (never copy `.git`, virtualenvs, secrets, or unrelated
   untracked files).
4. Run focused tests and `git diff --check` in the fresh clone.
5. Commit the copied changes, then force-push and verify the remote SHA:
   ```bash
   git -C /home/forget/QwertyWork/fork-push-repair push --force origin beta
   git -C /home/forget/QwertyWork/fork-push-repair fetch origin beta
   test "$(git -C /home/forget/QwertyWork/fork-push-repair rev-parse origin/beta)" = "$(git -C /home/forget/QwertyWork/fork-push-repair rev-parse HEAD)"
   ```

This preserves the requested branch state while rebuilding missing objects from
the remote. Remove the temporary repair clone and patch bundle after delivery
unless explicitly requested.

## Pitfalls

- **Don't commit secrets** — use `gh secret set` for CI, `.env` for local
- **Run tests before PR** — CI will fail otherwise
- **Keep branch focused** — one feature/fix per commit
- **Sync upstream regularly** — avoid massive merge conflicts
- **Conventional commits** — required for changelog generation

## Verification Checklist

- [ ] `git status` clean
- [ ] `make lint` passes (or project equivalent)
- [ ] `pytest` passes
- [ ] PR description explains *why* and *how tested*
- [ ] No secrets in diff (`git diff --name-only` check)

## References

- `references/token-discovery.md` — detailed token location patterns in userbot configs
- `references/fork-workflow.md` — extended fork/sync/PR recipes